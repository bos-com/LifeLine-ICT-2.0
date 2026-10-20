
import pytest

from ai.common.deduplication.observations import (
    find_duplicate_observations,
)


def test_identifies_repeated_observation():
    first = {"sensor_id": "S1", "timestamp": "2026-10-20T10:00:00Z", "rainfall_mm": 12}
    repeated = {"sensor_id": "S1", "timestamp": "2026-10-20T10:00:00Z", "rainfall_mm": 12}

    result = find_duplicate_observations([first, repeated])

    assert result["input_count"] == 2
    assert result["unique_count"] == 1
    assert result["duplicate_count"] == 1
    assert result["duplicates"][0]["index"] == 1


def test_keeps_observations_from_different_sensors():
    observations = [
        {"sensor_id": "S1", "timestamp": "2026-10-20T10:00:00Z"},
        {"sensor_id": "S2", "timestamp": "2026-10-20T10:00:00Z"},
    ]

    result = find_duplicate_observations(observations)

    assert result["duplicate_count"] == 0
    assert result["unique_count"] == 2


def test_keeps_same_sensor_observations_at_different_times():
    observations = [
        {"sensor_id": "S1", "timestamp": "2026-10-20T10:00:00Z"},
        {"sensor_id": "S1", "timestamp": "2026-10-20T10:05:00Z"},
    ]

    result = find_duplicate_observations(observations)

    assert result["duplicate_count"] == 0


def test_reports_multiple_retransmissions():
    observation = {"sensor_id": "S1", "timestamp": "2026-10-20T10:00:00Z"}

    result = find_duplicate_observations(
        [observation, observation, observation]
    )

    assert result["unique_count"] == 1
    assert result["duplicate_count"] == 2


def test_missing_identity_values_are_not_assumed_duplicate():
    observations = [
        {"sensor_id": "S1", "timestamp": None},
        {"sensor_id": "S1", "timestamp": None},
    ]

    result = find_duplicate_observations(observations)

    assert result["duplicate_count"] == 0
    assert result["unique_count"] == 2


def test_custom_identity_fields():
    observations = [
        {"observation_id": "O1", "rainfall_mm": 10},
        {"observation_id": "O1", "rainfall_mm": 11},
    ]

    result = find_duplicate_observations(
        observations,
        identity_fields=("observation_id",),
    )

    assert result["duplicate_count"] == 1


def test_rejects_empty_identity_fields():
    with pytest.raises(ValueError):
        find_duplicate_observations([], identity_fields=())


def test_rejects_non_mapping_observation():
    with pytest.raises(TypeError):
        find_duplicate_observations([{"sensor_id": "S1", "timestamp": "t"}, 42])


def test_does_not_modify_input_records():
    observation = {"sensor_id": "S1", "timestamp": "2026-10-20T10:00:00Z"}
    original = observation.copy()

    find_duplicate_observations([observation, observation])

    assert observation == original
