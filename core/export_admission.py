"""Process-wide admission control for high-resolution result exports."""

from config import (
    EXPORT_ACTIVE_LEASE_TIMEOUT_SEC,
    EXPORT_MAX_CONCURRENT,
    EXPORT_MAX_QUEUED,
    EXPORT_QUEUE_POLL_INTERVAL_SEC,
    EXPORT_QUEUE_WAIT_TIMEOUT_SEC,
)
from core.analysis_admission import AnalysisAdmissionController


EXPORT_ADMISSION_GATE = AnalysisAdmissionController(
    max_active=EXPORT_MAX_CONCURRENT,
    max_queued=EXPORT_MAX_QUEUED,
    wait_timeout_seconds=EXPORT_QUEUE_WAIT_TIMEOUT_SEC,
    lease_timeout_seconds=EXPORT_ACTIVE_LEASE_TIMEOUT_SEC,
    poll_interval_seconds=EXPORT_QUEUE_POLL_INTERVAL_SEC,
)
