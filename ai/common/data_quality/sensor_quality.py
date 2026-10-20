
"""Validation utilities for environmental sensor observations.

This module flags questionable observations. It does not claim to calibrate
sensors or prove that an observation represents a real environmental event.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from math import isfinite
from typing import Any, Mapping


@dataclass(frozen=True)
class SensorQualityResult:
    """Quality assessment for one sensor observation."""

    accepted: bool
    quality_status: str
    sensor_id: str | None
    rainfall_mm: float | None
    observed_at: str | None
    quality_flags: tuple[str, ...]
    explanation: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly representation."""
        result = asdict(self)
        result["quality_flags"] = list(self.quality_flags)
        return result


def _parse_timestamp(value: Any) -> datetime | None:
    """Parse an ISO-8601 timestamp and require a timezone."""
    if not isinstance(value, str) or not value.strip():
        return None

    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None

    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None

    return parsed.astimezone(timezone.utc)


def assess_sensor_observation(
    observation: Mapping[str, Any],
    *,
    received_at: datetime,
    max_delay_seconds: float = 900.0,
    max_rainfall_mm: float = 500.0,
) -> SensorQualityResult:
    """Validate one rainfall observation and return explicit quality flags.

    Expected fields:
        sensor_id: non-empty sensor identifier
        rainfall_mm: finite, non-negative numeric measurement
        observed_at: timezone-aware ISO-8601 timestamp

    Duplicate detection across multiple observations is handled separately.
    Thresholds are configurable safeguards, not universal physical limits.
    """
    if not isinstance(received_at, datetime):
        raise TypeError("received_at must be a datetime")

    if received_at.tzinfo is None or received_at.utcoffset() is None:
        raise ValueError("received_at must include a timezone")

    for name, value in (
        ("max_delay_seconds", max_delay_seconds),
        ("max_rainfall_mm", max_rainfall_mm),
    ):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{name} must be a number")
        if not isfinite(value) or value < 0:
            raise ValueError(f"{name} must be finite and non-negative")

    flags: list[str] = []

    raw_sensor_id = observation.get("sensor_id")
    sensor_id: str | None = None

    if not isinstance(raw_sensor_id, str) or not raw_sensor_id.strip():
        flags.append("MISSING_OR_INVALID_SENSOR_ID")
    else:
        sensor_id = raw_sensor_id.strip()

    raw_rainfall = observation.get("rainfall_mm")
    rainfall: float | None = None

    if raw_rainfall is None:
        flags.append("MISSING_RAINFALL_MM")
    elif isinstance(raw_rainfall, bool) or not isinstance(
        raw_rainfall, (int, float)
    ):
        flags.append("INVALID_RAINFALL_MM")
    elif not isfinite(raw_rainfall) or raw_rainfall < 0:
        flags.append("INVALID_RAINFALL_MM")
    else:
        rainfall = float(raw_rainfall)
        if rainfall > max_rainfall_mm:
            flags.append("SUSPICIOUSLY_HIGH_RAINFALL_MM")

    raw_timestamp = observation.get("observed_at")
    timestamp = _parse_timestamp(raw_timestamp)

    if timestamp is None:
        flags.append("MISSING_OR_INVALID_OBSERVED_AT")
        observed_at = (
            raw_timestamp.strip()
            if isinstance(raw_timestamp, str) and raw_timestamp.strip()
            else None
        )
    else:
        observed_at = timestamp.isoformat()
        received_utc = received_at.astimezone(timezone.utc)
        delay_seconds = (received_utc - timestamp).total_seconds()

        if delay_seconds < 0:
            flags.append("OBSERVATION_FROM_FUTURE")
        elif delay_seconds > max_delay_seconds:
            flags.append("DELAYED_OBSERVATION")

    blocking_flags = {
        "MISSING_OR_INVALID_SENSOR_ID",
        "MISSING_RAINFALL_MM",
        "INVALID_RAINFALL_MM",
        "MISSING_OR_INVALID_OBSERVED_AT",
        "OBSERVATION_FROM_FUTURE",
    }

    accepted = not any(flag in blocking_flags for flag in flags)

    if not accepted:
        status = "REJECTED"
        explanation = "One or more blocking validation checks failed."
    elif flags:
        status = "FLAGGED"
        explanation = (
            "The observation passed basic validation but has quality warnings."
        )
    else:
        status = "ACCEPTED"
        explanation = "The observation passed the configured quality checks."

    return SensorQualityResult(
        accepted=accepted,
        quality_status=status,
        sensor_id=sensor_id,
        rainfall_mm=rainfall,
        observed_at=observed_at,
        quality_flags=tuple(flags),
        explanation=explanation,
    )
