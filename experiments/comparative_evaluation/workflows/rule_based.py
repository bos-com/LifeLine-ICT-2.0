"""Workflow B: conventional validation and duplicate suppression."""

from datetime import datetime, timezone
from math import isfinite
from collections.abc import Mapping


def _parse_timestamp(value):
    if not isinstance(value, str) or not value.strip():
        return None

    try:
        parsed = datetime.fromisoformat(
            value.strip().replace("Z", "+00:00")
        )
    except ValueError:
        return None

    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None

    return parsed.astimezone(timezone.utc)


def run_rule_based(
    observations,
    registered_sensor_ids,
    *,
    received_at,
    max_delay_seconds=900,
    max_rainfall_mm=500,
):
    """Validate, deduplicate and check sensor registration.

    This workflow does not perform integrated sensor-health monitoring.
    """
    registered_ids = set(registered_sensor_ids)
    results = []
    first_seen = {}

    for index, observation in enumerate(observations):
        result = {
            "index": index,
            "status": "REJECTED",
            "risk_eligible": False,
            "forwarded": False,
            "quality_flags": [],
            "duplicate_of_index": None,
        }

        if not isinstance(observation, Mapping):
            result["quality_flags"].append("MALFORMED_OBSERVATION")
            results.append(result)
            continue

        flags = []

        sensor_id = observation.get("sensor_id")
        if not isinstance(sensor_id, str) or not sensor_id.strip():
            flags.append("MISSING_OR_INVALID_SENSOR_ID")
            sensor_id = None
        else:
            sensor_id = sensor_id.strip()

        rainfall = observation.get("rainfall_mm")

        if rainfall is None:
            flags.append("MISSING_RAINFALL_MM")
        elif (
            isinstance(rainfall, bool)
            or not isinstance(rainfall, (int, float))
            or not isfinite(rainfall)
            or rainfall < 0
        ):
            flags.append("INVALID_RAINFALL_MM")

        observed_at = observation.get("observed_at")
        timestamp = _parse_timestamp(observed_at)

        if timestamp is None:
            flags.append("MISSING_OR_INVALID_OBSERVED_AT")
        else:
            delay = (
                received_at.astimezone(timezone.utc) - timestamp
            ).total_seconds()

            if delay < 0:
                flags.append("OBSERVATION_FROM_FUTURE")
            elif delay > max_delay_seconds:
                flags.append("DELAYED_OBSERVATION")

        if (
            isinstance(rainfall, (int, float))
            and not isinstance(rainfall, bool)
            and isfinite(rainfall)
            and rainfall >= 0
            and rainfall > max_rainfall_mm
        ):
            flags.append("SUSPICIOUSLY_HIGH_RAINFALL_MM")

        blocking_flags = {
            "MISSING_OR_INVALID_SENSOR_ID",
            "MISSING_RAINFALL_MM",
            "INVALID_RAINFALL_MM",
            "MISSING_OR_INVALID_OBSERVED_AT",
            "OBSERVATION_FROM_FUTURE",
        }

        if any(flag in blocking_flags for flag in flags):
            result["status"] = "REJECTED"
            result["quality_flags"] = flags
            results.append(result)
            continue

        # Only quality-valid records enter duplicate detection.
        identity = (sensor_id, timestamp.isoformat())

        if identity in first_seen:
            result["status"] = "DUPLICATE"
            result["quality_flags"] = flags + [
                "DUPLICATE_SENSOR_TIMESTAMP"
            ]
            result["duplicate_of_index"] = first_seen[identity]
            results.append(result)
            continue

        first_seen[identity] = index

        if sensor_id not in registered_ids:
            flags.append("UNREGISTERED_SENSOR")
            result["status"] = "FLAGGED"
        elif flags:
            result["status"] = "FLAGGED"
        else:
            result["status"] = "ACCEPTED"

        result["quality_flags"] = flags
        result["forwarded"] = True
        result["risk_eligible"] = (
            result["status"] == "ACCEPTED"
        )

        results.append(result)

    return {
        "workflow": "B_RULE_BASED",
        "records": results,
        "input_count": len(observations),
        "forwarded_count": sum(
            record["forwarded"] for record in results
        ),
    }
