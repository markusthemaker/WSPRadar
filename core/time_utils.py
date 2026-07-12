"""Dependency-free UTC time helpers used by the idle application shell."""

from datetime import datetime


def quantize_time(timestamp: datetime) -> datetime:
    """Floor a timestamp to a 15-minute boundary for stable query caching."""
    minute = (timestamp.minute // 15) * 15
    return timestamp.replace(minute=minute, second=0, microsecond=0)
