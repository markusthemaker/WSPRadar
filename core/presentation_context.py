"""Presentation-only context passed explicitly into renderers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping


@dataclass(frozen=True)
class PresentationContext:
    """Localized labels and theme choices that must not affect scientific branches."""

    language: str = "en"
    labels: Mapping[str, str] = field(default_factory=dict)
    theme: str = "dark"
    solar_label: str = "All"

    def label(self, key: str, default: str = "") -> str:
        return str(self.labels.get(key, default))

    def absolute_terms(self, mode: str) -> dict[str, str]:
        """Return mode-specific display terms for Absolute Success Rate views."""
        mode_key = "tx" if str(mode).upper().startswith("TX") else "rx"
        default_counter = "Other Signals" if mode_key == "tx" else "Elsewhere"
        default_short = "OS" if mode_key == "tx" else "E"
        counter = self.label(f"abs_{mode_key}_counter", default_counter)
        counter_short = self.label(f"abs_{mode_key}_counter_short", default_short)
        pair = self.label(f"abs_{mode_key}_pair", f"Target+{counter}")
        formula = self.label(f"abs_{mode_key}_formula", f"Target/(Target+{counter})")
        formula_spaced = self.label(
            f"abs_{mode_key}_formula_spaced",
            f"Target / (Target + {counter})",
        )
        rate_column = self.label(
            f"abs_{mode_key}_rate_column",
            f"Target/(Target+{counter}) (%)",
        )
        counter_column = self.label(f"abs_{mode_key}_counter_column", counter)
        return {
            "mode": mode_key.upper(),
            "target": "Target",
            "target_short": "T",
            "target_column": self.label(f"abs_{mode_key}_target_column", "Target"),
            "counter": counter,
            "counter_short": counter_short,
            "counter_column": counter_column,
            "count_axis_label": self.label(
                f"abs_{mode_key}_count_axis",
                f"Target + {counter} count",
            ),
            "counter_marker": self.label(f"abs_{mode_key}_counter_marker", counter_column),
            "counter_bar": counter,
            "pair": pair,
            "formula": formula,
            "formula_spaced": formula_spaced,
            "rate_column": rate_column,
            "no_evidence": self.label(
                f"abs_{mode_key}_no_evidence",
                f"No T/{counter_short} evidence",
            ),
            "empty_evidence": self.label(
                f"abs_{mode_key}_empty_evidence",
                f"No {pair} evidence",
            ),
            "subtext": self.label(
                f"abs_{mode_key}_subtext",
                f" (T=Target | {counter_short}={counter} | Click a row for evidence)",
            ),
        }
