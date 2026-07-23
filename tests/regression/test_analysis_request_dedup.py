from dataclasses import replace
from datetime import datetime, timedelta, timezone

from core.analysis_context import (
    AnalysisContext,
    TX_AB_METHOD_SEQUENTIAL,
)
from ui.analysis_context_adapter import build_analysis_context_from_session_state
from ui.run_controller import _analysis_request_fingerprint


START = datetime(2026, 7, 1, 12, 0, tzinfo=timezone.utc)
END = START + timedelta(hours=24)


def _fingerprint(context=None, **overrides):
    values = {
        "analysis_context": context or AnalysisContext(
            run_mode="RX",
            callsign="DL1MKS",
            qth="JN37AA",
            band="20m",
        ),
        "start_t": START,
        "end_t": END,
        "band_filter": "AND band = '14'",
        "active_demo_profile": None,
    }
    values.update(overrides)
    return _analysis_request_fingerprint(**values)


def test_analysis_request_fingerprint_is_stable_for_equivalent_requests():
    first_context = AnalysisContext(
        run_mode="RX",
        callsign="DL1MKS",
        qth="JN37AA",
        band="20m",
    )
    second_context = AnalysisContext.from_dict(first_context.to_dict())

    assert _fingerprint(first_context) == _fingerprint(second_context)


def test_analysis_request_fingerprint_changes_with_scientific_inputs():
    context = AnalysisContext(
        run_mode="RX",
        callsign="DL1MKS",
        qth="JN37AA",
        band="20m",
    )

    assert _fingerprint(context) != _fingerprint(
        replace(context, reference_snr_correction_db=1.2)
    )
    assert _fingerprint(context) != _fingerprint(
        replace(context, reference_qth="JO62")
    )
    assert _fingerprint(context) != _fingerprint(
        replace(context, tx_ab_method=TX_AB_METHOD_SEQUENTIAL)
    )
    assert _fingerprint(context) != _fingerprint(
        replace(context, tx_ab_repeat_interval_minutes=20)
    )
    assert _fingerprint(context) != _fingerprint(
        replace(context, tx_ab_reference_start_minute=4)
    )
    assert _fingerprint(context) != _fingerprint(
        replace(context, max_peer_distance_km=10000)
    )
    assert _fingerprint(context) != _fingerprint(context, end_t=END + timedelta(minutes=2))


def test_correction_workflow_mode_does_not_change_request_fingerprint():
    """Exclude correction provenance when the applied numeric value is unchanged."""
    base_state = {
        "val_analysis_direction": "rx",
        "val_comp_mode": "hardware_ab",
        "val_snr_correction_mode": "no_offset",
        "val_benchmark_offset_db": 0.0,
    }
    establishment_state = {
        **base_state,
        "val_snr_correction_mode": "establish_offset",
    }

    assert _fingerprint(
        build_analysis_context_from_session_state(base_state)
    ) == _fingerprint(
        build_analysis_context_from_session_state(establishment_state)
    )


def test_analysis_request_fingerprint_preserves_demo_identity():
    assert _fingerprint(active_demo_profile="demo-rx-europe") != _fingerprint(
        active_demo_profile="demo-tx-europe"
    )


def test_analysis_context_serializes_only_canonical_target_reference_identity():
    values = AnalysisContext(
        callsign="DL1MKS",
        qth="JN37UN",
        reference_callsign="DL2XYZ",
        reference_qth="JO62",
    ).to_dict()

    assert values["reference_callsign"] == "DL2XYZ"
    assert values["reference_qth"] == "JO62"
    assert "setup_b_callsign" not in values
