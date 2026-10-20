
from datetime import datetime, timedelta, timezone

import pytest

from ai.common.monitoring.sensor_monitor import (
    assess_registered_sensors,
    assess_sensor_status,
)


NOW = datetime(2026, 10, 21, 12, 0, tzinfo=timezone.utc)


def test_recent_report_is_active():
    result = assess_sensor_status(
        "RAIN-001",
        NOW - timedelta(minutes=5),
        now=NOW,
    )

    assert result.status == "ACTIVE"
    assert result.seconds_since_last_seen == 300


def test_report_at_timeout_boundary_is_active():
    result = assess_sensor_status(
        "RAIN-001",
        NOW - timedelta(seconds=900),
        now=NOW,
        timeout_seconds=900,
    )

    assert result.status == "ACTIVE"


def test_report_after_timeout_is_overdue():
    result = assess_sensor_status(
        "RAIN-001",
        NOW - timedelta(minutes=20),
        now=NOW,
    )

    assert result.status == "OVERDUE"
    assert result.seconds_since_last_seen == 1200


def test_sensor_without_report_is_no_data():
    result = assess_sensor_status(
        "RAIN-002",
        None,
        now=NOW,
    )

    assert result.status == "NO_DATA"
    assert result.last_seen_at is None
    assert result.seconds_since_last_seen is None


def test_timeout_is_configurable():
    result = assess_sensor_status(
        "RAIN-001",
        NOW - timedelta(minutes=5),
        now=NOW,
        timeout_seconds=120,
    )

    assert result.status == "OVERDUE"


def test_future_report_time_is_rejected():
    with pytest.raises(ValueError):
        assess_sensor_status(
            "RAIN-001",
            NOW + timedelta(minutes=1),
            now=NOW,
        )


def test_naive_current_time_is_rejected():
    with pytest.raises(ValueError):
        assess_sensor_status(
            "RAIN-001",
            None,
            now=datetime(2026, 10, 21, 12, 0),
        )


def test_empty_sensor_id_is_rejected():
    with pytest.raises(ValueError):
        assess_sensor_status(" ", NOW, now=NOW)


def test_negative_timeout_is_rejected():
    with pytest.raises(ValueError):
        assess_sensor_status(
            "RAIN-001",
            NOW,
            now=NOW,
            timeout_seconds=-1,
        )


def test_registered_sensor_without_report_is_included():
    results = assess_registered_sensors(
        ["RAIN-001", "RAIN-002"],
        {"RAIN-001": NOW - timedelta(minutes=2)},
        now=NOW,
    )

    assert [result.status for result in results] == ["ACTIVE", "NO_DATA"]


def test_duplicate_registered_ids_are_rejected():
    with pytest.raises(ValueError):
        assess_registered_sensors(
            ["RAIN-001", "RAIN-001"],
            {},
            now=NOW,
        )


def test_unknown_report_sensor_is_rejected():
    with pytest.raises(ValueError):
        assess_registered_sensors(
            ["RAIN-001"],
            {"RAIN-999": NOW},
            now=NOW,
        )


def test_status_result_is_json_friendly():
    result = assess_sensor_status(
        "RAIN-001",
        NOW,
        now=NOW,
    )

    payload = result.to_dict()

    assert payload["sensor_id"] == "RAIN-001"
    assert payload["status"] == "ACTIVE"
