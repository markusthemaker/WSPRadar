"""Pure presentation helpers for configured Reference-side SNR correction."""

import math

from core.analysis_context import COMPARISON_LOCAL_NEIGHBORHOOD


def _localized_signed_correction_db(correction_db, translations):
    """Format one signed dB value with the active presentation decimal mark."""
    formatted = f"{correction_db:+.1f}"
    if translations["fmt_results_thousands_separator"] == ".":
        formatted = formatted.replace(".", ",")
    return formatted


def _reference_correction_recipient(
    analysis_context,
    translations,
    *,
    is_sequential,
):
    """Name the semantic Reference side receiving the configured correction."""
    comparison_mode = getattr(analysis_context, "comparison_mode", "")
    if comparison_mode == COMPARISON_LOCAL_NEIGHBORHOOD:
        return translations[
            "txt_results_snr_correction_reference_benchmark"
        ]
    if is_sequential:
        return translations[
            "txt_results_snr_correction_reference_schedule"
        ]

    reference_callsign = str(
        getattr(analysis_context, "reference_callsign", "")
    ).strip().upper()
    if not reference_callsign:
        return translations["txt_reference"]
    return translations[
        "txt_results_snr_correction_reference_identity"
    ].format(callsign=reference_callsign)


def configured_snr_correction_notice(
    analysis_context,
    translations,
    *,
    is_compare,
    is_sequential=False,
):
    """Return localized provenance for a nonzero completed Compare correction.

    The numeric value comes only from the immutable completed
    ``AnalysisContext``. It is rounded to the one-decimal precision used by the
    scientific configuration and omitted for Success results or display-zero
    corrections.
    """
    if not is_compare:
        return ""

    try:
        correction_db = float(
            getattr(analysis_context, "reference_snr_correction_db", 0.0)
        )
    except (TypeError, ValueError):
        return ""
    if not math.isfinite(correction_db):
        return ""

    correction_db = round(correction_db, 1)
    if correction_db == 0.0:
        return ""

    recipient = _reference_correction_recipient(
        analysis_context,
        translations,
        is_sequential=bool(is_sequential),
    )
    return translations["txt_results_configured_snr_correction"].format(
        correction_db=_localized_signed_correction_db(
            correction_db,
            translations,
        ),
        recipient=recipient,
    )
