"""Workflow C: proposed integrated LifeLine-ICT ingestion pipeline."""

from datetime import datetime

from ai.common.ingestion.pipeline import ingest_observation_batch


def run_proposed(
    observations,
    registered_sensor_ids,
    *,
    received_at,
    timeout_seconds=900,
    max_delay_seconds=900,
    max_rainfall_mm=500,
    include_flagged_in_risk=False,
):
    """Run the actual LifeLine-ICT integrated ingestion pipeline."""
    output = ingest_observation_batch(
        observations,
        registered_sensor_ids,
        received_at=received_at,
        timeout_seconds=timeout_seconds,
        max_delay_seconds=max_delay_seconds,
        max_rainfall_mm=max_rainfall_mm,
        include_flagged_in_risk=include_flagged_in_risk,
    )

    results = []

    for record in output["records"]:
        results.append({
            "index": record["index"],
            "status": record["status"],
            "risk_eligible": record.get("risk_eligible", False),
            "forwarded": record["status"] not in ("REJECTED", "DUPLICATE"),
            "quality_flags": record["quality_flags"],
            "duplicate_of_index": record["duplicate_of_index"],
        })

    return {
        "workflow": "C_PROPOSED",
        "records": results,
        "input_count": output["input_count"],
        "forwarded_count": sum(
            record["forwarded"] for record in results
        ),
        "pipeline_output": output,
    }
