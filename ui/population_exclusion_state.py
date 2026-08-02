"""Transient mode-aware defaults for the shared station-population filters."""

from collections.abc import Mapping, MutableMapping


PERFORMANCE_RESULT_TYPE = "performance"
COMPARE_RESULT_TYPE = "compare"
POPULATION_EXCLUSION_RESULT_TYPE_KEY = "_population_exclusion_result_type"
POPULATION_EXCLUSION_OVERRIDES_KEY = "_population_exclusion_overrides"

_RESULT_TYPES = frozenset({PERFORMANCE_RESULT_TYPE, COMPARE_RESULT_TYPE})
_COMPARISON_MODES = frozenset(
    {"hardware_ab", "reference_station", "local_neighborhood"}
)
_STATE_KEYS = (
    "val_exclude_special_callsigns",
    "val_filter_moving",
)
_WIDGET_KEYS_BY_STATE_KEY = {
    state_key: f"_{state_key}" for state_key in _STATE_KEYS
}
_DEFAULTS_BY_RESULT_TYPE = {
    PERFORMANCE_RESULT_TYPE: {
        "val_exclude_special_callsigns": True,
        "val_filter_moving": True,
    },
    COMPARE_RESULT_TYPE: {
        "val_exclude_special_callsigns": False,
        "val_filter_moving": False,
    },
}


def result_type_from_comparison_mode(comparison_mode: object) -> str:
    """Map the canonical benchmark mode to its visible result family."""
    if comparison_mode == "none":
        return PERFORMANCE_RESULT_TYPE
    if comparison_mode in _COMPARISON_MODES:
        return COMPARE_RESULT_TYPE
    raise ValueError(f"Unsupported comparison mode {comparison_mode!r}.")


def population_exclusion_defaults(result_type: str) -> dict[str, bool]:
    """Return a new canonical filter-default mapping for one result type."""
    try:
        return dict(_DEFAULTS_BY_RESULT_TYPE[result_type])
    except KeyError as error:
        raise ValueError(f"Unsupported result type {result_type!r}.") from error


def _override_flags(state: Mapping) -> dict[str, bool] | None:
    """Return valid per-field override flags, or ``None`` for legacy state."""
    overrides = state.get(POPULATION_EXCLUSION_OVERRIDES_KEY)
    if not isinstance(overrides, Mapping):
        return None
    if any(
        not isinstance(overrides.get(state_key), bool)
        for state_key in _STATE_KEYS
    ):
        return None
    return {state_key: overrides[state_key] for state_key in _STATE_KEYS}


def initialize_population_exclusion_state(state: MutableMapping) -> None:
    """Initialize new sessions while preserving canonical existing values."""
    # Reassignment detaches values from the former direct widget keys so a
    # hot-reloaded Streamlit session cannot delete the new canonical shadows.
    tracked_result_type = state.get(POPULATION_EXCLUSION_RESULT_TYPE_KEY)
    overrides = _override_flags(state)
    if tracked_result_type in _RESULT_TYPES and overrides is not None:
        defaults = population_exclusion_defaults(tracked_result_type)
        for state_key in _STATE_KEYS:
            canonical_value = state.get(state_key)
            state[state_key] = (
                canonical_value
                if isinstance(canonical_value, bool)
                else defaults[state_key]
            )
        return

    active_result_type = result_type_from_comparison_mode(
        state.get("val_comp_mode")
    )
    defaults = population_exclusion_defaults(active_result_type)
    migrated_overrides = {}
    for state_key in _STATE_KEYS:
        has_existing_value = isinstance(state.get(state_key), bool)
        state[state_key] = (
            state[state_key]
            if has_existing_value
            else defaults[state_key]
        )
        migrated_overrides[state_key] = has_existing_value
    state[POPULATION_EXCLUSION_RESULT_TYPE_KEY] = active_result_type
    state[POPULATION_EXCLUSION_OVERRIDES_KEY] = migrated_overrides


def transition_population_exclusion_result_type(
    state: MutableMapping,
    result_type: str,
) -> None:
    """Apply another result family's defaults only to untouched filter fields."""
    if result_type not in _RESULT_TYPES:
        raise ValueError(f"Unsupported result type {result_type!r}.")

    initialize_population_exclusion_state(state)
    overrides = _override_flags(state)
    assert overrides is not None
    defaults = population_exclusion_defaults(result_type)
    for state_key in _STATE_KEYS:
        if not overrides[state_key]:
            state[state_key] = defaults[state_key]
    state[POPULATION_EXCLUSION_RESULT_TYPE_KEY] = result_type


def mark_population_exclusion_override(
    state: MutableMapping,
    state_key: str,
) -> None:
    """Mark one user-edited population exclusion as an explicit session choice."""
    if state_key not in _STATE_KEYS:
        raise ValueError(
            f"Unsupported population exclusion field {state_key!r}."
        )
    initialize_population_exclusion_state(state)
    overrides = _override_flags(state)
    assert overrides is not None
    overrides[state_key] = True
    state[POPULATION_EXCLUSION_OVERRIDES_KEY] = overrides


def population_exclusion_widget_key(state_key: str) -> str:
    """Return the temporary Streamlit widget key for one canonical field."""
    try:
        return _WIDGET_KEYS_BY_STATE_KEY[state_key]
    except KeyError as error:
        raise ValueError(
            f"Unsupported population exclusion field {state_key!r}."
        ) from error


def load_population_exclusion_widget_values(state: MutableMapping) -> None:
    """Copy durable canonical values into temporary keys before rendering."""
    initialize_population_exclusion_state(state)
    for state_key, widget_key in _WIDGET_KEYS_BY_STATE_KEY.items():
        state[widget_key] = state[state_key]


def store_population_exclusion_widget_value(
    state: MutableMapping,
    state_key: str,
) -> None:
    """Persist one temporary widget value as an explicit canonical choice."""
    widget_key = population_exclusion_widget_key(state_key)
    widget_value = state.get(widget_key)
    if not isinstance(widget_value, bool):
        raise ValueError("Population exclusion widget values must be booleans.")
    state[state_key] = widget_value
    mark_population_exclusion_override(state, state_key)


def apply_population_exclusion_defaults(
    state: MutableMapping,
    result_type: str,
) -> None:
    """Apply both defaults and clear explicit ownership for a fresh preset."""
    defaults = population_exclusion_defaults(result_type)
    state.update(defaults)
    state[POPULATION_EXCLUSION_RESULT_TYPE_KEY] = result_type
    state[POPULATION_EXCLUSION_OVERRIDES_KEY] = {
        state_key: False for state_key in _STATE_KEYS
    }


def register_explicit_population_exclusion_values(
    state: MutableMapping,
    *,
    result_type: str | None = None,
) -> None:
    """Register loaded config values without replacing them with UI defaults."""
    active_result_type = result_type or result_type_from_comparison_mode(
        state.get("val_comp_mode")
    )
    population_exclusion_defaults(active_result_type)
    if any(
        not isinstance(state.get(state_key), bool)
        for state_key in _STATE_KEYS
    ):
        raise ValueError("Loaded population exclusions must both be booleans.")
    state[POPULATION_EXCLUSION_RESULT_TYPE_KEY] = active_result_type
    state[POPULATION_EXCLUSION_OVERRIDES_KEY] = {
        state_key: True for state_key in _STATE_KEYS
    }


def reset_population_exclusion_state(state: MutableMapping) -> None:
    """Restore untouched Performance defaults for a factory-reset session."""
    apply_population_exclusion_defaults(state, PERFORMANCE_RESULT_TYPE)
