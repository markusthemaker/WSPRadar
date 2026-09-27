"""Package current WSPRadar source for an isolated Codespaces load-test run.

Reads the working-tree contents of tracked files plus an explicit manual-harness
allowlist. Git metadata, local environments, caches, reports and secrets are
excluded. No commit, branch, staging area or tracked source file is changed.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import uuid
import zipfile


REPOSITORY_ROOT = next(
    directory for directory in Path(__file__).resolve().parents
    if (directory / "app.py").is_file() and (directory / "AGENT_README.md").is_file()
)
HARNESS_PATH = "tests/manual/multi_user_load_test"
HARNESS_FILES = frozenset({
    "README.md", "requirements.txt", "app_entry.py", "metrics.py", "replay.py",
    "run.py", "make_bundle.py", "test_lifecycle.py", "test_metrics.py",
    "test_replay.py", "test_bundle.py", "test_summary.py", "test_startup.py",
    "test_interactions.py", "ui_trace.py", "test_ui_trace.py",
})
SOURCE_SUFFIXES = frozenset({".py", ".toml", ".config", ".json", ".txt"})
EXCLUDED_DIRECTORIES = frozenset({
    ".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", ".wspr_cache", ".test",
})
EXCLUDED_ROOT_DIRECTORIES = frozenset({"output", "reports", "results"})
SECRET_SUFFIXES = frozenset({".pem", ".key", ".p12", ".pfx"})


def _git(repository: Path, *arguments: str) -> bytes:
    command = subprocess.run(
        ["git", *arguments], cwd=repository, capture_output=True, timeout=30,
    )
    if command.returncode:
        raise RuntimeError(command.stderr.decode("utf-8", errors="replace").strip())
    return command.stdout


def is_excluded(relative_name: str) -> bool:
    path = PurePosixPath(relative_name)
    lowered_parts = tuple(part.lower() for part in path.parts)
    filename = path.name.lower()
    return (
        any(part in EXCLUDED_DIRECTORIES for part in lowered_parts)
        or bool(lowered_parts and lowered_parts[0] in EXCLUDED_ROOT_DIRECTORIES)
        or filename == "source_snapshot.json"
        or filename == "secrets.toml"
        or filename == ".env"
        or filename.startswith(".env.")
        or filename.startswith("credentials.")
        or path.suffix.lower() in SECRET_SUFFIXES
    )


def validated_source_path(repository: Path, relative_name: str) -> Path:
    """Reject traversal, links/junctions and paths escaping the source root."""
    portable = PurePosixPath(relative_name.replace("\\", "/"))
    if (
        portable.is_absolute() or not portable.parts
        or any(part in {".", ".."} or ":" in part for part in portable.parts)
    ):
        raise ValueError(f"Unsafe source path: {relative_name!r}")
    current = repository
    for part in portable.parts:
        current = current / part
        information = current.lstat()
        if stat.S_ISLNK(information.st_mode) or getattr(information, "st_file_attributes", 0) & 0x400:
            raise ValueError(f"Links and reparse points are not allowed in the bundle: {relative_name}")
    try:
        current.resolve().relative_to(repository.resolve())
    except ValueError as error:
        raise ValueError(f"Source escaped the repository: {relative_name}") from error
    if not current.is_file():
        raise ValueError(f"Bundle source is not a regular file: {relative_name}")
    return current


def collect_bundle_paths(repository: Path, tracked_names: list[str]) -> tuple[list[str], list[str]]:
    """Select current files; deleted tracked files remain absent in the bundle."""
    names = {name.replace("\\", "/") for name in tracked_names if name}
    harness_directory = repository / HARNESS_PATH
    if harness_directory.is_dir():
        for path in harness_directory.iterdir():
            if path.name == "__pycache__":
                continue
            if path.name not in HARNESS_FILES:
                raise ValueError(f"Manual harness entry is not approved for packaging: {path.name}")
            names.add(f"{HARNESS_PATH}/{path.name}")
    included, excluded = [], []
    for name in sorted(names):
        if is_excluded(name):
            excluded.append(name)
            continue
        # Lexical validation must happen even for a missing tracked path.
        portable = PurePosixPath(name)
        if portable.is_absolute() or ".." in portable.parts or any(":" in part for part in portable.parts):
            raise ValueError(f"Unsafe tracked source path: {name!r}")
        try:
            validated_source_path(repository, name)
        except FileNotFoundError:
            excluded.append(name)
            continue
        included.append(name)
    return included, excluded


def source_digest(file_records: list[dict]) -> str:
    """Match the runner's portable sorted path:sha256 newline fingerprint."""
    digest = hashlib.sha256()
    portable_records = sorted(
        (record["path"].replace("\\", "/"), record["sha256"])
        for record in file_records
    )
    for path, file_hash in portable_records:
        if path != "source_snapshot.json" and PurePosixPath(path).suffix in SOURCE_SUFFIXES:
            digest.update(f"{path}:{file_hash}\n".encode("utf-8"))
    return digest.hexdigest()


def inspect_checkout(repository: Path) -> dict:
    repository = repository.resolve()
    git_root = Path(_git(repository, "rev-parse", "--show-toplevel").decode("utf-8").strip()).resolve()
    if git_root != repository:
        raise ValueError("The bundle root must be the exact Git checkout root.")
    tracked_names = _git(repository, "ls-files", "-z").decode("utf-8").split("\0")
    included, excluded = collect_bundle_paths(repository, tracked_names)
    return {
        "git_revision": _git(repository, "rev-parse", "HEAD").decode("utf-8").strip(),
        "dirty": bool(_git(repository, "status", "--porcelain", "--untracked-files=normal").strip()),
        "files": included, "excluded_files": excluded,
        "total_source_bytes": sum(validated_source_path(repository, name).stat().st_size for name in included),
    }


def build_bundle(repository: Path, destination: Path, *, overwrite: bool = False) -> dict:
    repository = repository.resolve()
    destination = destination if destination.is_absolute() else repository / destination
    # Keep generated output inside the ignored local workspace, never over source.
    destination = destination.absolute()
    expected_output_root = repository / ".test"
    try:
        destination.resolve().relative_to(expected_output_root)
    except ValueError as error:
        raise ValueError("Write the transfer ZIP inside this checkout's .test directory.") from error
    if destination.suffix.lower() != ".zip":
        raise ValueError("The transfer destination must have a .zip extension.")
    if destination.is_symlink():
        raise ValueError("The transfer destination cannot be a symbolic link.")
    if destination.exists() and not overwrite:
        raise FileExistsError(f"Refusing to replace an existing bundle without --overwrite: {destination}")
    inventory = inspect_checkout(repository)
    print(json.dumps({
        "phase": "inventory", "files": len(inventory["files"]),
        "total_source_bytes": inventory["total_source_bytes"],
        "excluded_files": inventory["excluded_files"],
    }), flush=True)
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Validate the output ancestors separately; a junction into a different
    # workspace is not an acceptable .test destination.
    current = destination.parent
    while current != repository:
        information = current.lstat()
        if stat.S_ISLNK(information.st_mode) or getattr(information, "st_file_attributes", 0) & 0x400:
            raise ValueError("The output directory cannot contain links or reparse points.")
        current = current.parent
    temporary_path = destination.with_name(f".{destination.name}.{uuid.uuid4().hex}.tmp")
    records = []
    try:
        with zipfile.ZipFile(temporary_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            for name in inventory["files"]:
                source_path = validated_source_path(repository, name)
                before = source_path.stat()
                file_hash = hashlib.sha256()
                # Hash the exact streamed bytes written to the ZIP, not a
                # separate read that could observe another edit revision.
                with source_path.open("rb") as source, archive.open(name, "w") as target:
                    for chunk in iter(lambda: source.read(1024 * 1024), b""):
                        file_hash.update(chunk)
                        target.write(chunk)
                after = validated_source_path(repository, name).stat()
                if (before.st_size, before.st_mtime_ns, before.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
                    raise RuntimeError(f"Source changed during packaging; retry after edits finish: {name}")
                records.append({"path": name, "sha256": file_hash.hexdigest()})
            snapshot = {
                "schema_version": 1,
                "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "git_revision": inventory["git_revision"],
                "dirty": inventory["dirty"],
                "source_digest": source_digest(records),
                "source_digest_algorithm": "sha256 of sorted eligible UTF-8 path:sha256 followed by newline; .py .toml .config .json .txt; excludes source_snapshot.json",
                "files": records,
            }
            archive.writestr("source_snapshot.json", json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n")
        # A second check catches edits to a file already streamed while another
        # file was being copied. The bundle then describes one stable checkout.
        for record in records:
            source_path = validated_source_path(repository, record["path"])
            current_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
            if current_hash != record["sha256"]:
                raise RuntimeError(f"Source changed before bundle publication: {record['path']}")
        os.replace(temporary_path, destination)
        return {"path": str(destination), "bytes": destination.stat().st_size, "source_digest": snapshot["source_digest"], "files": len(records)}
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(".test/multiuser-load-transfer.zip"))
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--inspect", action="store_true", help="Report selected size/paths without writing a ZIP.")
    arguments = parser.parse_args()
    if arguments.inspect:
        print(json.dumps(inspect_checkout(REPOSITORY_ROOT), indent=2))
    else:
        print(json.dumps(build_bundle(REPOSITORY_ROOT, arguments.output, overwrite=arguments.overwrite), indent=2))


if __name__ == "__main__":
    main()
