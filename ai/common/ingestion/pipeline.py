"""Batch ingestion pipeline for resilient environmental observations.

This module coordinates quality validation, duplicate detection, sensor
reporting status, and optional threshold-based flood-risk assessment.

Rainfall summary values passed to this pipeline must be calculated by the
caller from eligible, unique observations using an explicitly documented
aggregation policy. This module does not aggregate measurements across
sensors or claim to calculate a validated flood probability.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any

from ai.common.data_quality.sensor_quality import assess_sensor_observation
from ai.common.deduplication.observations import find_duplicate_observations
from ai.common.monitoring.sensor_monitor import assess_registered_sensors
from ai.hazards.flood.baseline import assess_flood_risk


def ingest_observation_batch(
    observations: Sequence[Mapping[str, Any]],
    registered_sensor_ids: Sequence[str],
    *,
    received_at: datetime,
    timeout_seconds: float = 900.0,
    max_delay_seconds: float = 900.0,
    max_rainfall_mm: float = 500.0,
    daily_rainfall_mm: float | None = None,
    three_day_rainfall_mm: float | None = None,
    include_flagged_in_risk: bool = False,
) -> dict[str, Any]:
    """Validate, deduplicate, monitor, and summarize an observation batch.

    Record outcomes are ACCEPTED, FLAGGED, REJECTED, or DUPLICATE.

    FLAGGED observations are excluded from risk eligibility by default.
    Sensor health uses unique observations that passed blocking quality
    checks. A batch's received_at represents the actual ingestion time.

    The optional rainfall summaries must already have been calculated from
    eligible, unique observations by the caller. If no eligible observations
    remain, flood risk is UNKNOWN regardless of supplied summary values.
    """
    if isinstance(observations, (str, bytes)) or not isinstance(
        observations, Sequence
    ):
        raise TypeError("observations must be a sequence of mappings")

    if isinstance(registered_sensor_ids, (str, bytes)) or not isinstance(
        registered_sensor_ids, Sequence
    ):
        raise TypeError("registered_sensor_ids must be a sequence of IDs")

    if not isinstance(received_at, datetime):
        raise TypeError("received_at must be a datetime")
    if received_at.tzinfo is None or received_at.utcoffset() is None:
        raise ValueError("received_at must include a timezone")

    if not isinstance(include_flagged_in_risk, bool):
        raise TypeError("include_flagged_in_risk must be a boolean")

    # Assess every record independently so one malformed record does not
    # prevent other records in the batch from being processed.
    results: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []

    for index, observation in enumerate(observations):
        if not isinstance(observation, Mapping):
            results.append(
                {
                    "index": index,
                    "status": "REJECTED",
                    "sensor_id": None,
                    "observed_at": None,
                    "quality_flags": ["MALFORMED_OBSERVATION"],
                    "explanation": "Observation must be a mapping.",
                    "duplicate_of_index": None,
                }
            )
            continue

        quality = assess_sensor_observation(
            observation,
            received_at=received_at,
            max_delay_seconds=max_delay_seconds,
            max_rainfall_mm=max_rainfall_mm,
        )

        record = {
            "index": index,
            "status": quality.quality_status,
            "sensor_id": quality.sensor_id,
            "observed_at": quality.observed_at,
            "quality_flags": list(quality.quality_flags),
            "explanation": quality.explanation,
            "duplicate_of_index": None,
        }
        results.append(record)

        if quality.accepted:
            # Use normalized UTC timestamps so equivalent ISO-8601 strings
            # such as Z and +00:00 identify the same observation.
            candidates.append(
                {
                    "sensor_id": quality.sensor_id,
                    "timestamp": quality.observed_at,
                    "_original_index": index,
                    "_quality_status": quality.quality_status,
                    "_rainfall_mm": quality.rainfall_mm,
                }
            )

    deduplication = find_duplicate_observations(
        candidates,
        identity_fields=("sensor_id", "timestamp"),
    )

    duplicate_indexes: set[int] = set()
    unique_indexes: set[int] = set()
    first_seen: dict[tuple[str, str], int] = {}

    for candidate in deduplication["unique_observations"]:
        original_index = candidate["_original_index"]
        unique_indexes.add(original_index)
        key = (candidate["sensor_id"], candidate["timestamp"])
        first_seen[key] = original_index

    for duplicate in deduplication["duplicates"]:
        candidate = duplicate["observation"]
        original_index = candidate["_original_index"]
        duplicate_indexes.add(original_index)
        key = (candidate["sensor_id"], candidate["timestamp"])
        original_index_of_first = first_seen[key]

        results[original_index]["status"] = "DUPLICATE"
        results[original_index]["duplicate_of_index"] = original_index_of_first
        results[original_index]["explanation"] = (
            f"Duplicate of observation at input index {original_index_of_first}."
        )
        results[original_index]["quality_flags"].append(
            "DUPLICATE_SENSOR_TIMESTAMP"
        )

    registered_ids = {
        sensor_id.strip()
        for sensor_id in registered_sensor_ids
        if isinstance(sensor_id, str) and sensor_id.strip()
    }

    latest_reports: dict[str, datetime] = {}
    eligible_indexes: set[int] = set()

    for candidate in deduplication["unique_observations"]:
        sensor_id = candidate["sensor_id"]
        original_index = candidate["_original_index"]

        # Unknown sensors are retained in the audit trail, but they cannot
        # establish registered-sensor health or contribute to flood risk.
        if sensor_id not in registered_ids:
            results[original_index]["status"] = "FLAGGED"
            results[original_index]["quality_flags"].append(
                "UNREGISTERED_SENSOR"
            )
            results[original_index]["explanation"] = (
                "Observation passed basic validation but its sensor ID "
                "is not registered."
            )
            results[original_index]["risk_eligible"] = False
            continue

        # A valid, unique report establishes recent receipt activity.
        latest_reports[sensor_id] = received_at

        status = candidate["_quality_status"]
        if status == "ACCEPTED" or include_flagged_in_risk:
            eligible_indexes.add(original_index)

    for original_index in eligible_indexes:
        results[original_index]["risk_eligible"] = True

    for original_index in unique_indexes - eligible_indexes:
        results[original_index]["risk_eligible"] = False

    # The monitoring component requires registered IDs. It returns a status
    # for every registered sensor, including those with no valid report.
    sensor_statuses = assess_registered_sensors(
        registered_sensor_ids,
        latest_reports,
        now=received_at,
        timeout_seconds=timeout_seconds,
    )

    # Risk summaries are supplied by the caller after its aggregation policy
    # has selected the eligible, unique observations.
    if eligible_indexes:
        risk = assess_flood_risk(
            daily_rainfall_mm,
            three_day_rainfall_mm,
        )
    else:
        risk = assess_flood_risk(None, None)

    counts = {
        status: sum(record["status"] == status for record in results)
        for status in ("ACCEPTED", "FLAGGED", "REJECTED", "DUPLICATE")
    }

    return {
        "received_at": received_at.isoformat(),
        "input_count": len(observations),
        "outcome_counts": counts,
        "eligible_observation_count": len(eligible_indexes),
        "records": results,
        "sensor_statuses": [status.to_dict() for status in sensor_statuses],
        "deduplication": {
            "candidate_count": deduplication["input_count"],
            "unique_count": deduplication["unique_count"],
            "duplicate_count": deduplication["duplicate_count"],
        },
        "flood_risk": risk.to_dict(),
        "policy": {
            "include_flagged_in_risk": include_flagged_in_risk,
            "rainfall_summaries_aggregated_by_pipeline": False,
        },
    }
