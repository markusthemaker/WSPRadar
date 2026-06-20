"""Sync README.md from the English WSPRadar manual.

The Streamlit/PDF manual source lives in docs/doc_en.py as DOC_EN. README.md adds only
the repository heading above that manual body, so this script keeps both surfaces aligned.
"""

from __future__ import annotations

import ast
from pathlib import Path

README_HEADER = "# WSPRadar.org\n\nHAM RADIO STATION & ANTENNA BENCHMARKING\n\n"


def _extract_doc_en(source_path: Path) -> str:
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == "DOC_EN" for target in node.targets):
            continue
        value = ast.literal_eval(node.value)
        if not isinstance(value, str):
            raise TypeError("DOC_EN must be a string literal")
        return value
    raise RuntimeError("DOC_EN assignment not found")


def build_readme_text(doc_en: str) -> str:
    manual = doc_en.strip()
    if manual.startswith("---"):
        manual = manual[3:].lstrip()
    return README_HEADER + manual.rstrip() + "\n"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    doc_path = repo_root / "docs" / "doc_en.py"
    readme_path = repo_root / "README.md"
    readme_path.write_text(build_readme_text(_extract_doc_en(doc_path)), encoding="utf-8", newline="\n")
    print(f"Synced {readme_path.relative_to(repo_root)} from {doc_path.relative_to(repo_root)}")


if __name__ == "__main__":
    main()
