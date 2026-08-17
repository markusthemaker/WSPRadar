"""Dependency-light scientific policy for optional Delta-SNR episodes."""

from __future__ import annotations

from dataclasses import dataclass
import math
from numbers import Real


DEFAULT_MINIMUM_DEPARTURE_DB = 6.0
DEFAULT_MINIMUM_ROBUST_Z = 3.0
DEFAULT_MAXIMUM_BASELINE_DIFFERENCE_DB = 3.0
LEGACY_BURST_MINIMUM_DEPARTURE_DB = 3.0
LEGACY_BURST_MINIMUM_ROBUST_Z = 3.5
DELTA_SNR_OUTLIER_MINIMUM_THRESHOLD = 0.1
DELTA_SNR_OUTLIER_MAXIMUM_THRESHOLD = 100.0

DELTA_SNR_OUTLIER_CONFIG_FIELD_TO_POLICY_FIELD = (
    (
        "delta_snr_outlier_minimum_departure_db",
        "minimum_departure_db",
    ),
    (
        "delta_snr_outlier_minimum_robust_z",
        "minimum_robust_z",
    ),
    (
        "delta_snr_outlier_maximum_baseline_difference_db",
        "maximum_baseline_difference_db",
    ),
)

# Unpublished duration-specific configuration fields remain recognizable only
# so an experimental version-1 document can be converted deterministically.
LEGACY_DELTA_SNR_OUTLIER_CONFIG_FIELDS = (
    "delta_snr_outlier_spot_minimum_departure_db",
    "delta_snr_outlier_burst_minimum_departure_db",
    "delta_snr_outlier_sustained_minimum_departure_db",
    "delta_snr_outlier_spot_minimum_robust_z",
    "delta_snr_outlier_burst_minimum_robust_z",
    "delta_snr_outlier_sustained_minimum_robust_z",
)


@dataclass(frozen=True)
class DeltaSnrOutlierDetectionPolicy:
    """Define the three validated gates shared by every grouped candidate."""

    minimum_departure_db: float = DEFAULT_MINIMUM_DEPARTURE_DB
    minimum_robust_z: float = DEFAULT_MINIMUM_ROBUST_Z
    maximum_baseline_difference_db: float = (
        DEFAULT_MAXIMUM_BASELINE_DIFFERENCE_DB
    )

    def __post_init__(self) -> None:
        """Normalize every configured gate to one bounded finite float."""
        policy_fields = tuple(
            policy_field
            for _config_field, policy_field in (
                DELTA_SNR_OUTLIER_CONFIG_FIELD_TO_POLICY_FIELD
            )
        )
        for field_name in policy_fields:
            raw_value = getattr(self, field_name)
            if isinstance(raw_value, bool) or not isinstance(raw_value, Real):
                raise ValueError(
                    f"{field_name} must be between "
                    f"{DELTA_SNR_OUTLIER_MINIMUM_THRESHOLD} and "
                    f"{DELTA_SNR_OUTLIER_MAXIMUM_THRESHOLD} inclusive."
                )
            numeric_value = float(raw_value)
            if (
                not math.isfinite(numeric_value)
                or numeric_value < DELTA_SNR_OUTLIER_MINIMUM_THRESHOLD
                or numeric_value > DELTA_SNR_OUTLIER_MAXIMUM_THRESHOLD
            ):
                raise ValueError(
                    f"{field_name} must be between "
                    f"{DELTA_SNR_OUTLIER_MINIMUM_THRESHOLD} and "
                    f"{DELTA_SNR_OUTLIER_MAXIMUM_THRESHOLD} inclusive."
                )
            object.__setattr__(self, field_name, numeric_value)

    @property
    def signature_tuple(self) -> tuple[float, ...]:
        """Return stable ordered scientific values for cache/signature identity."""
        return tuple(
            getattr(self, policy_field)
            for _config_field, policy_field in (
                DELTA_SNR_OUTLIER_CONFIG_FIELD_TO_POLICY_FIELD
            )
        )

    def as_dict(self) -> dict[str, float]:
        """Return a stable JSON-friendly mapping keyed by policy field name."""
        return {
            policy_field: getattr(self, policy_field)
            for _config_field, policy_field in (
                DELTA_SNR_OUTLIER_CONFIG_FIELD_TO_POLICY_FIELD
            )
        }


DEFAULT_DELTA_SNR_OUTLIER_DETECTION_POLICY = DeltaSnrOutlierDetectionPolicy()

# Version-1 saved configurations and public URLs originally omitted detector
# values equal to this policy. Keep that omission meaning stable even when the
# factory defaults for new analyses change.
VERSION_1_OMITTED_DELTA_SNR_OUTLIER_DETECTION_POLICY = (
    DeltaSnrOutlierDetectionPolicy(
        minimum_departure_db=3.0,
        minimum_robust_z=4.0,
        maximum_baseline_difference_db=3.0,
    )
)


__all__ = [
    "DEFAULT_DELTA_SNR_OUTLIER_DETECTION_POLICY",
    "DEFAULT_MAXIMUM_BASELINE_DIFFERENCE_DB",
    "DEFAULT_MINIMUM_DEPARTURE_DB",
    "DEFAULT_MINIMUM_ROBUST_Z",
    "DELTA_SNR_OUTLIER_CONFIG_FIELD_TO_POLICY_FIELD",
    "DELTA_SNR_OUTLIER_MAXIMUM_THRESHOLD",
    "DELTA_SNR_OUTLIER_MINIMUM_THRESHOLD",
    "DeltaSnrOutlierDetectionPolicy",
    "LEGACY_BURST_MINIMUM_DEPARTURE_DB",
    "LEGACY_BURST_MINIMUM_ROBUST_Z",
    "LEGACY_DELTA_SNR_OUTLIER_CONFIG_FIELDS",
    "VERSION_1_OMITTED_DELTA_SNR_OUTLIER_DETECTION_POLICY",
]
