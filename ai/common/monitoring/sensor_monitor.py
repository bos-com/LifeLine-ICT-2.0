
"""Monitor environmental sensor reporting and detect possible outages."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Iterable


@dataclass(frozen=True)
class SensorStatus:
    """Reporting status for one registered sensor."""

    sensor_id: str
    status: str
    last_seen_at: str | None
    seconds_since_last_seen: float | None
    timeout_seconds: float
    explanation: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly result."""
        return asdict(self)


def _utc_datetime(value: datetime, field_name: str) -> datetime:
    """Require a timezone-aware datetime and normalize it to UTC."""
    if not isinstance(value, datetime):
        raise TypeError(f"{field_name} must be a datetime")

    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must include a timezone")

    return value.astimezone(timezone.utc)


def assess_sensor_status(
    sensor_id: str,
    last_seen_at: datetime | None,
    *,
    now: datetime,
    timeout_seconds: float = 900.0,
) -> SensorStatus:
    """Classify a registered sensor based on its latest reporting time.

    ACTIVE: a report was received within the configured timeout.
    OVERDUE: the last report is older than the configured timeout.
    NO_DATA: no report has been recorded.

    The caller is responsible for ensuring last_seen_at represents an
    accepted observation or a valid sensor heartbeat.
    """
    if not isinstance(sensor_id, str) or not sensor_id.strip():
        raise ValueError("sensor_id must be a non-empty string")

    if isinstance(timeout_seconds, bool) or not isinstance(
        timeout_seconds, (int, float)
    ):
        raise TypeError("timeout_seconds must be a number")

    if timeout_seconds < 0 or timeout_seconds != timeout_seconds:
        raise ValueError("timeout_seconds must be non-negative and finite")

    if timeout_seconds == float("inf"):
        raise ValueError("timeout_seconds must be non-negative and finite")

    current_time = _utc_datetime(now, "now")
    normalized_id = sensor_id.strip()

    if last_seen_at is None:
        return SensorStatus(
            sensor_id=normalized_id,
            status="NO_DATA",
            last_seen_at=None,
            seconds_since_last_seen=None,
            timeout_seconds=float(timeout_seconds),
            explanation="No valid report has been recorded for this sensor.",
        )

    last_seen = _utc_datetime(last_seen_at, "last_seen_at")
    elapsed = (current_time - last_seen).total_seconds()

    if elapsed < 0:
        raise ValueError("last_seen_at cannot be later than now")

    if elapsed <= timeout_seconds:
        status = "ACTIVE"
        explanation = "The sensor reported within the configured timeout."
    else:
        status = "OVERDUE"
        explanation = "The sensor has not reported within the configured timeout."

    return SensorStatus(
        sensor_id=normalized_id,
        status=status,
        last_seen_at=last_seen.isoformat(),
        seconds_since_last_seen=elapsed,
        timeout_seconds=float(timeout_seconds),
        explanation=explanation,
    )


def assess_registered_sensors(
    registered_sensor_ids: Iterable[str],
    latest_reports: dict[str, datetime],
    *,
    now: datetime,
    timeout_seconds: float = 900.0,
) -> list[SensorStatus]:
    """Assess all registered sensors, including sensors with no reports."""
    sensor_ids = list(registered_sensor_ids)

    if any(not isinstance(sensor_id, str) or not sensor_id.strip()
           for sensor_id in sensor_ids):
        raise ValueError("all registered sensor IDs must be non-empty strings")

    normalized_ids = [sensor_id.strip() for sensor_id in sensor_ids]

    if len(set(normalized_ids)) != len(normalized_ids):
        raise ValueError("registered sensor IDs must be unique")

    unknown_ids = set(latest_reports) - set(normalized_ids)
    if unknown_ids:
        raise ValueError(
            f"latest_reports contains unregistered sensor IDs: "
            f"{sorted(unknown_ids)}"
        )

    return [
        assess_sensor_status(
            sensor_id,
            latest_reports.get(sensor_id),
            now=now,
            timeout_seconds=timeout_seconds,
        )
        for sensor_id in normalized_ids
    ]
