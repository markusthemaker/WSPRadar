"""Presentation-only context passed explicitly into renderers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping


@dataclass(frozen=True)
class PresentationContext:
    """Localized labels and theme choices that must not affect scientific branches."""

    solar_label: str
    language: str = "en"
    labels: Mapping[str, str] = field(default_factory=dict)
    theme: str = "dark"

    def label(self, key: str, default: str = "") -> str:
        return str(self.labels.get(key, default))

    def absolute_terms(self, mode: str) -> dict[str, str]:
        """Return canonical compatibility terms and localized Performance labels.

        Canonical counter names and formulas remain available for compatibility
        exports and scientific documentation. The explicit opportunity/station
        outcome names are the direction-aware vocabulary used by interactive
        and figure presentation layers.
        """
        mode_key = "tx" if str(mode).upper().startswith("TX") else "rx"
        default_counter = "Other Signals" if mode_key == "tx" else "Elsewhere"
        default_short = "OS" if mode_key == "tx" else "E"
        counter = self.label(f"abs_{mode_key}_counter", default_counter)
        counter_short = self.label(f"abs_{mode_key}_counter_short", default_short)
        pair = self.label(f"abs_{mode_key}_pair", f"Target+{counter}")
        formula = self.label(f"abs_{mode_key}_formula", f"Target/(Target+{counter})")
        rate_column = self.label(
            f"abs_{mode_key}_rate_column",
            f"Target/(Target+{counter}) (%)",
        )
        counter_column = self.label(f"abs_{mode_key}_counter_column", counter)
        return {
            "mode": mode_key.upper(),
            "target_column": self.label(f"abs_{mode_key}_target_column", "Target"),
            "counter": counter,
            "counter_short": counter_short,
            "counter_column": counter_column,
            "opportunity_success": str(
                self.labels[f"success_{mode_key}_opportunity_success"]
            ),
            "opportunity_counter": str(
                self.labels[f"success_{mode_key}_opportunity_counter"]
            ),
            "station_success": str(
                self.labels[f"success_{mode_key}_station_success"]
            ),
            "station_counter": str(
                self.labels[f"success_{mode_key}_station_counter"]
            ),
            "target_only_audit": str(
                self.labels[f"success_{mode_key}_target_only_audit"]
            ),
            "presentation_subtext": str(
                self.labels[f"success_{mode_key}_subtext"]
            ),
            "show_counter": str(
                self.labels[f"success_{mode_key}_show_counter"]
            ),
            "pair": pair,
            "formula": formula,
            "rate_column": rate_column,
        }
