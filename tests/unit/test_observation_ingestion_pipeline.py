"""Integration tests for the resilient observation-ingestion pipeline."""

from datetime import datetime, timezone

from ai.common.ingestion.pipeline import ingest_observation_batch


NOW = datetime(2026, 10, 21, 9, 0, tzinfo=timezone.utc)


def observation(
    sensor_id="RAIN-01",
    rainfall_mm=12.5,
    observed_at="2026-10-21T08:55:00Z",
):
    return {
        "sensor_id": sensor_id,
        "rainfall_mm": rainfall_mm,
        "observed_at": observed_at,
    }


def run_pipeline(records, registered=("RAIN-01",), **kwargs):
    return ingest_observation_batch(
        records,
        registered,
        received_at=NOW,
        **kwargs,
    )


def test_accepts_valid_observation_and_reports_sensor_active():
    result = run_pipeline(
        [observation()],
        daily_rainfall_mm=30,
        three_day_rainfall_mm=70,
    )

    assert result["outcome_counts"]["ACCEPTED"] == 1
    assert result["eligible_observation_count"] == 1
    assert result["records"][0]["risk_eligible"] is True
    assert result["sensor_statuses"][0]["status"] == "ACTIVE"
    assert result["flood_risk"]["risk_level"] == "HIGH"


def test_detects_duplicate_with_equivalent_utc_timestamp():
    result = run_pipeline(
        [
            observation(observed_at="2026-10-21T08:55:00Z"),
            observation(observed_at="2026-10-21T08:55:00+00:00"),
        ],
        daily_rainfall_mm=30,
        three_day_rainfall_mm=70,
    )

    assert result["outcome_counts"]["ACCEPTED"] == 1
    assert result["outcome_counts"]["DUPLICATE"] == 1
    assert result["records"][1]["duplicate_of_index"] == 0
    assert result["eligible_observation_count"] == 1
    assert result["deduplication"]["duplicate_count"] == 1


def test_rejects_invalid_observation_without_aborting_batch():
    result = run_pipeline(
        [
            observation(rainfall_mm=-1),
            observation(sensor_id="RAIN-02"),
        ],
        registered=("RAIN-01", "RAIN-02"),
    )

    assert result["outcome_counts"]["REJECTED"] == 1
    assert result["outcome_counts"]["ACCEPTED"] == 1
    assert result["records"][0]["status"] == "REJECTED"
    assert "INVALID_RAINFALL_MM" in result["records"][0]["quality_flags"]


def test_delayed_observation_is_flagged_and_excluded_from_risk_by_default():
    result = run_pipeline(
        [observation(observed_at="2026-10-21T08:00:00Z")],
        max_delay_seconds=900,
        daily_rainfall_mm=30,
        three_day_rainfall_mm=70,
    )

    assert result["outcome_counts"]["FLAGGED"] == 1
    assert result["eligible_observation_count"] == 0
    assert result["records"][0]["risk_eligible"] is False
    assert "DELAYED_OBSERVATION" in result["records"][0]["quality_flags"]
    assert result["flood_risk"]["risk_level"] == "UNKNOWN"


def test_flagged_observation_can_be_included_by_explicit_policy():
    result = run_pipeline(
        [observation(observed_at="2026-10-21T08:00:00Z")],
        max_delay_seconds=900,
        include_flagged_in_risk=True,
        daily_rainfall_mm=30,
        three_day_rainfall_mm=70,
    )

    assert result["outcome_counts"]["FLAGGED"] == 1
    assert result["eligible_observation_count"] == 1
    assert result["records"][0]["risk_eligible"] is True
    assert result["flood_risk"]["risk_level"] == "HIGH"


def test_sensor_without_a_valid_report_is_no_data():
    result = run_pipeline(
        [observation(rainfall_mm=None)],
        registered=("RAIN-01", "RAIN-02"),
    )

    statuses = {
        item["sensor_id"]: item["status"]
        for item in result["sensor_statuses"]
    }

    assert statuses["RAIN-01"] == "NO_DATA"
    assert statuses["RAIN-02"] == "NO_DATA"


def test_malformed_record_does_not_abort_valid_record():
    result = run_pipeline(
        [
            None,
            observation(),
        ],
        daily_rainfall_mm=12,
        three_day_rainfall_mm=20,
    )

    assert result["outcome_counts"]["REJECTED"] == 1
    assert result["outcome_counts"]["ACCEPTED"] == 1
    assert result["records"][0]["quality_flags"] == [
        "MALFORMED_OBSERVATION"
    ]


def test_missing_rainfall_summary_produces_unknown_risk():
    result = run_pipeline(
        [observation()],
        daily_rainfall_mm=12,
        three_day_rainfall_mm=None,
    )

    assert result["flood_risk"]["risk_level"] == "UNKNOWN"
    assert result["flood_risk"]["status"] == "INSUFFICIENT_DATA"


def test_duplicate_does_not_increase_risk_eligible_count():
    result = run_pipeline(
        [observation(), observation()],
        daily_rainfall_mm=20,
        three_day_rainfall_mm=40,
    )

    assert result["eligible_observation_count"] == 1
    assert result["outcome_counts"]["DUPLICATE"] == 1
    assert result["flood_risk"]["risk_level"] == "LOW"


def test_empty_batch_reports_no_data_and_unknown_risk():
    result = run_pipeline([], registered=("RAIN-01",))

    assert result["input_count"] == 0
    assert result["eligible_observation_count"] == 0
    assert result["sensor_statuses"][0]["status"] == "NO_DATA"
    assert result["flood_risk"]["risk_level"] == "UNKNOWN"


def test_unregistered_sensor_is_flagged_without_aborting_batch():
    result = run_pipeline(
        [
            observation(sensor_id="UNKNOWN-99"),
            observation(sensor_id="RAIN-01"),
        ],
        registered=("RAIN-01",),
        daily_rainfall_mm=12,
        three_day_rainfall_mm=20,
    )

    unknown = result["records"][0]

    assert unknown["status"] == "FLAGGED"
    assert "UNREGISTERED_SENSOR" in unknown["quality_flags"]
    assert unknown["risk_eligible"] is False
    assert result["records"][1]["status"] == "ACCEPTED"
    assert result["eligible_observation_count"] == 1
    assert result["sensor_statuses"][0]["sensor_id"] == "RAIN-01"


def test_unregistered_sensor_does_not_count_as_registered_sensor_activity():
    result = run_pipeline(
        [observation(sensor_id="UNKNOWN-99")],
        registered=("RAIN-01",),
    )

    assert result["records"][0]["status"] == "FLAGGED"
    assert result["sensor_statuses"][0]["sensor_id"] == "RAIN-01"
    assert result["sensor_statuses"][0]["status"] == "NO_DATA"
    assert result["eligible_observation_count"] == 0
    assert result["flood_risk"]["risk_level"] == "UNKNOWN"
