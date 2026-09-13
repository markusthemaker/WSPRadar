"""Canonical Inspector selection records and dependency-light boundary codecs.

Persisted scope uses ``"all"`` or a nonempty list. The immutable scope fields
use ``None`` for All; they never overload an empty tuple with that meaning.
Station intent has a separate contract: ``None`` keeps automatic selection,
while an empty tuple records deliberate deselection. No record owns evidence.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import InitVar, dataclass

from config.config_schema import (
    SEGMENT_DIRECTION_OPTIONS,
    SEGMENT_EVIDENCE_TIME_BINS,
    SEGMENT_RANGE_OPTIONS,
    SEGMENT_SELECTION_ALL,
    STATION_EVIDENCE_TIME_BINS,
)
from core.input_validation import (
    is_valid_callsign,
    is_valid_locator,
    normalize_ascii_upper,
)


def _normalize_identity_text(value, *, field: str, is_locator: bool) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string.")
    validator = is_valid_locator if is_locator else is_valid_callsign
    if not validator(value):
        description = "4- or 6-character Maidenhead locator" if is_locator else "callsign"
        raise ValueError(f"{field} is not a valid {description}.")
    return normalize_ascii_upper(value)


@dataclass(frozen=True, slots=True)
class StationIdentity:
    """One exact normalized callsign and full four- or six-character locator."""

    callsign: str
    locator: str
    identity_field: InitVar[str] = ""

    def __post_init__(self, identity_field: str) -> None:
        field_prefix = f"{identity_field}." if identity_field else ""
        object.__setattr__(self, "callsign", _normalize_identity_text(
            self.callsign, field=f"{field_prefix}callsign", is_locator=False,
        ))
        object.__setattr__(self, "locator", _normalize_identity_text(
            self.locator, field=f"{field_prefix}locator", is_locator=True,
        ))

    @property
    def pair(self) -> tuple[str, str]:
        return self.callsign, self.locator

    def to_dict(self) -> dict[str, str]:
        return {"callsign": self.callsign, "locator": self.locator}


def parse_station_identities(
    records,
    *,
    field: str = "Selected-station state",
    maximum_count: int | None = 1,
) -> tuple[StationIdentity, ...] | None:
    """Validate automatic, empty or ordered unique station-selection intent."""
    if records is None:
        return None
    if not isinstance(records, list):
        raise ValueError(f"{field} must be null or a JSON array.")
    identities = []
    seen_identities = set()
    for station_index, record in enumerate(records):
        station_field = f"{field}[{station_index}]"
        if not isinstance(record, Mapping):
            raise ValueError(f"{station_field} must be a JSON object.")
        required_fields = {"callsign", "locator"}
        missing_fields = sorted(required_fields.difference(record))
        if missing_fields:
            raise ValueError(f"Missing required {station_field} field(s): " + ", ".join(missing_fields) + ".")
        unknown_fields = sorted(set(record).difference(required_fields))
        if unknown_fields:
            raise ValueError(f"Unknown {station_field} field(s): " + ", ".join(unknown_fields) + ".")
        identity = StationIdentity(
            record["callsign"], record["locator"], identity_field=station_field,
        )
        if identity in seen_identities:
            raise ValueError(f"{field} contains duplicate station identity {identity.callsign}/{identity.locator}.")
        seen_identities.add(identity)
        identities.append(identity)
    if maximum_count is not None:
        if isinstance(maximum_count, bool) or not isinstance(maximum_count, int) or maximum_count < 0:
            raise ValueError("Maximum station count must be a nonnegative integer or None.")
        if len(identities) > maximum_count:
            if maximum_count == 1:
                raise ValueError(f"{field} must contain at most one station identity.")
            raise ValueError(f"{field} must contain at most {maximum_count} station identities.")
    return tuple(identities)


def station_identity_records(
    identities: tuple[StationIdentity, ...] | None,
) -> list[dict[str, str]] | None:
    """Create independent persisted records without changing selection intent."""
    return None if identities is None else [identity.to_dict() for identity in identities]


def parse_segment_selection(
    value,
    *,
    field: str,
    choices: Sequence[str],
) -> tuple[str, ...] | None:
    """Validate explicit All or a nonempty scope while preserving its order."""
    if value == SEGMENT_SELECTION_ALL:
        return None
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field} must be {SEGMENT_SELECTION_ALL!r} or a non-empty JSON array.")
    selected_values = []
    seen_values = set()
    for selection_index, selected_value in enumerate(value):
        if not isinstance(selected_value, str) or selected_value not in choices:
            raise ValueError(f"{field}[{selection_index}] must be one of: {', '.join(choices)}.")
        if selected_value in seen_values:
            raise ValueError(f"{field} contains duplicate value {selected_value!r}.")
        seen_values.add(selected_value)
        selected_values.append(selected_value)
    return tuple(selected_values)


def segment_selection_value(selection: tuple[str, ...] | None) -> str | list[str]:
    """Return the unchanged config representation of a validated scope."""
    return SEGMENT_SELECTION_ALL if selection is None else list(selection)


def validate_evidence_time_bin(
    value,
    *,
    field: str,
    is_segment: bool = False,
    allow_uninitialized: bool = False,
) -> str | None:
    """Validate canonical and retained legacy bins without choosing a default."""
    if value is None and allow_uninitialized:
        return None
    choices = SEGMENT_EVIDENCE_TIME_BINS if is_segment else STATION_EVIDENCE_TIME_BINS
    if not isinstance(value, str) or value not in choices:
        raise ValueError(f"{field} must be one of: {', '.join(choices)}.")
    return value


@dataclass(frozen=True, slots=True, kw_only=True)
class InspectorSelection:
    """One run-scoped, validated selection snapshot for the state owner.

    Range and direction intent remains distinct from a renderer's resolved
    available rows. Candidate provenance and zoom intervals have their own
    existing records and are deliberately not folded into station intent.
    """

    run_id: int
    analysis_id: str
    scope_token: str
    is_compare: bool
    is_outlier_reporting_enabled: bool = False
    selected_ranges: tuple[str, ...] | None = None
    selected_directions: tuple[str, ...] | None = None
    selected_stations: tuple[StationIdentity, ...] | None = None
    segment_time_bin: str = "auto"
    station_time_bin: str | None = None

    def __post_init__(self) -> None:
        if type(self.run_id) is not int or self.run_id < 0:
            raise ValueError("Inspector selection run_id must be a nonnegative integer.")
        for field_name in ("analysis_id", "scope_token"):
            text_value = getattr(self, field_name)
            if not isinstance(text_value, str) or not text_value.strip():
                raise ValueError(f"Inspector selection {field_name} must be nonempty text.")
        for field_name in ("is_compare", "is_outlier_reporting_enabled"):
            if type(getattr(self, field_name)) is not bool:
                raise ValueError(f"Inspector selection {field_name} must be a boolean.")
        if self.is_outlier_reporting_enabled and not self.is_compare:
            raise ValueError("Outlier reporting requires a Benchmark selection.")
        for field_name, choices in (
            ("selected_ranges", SEGMENT_RANGE_OPTIONS),
            ("selected_directions", SEGMENT_DIRECTION_OPTIONS),
        ):
            selection = getattr(self, field_name)
            if selection is not None:
                if not isinstance(selection, tuple):
                    raise TypeError(f"Inspector selection {field_name} must be an immutable tuple or None.")
                parse_segment_selection(list(selection), field=field_name, choices=choices)
        if self.selected_stations is not None:
            if not isinstance(self.selected_stations, tuple) or not all(
                isinstance(identity, StationIdentity) for identity in self.selected_stations
            ):
                raise TypeError("Inspector selected_stations must contain immutable station identities.")
            if len(set(self.selected_stations)) != len(self.selected_stations):
                raise ValueError("Inspector selected_stations contains duplicate station identities.")
            if not self.is_outlier_reporting_enabled and len(self.selected_stations) > 1:
                raise ValueError("Inspector selected_stations must contain at most one station identity.")
        validate_evidence_time_bin(self.segment_time_bin, field="segment_time_bin", is_segment=True)
        validate_evidence_time_bin(self.station_time_bin, field="station_time_bin", allow_uninitialized=True)
