
from datetime import datetime, timezone

import pytest

from ai.common.data_quality.sensor_quality import (
    assess_sensor_observation,
)


RECEIVED_AT = datetime(2026, 10, 21, 9, 0, tzinfo=timezone.utc)


def make_observation(**overrides):
    observation = {
        "sensor_id": "RAIN-001",
        "rainfall_mm": 12.5,
        "observed_at": "2026-10-21T08:55:00Z",
    }
    observation.update(overrides)
    return observation


def test_valid_observation_is_accepted():
    result = assess_sensor_observation(
        make_observation(),
        received_at=RECEIVED_AT,
    )

    assert result.accepted is True
    assert result.quality_status == "ACCEPTED"
    assert result.rainfall_mm == 12.5
    assert result.quality_flags == ()


def test_missing_sensor_id_is_rejected():
    result = assess_sensor_observation(
        make_observation(sensor_id=" "),
        received_at=RECEIVED_AT,
    )

    assert result.accepted is False
    assert "MISSING_OR_INVALID_SENSOR_ID" in result.quality_flags


def test_missing_rainfall_is_rejected():
    result = assess_sensor_observation(
        make_observation(rainfall_mm=None),
        received_at=RECEIVED_AT,
    )

    assert result.accepted is False
    assert "MISSING_RAINFALL_MM" in result.quality_flags


@pytest.mark.parametrize("value", [-1, float("inf"), float("nan"), "bad", True])
def test_invalid_rainfall_is_rejected(value):
    result = assess_sensor_observation(
        make_observation(rainfall_mm=value),
        received_at=RECEIVED_AT,
    )

    assert result.accepted is False
    assert "INVALID_RAINFALL_MM" in result.quality_flags


def test_zero_rainfall_is_valid():
    result = assess_sensor_observation(
        make_observation(rainfall_mm=0),
        received_at=RECEIVED_AT,
    )

    assert result.accepted is True
    assert result.rainfall_mm == 0.0


def test_delayed_observation_is_flagged_but_retained():
    result = assess_sensor_observation(
        make_observation(observed_at="2026-10-21T08:00:00Z"),
        received_at=RECEIVED_AT,
        max_delay_seconds=900,
    )

    assert result.accepted is True
    assert result.quality_status == "FLAGGED"
    assert "DELAYED_OBSERVATION" in result.quality_flags


def test_future_timestamp_is_rejected():
    result = assess_sensor_observation(
        make_observation(observed_at="2026-10-21T09:05:00Z"),
        received_at=RECEIVED_AT,
    )

    assert result.accepted is False
    assert "OBSERVATION_FROM_FUTURE" in result.quality_flags


def test_timestamp_without_timezone_is_rejected():
    result = assess_sensor_observation(
        make_observation(observed_at="2026-10-21T08:55:00"),
        received_at=RECEIVED_AT,
    )

    assert result.accepted is False
    assert "MISSING_OR_INVALID_OBSERVED_AT" in result.quality_flags


def test_high_rainfall_is_flagged_not_silently_discarded():
    result = assess_sensor_observation(
        make_observation(rainfall_mm=510),
        received_at=RECEIVED_AT,
        max_rainfall_mm=500,
    )

    assert result.accepted is True
    assert result.quality_status == "FLAGGED"
    assert "SUSPICIOUSLY_HIGH_RAINFALL_MM" in result.quality_flags
    assert result.rainfall_mm == 510.0


def test_result_is_json_friendly():
    result = assess_sensor_observation(
        make_observation(),
        received_at=RECEIVED_AT,
    )

    payload = result.to_dict()

    assert payload["quality_status"] == "ACCEPTED"
    assert isinstance(payload["quality_flags"], list)


def test_naive_receive_timestamp_is_rejected():
    with pytest.raises(ValueError):
        assess_sensor_observation(
            make_observation(),
            received_at=datetime(2026, 10, 21, 9, 0),
        )


def test_negative_delay_limit_is_rejected():
    with pytest.raises(ValueError):
        assess_sensor_observation(
            make_observation(),
            received_at=RECEIVED_AT,
            max_delay_seconds=-1,
        )
