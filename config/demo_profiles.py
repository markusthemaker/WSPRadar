"""Discover ordinary versioned configs that are installed as guided demos."""

from pathlib import Path

from .config_codec import prepare_config_document
from .json_utils import decode_strict_json_bytes


DEMO_PROFILES_DIR = Path(__file__).with_name("demos")
DEMO_PROFILE_MAX_BYTES = 200_000


def resolve_demo_profile_text(profile, field, language, fallback=""):
    """Return requested demo text, falling back explicitly to English.

    Installed demos require English profile text, while German translations are
    optional. This resolver keeps that convention at the presentation boundary
    and returns ``fallback`` only for malformed compatibility input.
    """
    localized_values = profile.get(field, {}) if isinstance(profile, dict) else {}
    if not isinstance(localized_values, dict):
        return fallback

    requested_language = str(language or "").strip()
    for language_key in dict.fromkeys((requested_language, "en")):
        localized_value = localized_values.get(language_key)
        if isinstance(localized_value, str) and localized_value.strip():
            return localized_value.strip()
    return fallback


def prepare_demo_description_markdown(description):
    """Preserve config line feeds as Markdown hard breaks without changing links."""
    normalized_description = str(description or "").replace("\r\n", "\n").replace(
        "\r",
        "\n",
    )
    return "  \n".join(normalized_description.split("\n"))


def _validate_demo_english_fallback(profile, profile_path):
    """Require the English baseline used when an optional translation is absent."""
    for field in ("title", "description"):
        if field == "description" and field not in profile:
            continue
        localized_values = profile[field]
        english_text = localized_values.get("en")
        if not isinstance(english_text, str) or not english_text.strip():
            raise ValueError(
                f"Demo config {profile_path.name} must contain "
                f"profile.{field}.en; German text is optional."
            )


def _read_demo_document(profile_path):
    """Read, strictly decode, and validate one installed demo config."""
    try:
        raw_bytes = profile_path.read_bytes()
    except OSError as exc:
        raise RuntimeError(f"Unable to read demo config: {profile_path}") from exc
    if not raw_bytes:
        raise ValueError(f"The demo config is empty: {profile_path.name}.")
    if len(raw_bytes) > DEMO_PROFILE_MAX_BYTES:
        raise ValueError(f"The demo config is too large: {profile_path.name}.")

    payload = decode_strict_json_bytes(
        raw_bytes,
        document_name=f"demo config {profile_path.name}",
    )
    return prepare_config_document(payload)


def load_demo_profiles(path=DEMO_PROFILES_DIR):
    """Load filename-ordered configs into the legacy demo-profile mapping.

    Every regular ``*.config`` file is accepted and ordered lexicographically by
    its complete filename. Filenames are opaque ordering keys and are independent
    of the required ``profile.id`` stored in each document. The compatibility
    mapping retains the ``id``, ``label``, ``description``, and ``configuration``
    fields expected by existing UI consumers while rejecting duplicate profile
    IDs that would collide in that mapping.
    """
    profiles_directory = Path(path)
    if not profiles_directory.is_dir():
        raise RuntimeError(
            f"Unable to read demo configuration directory: {profiles_directory}"
        )
    try:
        profile_paths = sorted(
            [
                profile_path
                for profile_path in profiles_directory.glob("*.config")
                if profile_path.is_file()
            ],
            key=lambda profile_path: profile_path.name,
        )
    except OSError as exc:
        raise RuntimeError(
            f"Unable to read demo configuration directory: {profiles_directory}"
        ) from exc
    if not profile_paths:
        raise ValueError("The demo configuration directory contains no config files.")

    demo_profiles = []
    seen_profile_ids = set()
    for profile_path in profile_paths:
        configuration = _read_demo_document(profile_path)
        profile = configuration.get("profile")
        if profile is None:
            raise ValueError(
                f"Demo config {profile_path.name} must contain profile metadata."
            )
        _validate_demo_english_fallback(profile, profile_path)
        profile_id = profile["id"]
        if profile_id in seen_profile_ids:
            raise ValueError(f"Duplicate demo profile id: {profile_id}.")

        seen_profile_ids.add(profile_id)
        demo_profiles.append(
            (
                profile_id,
                {
                    "id": profile_id,
                    "label": dict(profile["title"]),
                    "description": dict(profile.get("description", {})),
                    "configuration": configuration,
                },
            )
        )

    return dict(demo_profiles)


DEMO_PROFILES = load_demo_profiles()
