"""Dependency-free validation of versioned WSPRadar config documents.

The codec verifies the stable document discriminator and current pre-production
schema version before validating an independent copy of the document envelope.
Scientific and UI-setting semantics remain with their owning validators; this
module owns the shared persistence envelope, provenance metadata, and optional
reusable-profile metadata.
"""

from copy import deepcopy
from datetime import datetime
import re

from .config_schema import (
    CONFIG_APP_NAME,
    CONFIG_DOCUMENT_FORMAT,
    CONFIG_DOCUMENT_KEYS,
    CONFIG_KEYS,
    CONFIG_SCHEMA_VERSION,
    LOCALIZED_LANGUAGE_PATTERN,
    PROFILE_ID_MAX_LENGTH,
    PROFILE_ID_PATTERN,
)


_PROFILE_ID_RE = re.compile(PROFILE_ID_PATTERN)
_LOCALIZED_LANGUAGE_RE = re.compile(LOCALIZED_LANGUAGE_PATTERN)


def _validate_metadata(value):
    """Validate optional writer provenance in the current envelope."""
    if not isinstance(value, dict):
        raise ValueError("metadata must be a JSON object.")
    unknown_fields = sorted(set(value) - {"created_utc", "generator"})
    if unknown_fields:
        raise ValueError(
            "Unknown metadata field(s): " + ", ".join(unknown_fields) + "."
        )

    created_utc = value.get("created_utc")
    if created_utc is not None:
        if not isinstance(created_utc, str):
            raise ValueError("metadata.created_utc must be an RFC 3339 string.")
        try:
            parsed_created_utc = datetime.fromisoformat(
                created_utc.replace("Z", "+00:00")
            )
        except ValueError as exc:
            raise ValueError(
                "metadata.created_utc must be an RFC 3339 timestamp."
            ) from exc
        if parsed_created_utc.tzinfo is None:
            raise ValueError("metadata.created_utc must include a UTC offset.")

    generator = value.get("generator")
    if generator is None:
        return
    if not isinstance(generator, dict):
        raise ValueError("metadata.generator must be a JSON object.")
    missing_fields = sorted({"application", "version"} - set(generator))
    if missing_fields:
        raise ValueError(
            "Missing required metadata.generator field(s): "
            + ", ".join(missing_fields)
            + "."
        )
    unknown_fields = sorted(set(generator) - {"application", "version"})
    if unknown_fields:
        raise ValueError(
            "Unknown metadata.generator field(s): "
            + ", ".join(unknown_fields)
            + "."
        )
    if generator["application"] != CONFIG_APP_NAME:
        raise ValueError(
            f"metadata.generator.application must be {CONFIG_APP_NAME!r}."
        )
    if not isinstance(generator["version"], str) or not generator["version"]:
        raise ValueError("metadata.generator.version must be a non-empty string.")


def _validate_localized_text(value, *, field_path):
    """Validate one non-empty map from language tags to non-blank text."""
    if not isinstance(value, dict):
        raise ValueError(f"{field_path} must be a JSON object.")
    if not value:
        raise ValueError(f"{field_path} must contain at least one language.")
    for language, localized_value in value.items():
        if not isinstance(language, str) or not _LOCALIZED_LANGUAGE_RE.fullmatch(
            language
        ):
            raise ValueError(f"{field_path} contains an invalid language tag.")
        if not isinstance(localized_value, str) or not localized_value.strip():
            raise ValueError(f"{field_path}.{language} must be a non-empty string.")


def _validate_profile(value):
    """Validate optional reusable profile identity and localized presentation."""
    if not isinstance(value, dict):
        raise ValueError("profile must be a JSON object.")
    missing_fields = sorted({"id", "title"} - set(value))
    if missing_fields:
        raise ValueError(
            "Missing required profile field(s): " + ", ".join(missing_fields) + "."
        )
    unknown_fields = sorted(set(value) - {"id", "title", "description"})
    if unknown_fields:
        raise ValueError(
            "Unknown profile field(s): " + ", ".join(unknown_fields) + "."
        )

    profile_id = value["id"]
    if not isinstance(profile_id, str) or not _PROFILE_ID_RE.fullmatch(profile_id):
        raise ValueError(
            "profile.id must be a lowercase stable token of at most "
            f"{PROFILE_ID_MAX_LENGTH} characters."
        )
    _validate_localized_text(value["title"], field_path="profile.title")
    if "description" in value:
        _validate_localized_text(
            value["description"],
            field_path="profile.description",
        )


def _validate_current_envelope(payload):
    """Validate the non-scientific structure of one current config document."""
    unknown_document_keys = sorted(set(payload) - CONFIG_DOCUMENT_KEYS)
    if unknown_document_keys:
        raise ValueError(
            "Unknown config document field(s): "
            + ", ".join(unknown_document_keys)
            + ". Put non-core data under extensions."
        )
    if payload.get("format") != CONFIG_DOCUMENT_FORMAT:
        raise ValueError(f"format must be {CONFIG_DOCUMENT_FORMAT!r}.")
    if payload.get("schema_version") != CONFIG_SCHEMA_VERSION:
        raise ValueError(f"schema_version must be {CONFIG_SCHEMA_VERSION}.")

    _validate_metadata(payload.get("metadata", {}))
    if "profile" in payload:
        _validate_profile(payload["profile"])
    if not isinstance(payload.get("extensions", {}), dict):
        raise ValueError("extensions must be a JSON object.")

    settings = payload.get("settings")
    if not isinstance(settings, dict):
        raise ValueError("settings must be a JSON object.")
    missing_settings_groups = sorted(CONFIG_KEYS - set(settings))
    if missing_settings_groups:
        raise ValueError(
            "settings is missing required group(s): "
            + ", ".join(missing_settings_groups)
            + "."
        )
    unknown_settings_groups = sorted(set(settings) - CONFIG_KEYS)
    if unknown_settings_groups:
        raise ValueError(
            "settings has unknown group(s): "
            + ", ".join(unknown_settings_groups)
            + "."
        )
    for settings_group in CONFIG_KEYS:
        if not isinstance(settings[settings_group], dict):
            raise ValueError(f"settings.{settings_group} must be a JSON object.")


def prepare_config_document(payload):
    """Return an independent, validated current-schema config document.

    The input must be a decoded JSON object. The pre-production version-1
    contract has no supported predecessor or migration path, so every
    unsupported schema version is rejected rather than guessed. The returned
    dictionary never aliases the caller's nested objects.
    """
    if not isinstance(payload, dict):
        raise ValueError("The config file must contain a JSON object.")
    if payload.get("format") != CONFIG_DOCUMENT_FORMAT:
        raise ValueError(f"format must be {CONFIG_DOCUMENT_FORMAT!r}.")

    schema_version = payload.get("schema_version")
    if isinstance(schema_version, bool) or not isinstance(schema_version, int):
        raise ValueError("schema_version must be an integer.")
    if schema_version < 1:
        raise ValueError("schema_version must be at least 1.")
    if schema_version > CONFIG_SCHEMA_VERSION:
        raise ValueError(
            f"Config schema version {schema_version} is newer than the supported "
            f"version {CONFIG_SCHEMA_VERSION}."
        )
    if schema_version < CONFIG_SCHEMA_VERSION:
        raise ValueError(
            f"Config schema version {schema_version} is older than the supported "
            f"version {CONFIG_SCHEMA_VERSION}."
        )

    prepared_payload = deepcopy(payload)
    _validate_current_envelope(prepared_payload)
    return prepared_payload
