"""Shared canonical configuration fields used by Guided and Classic editors.

The established widget implementations remain in ``config_panel`` during the
incremental UI split so existing callback and rendering contracts stay intact.
This module is the stable composition surface for both editors and prevents a
second implementation of any scientific input.
"""

from .config_panel import (
    _render_analysis_direction_selector as render_analysis_direction,
    render_evidence_threshold_fields,
    render_reference_correction_field,
    render_reference_design_fields,
    render_scope_fields,
    render_station_population_fields,
    render_target_and_window_fields,
)

__all__ = [
    "render_analysis_direction",
    "render_evidence_threshold_fields",
    "render_reference_correction_field",
    "render_reference_design_fields",
    "render_scope_fields",
    "render_station_population_fields",
    "render_target_and_window_fields",
]
