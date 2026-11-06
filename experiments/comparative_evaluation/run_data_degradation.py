
"""Run Experiment 2 across three comparative workflows.

A: Unfiltered workflow
B: Rule-based workflow
C: Proposed LifeLine-ICT ingestion pipeline

The experiment evaluates:
1. Missing observations.
2. Delayed observations.
3. Duplicate transmissions.
4. Sensor-health monitoring.

Original datasets are never modified.
"""

import json
from collections import Counter
from datetime import datetime
from pathlib import Path

from workflows.unfiltered import run_unfiltered
from workflows.rule_based import run_rule_based
from workflows.proposed import run_proposed


BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "data" / "degraded_scenarios.json"

OUTPUT_FILE = (
    BASE_DIR
    / "results"
    / "raw"
    / "data_degradation_results.json"
)


WORKFLOW_NAMES = [
    "A_UNFILTERED",
    "B_RULE_BASED",
    "C_PROPOSED",
]


def load_scenarios():
    """Load and validate the degradation scenarios."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Scenario file not found: {INPUT_FILE}"
        )

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if data.get("experiment_id") != "data-degradation-v1":
        raise ValueError("Unexpected experiment ID.")

    return data


def count_workflow_results(records):
    """Calculate record-level workflow metrics."""

    status_counts = Counter(
        record["status"] for record in records
    )

    return {
        "input_count": len(records),
        "status_counts": dict(sorted(status_counts.items())),
        "forwarded_count": sum(
            record["forwarded"] for record in records
        ),
        "risk_eligible_count": sum(
            record["risk_eligible"] for record in records
        ),
        "flagged_count": status_counts.get("FLAGGED", 0),
        "rejected_count": status_counts.get("REJECTED", 0),
        "duplicate_count": status_counts.get("DUPLICATE", 0),
        "delayed_flag_count": sum(
            "DELAYED_OBSERVATION" in record["quality_flags"]
            for record in records
        ),
    }


def assess_sensor_health(
    sensor_statuses,
    registered_sensor_ids,
    observations,
):
    """Compare pipeline sensor statuses with expected batch reports.

    Each generated batch is expected to contain one observation
    from every registered sensor.

    A missing sensor report is expected to correspond to NO_DATA
    in the proposed pipeline's point-in-time assessment.
    """

    registered = set(registered_sensor_ids)

    observed_sensor_ids = {
        observation.get("sensor_id")
        for observation in observations
        if observation.get("sensor_id") in registered
    }

    expected_missing_sensor_ids = (
        registered - observed_sensor_ids
    )

    status_sensor_ids = {
        item["sensor_id"]
        for item in sensor_statuses
    }

    if status_sensor_ids != registered:
        raise RuntimeError(
            "Sensor monitoring output does not match "
            "the registered sensor population."
        )

    status_counts = Counter(
        item["status"] for item in sensor_statuses
    )

    status_by_sensor = {
        item["sensor_id"]: item["status"]
        for item in sensor_statuses
    }

    correctly_detected = sum(
        status_by_sensor[sensor_id] == "NO_DATA"
        for sensor_id in expected_missing_sensor_ids
    )

    false_positives = sum(
        status_by_sensor[sensor_id] == "NO_DATA"
        and sensor_id not in expected_missing_sensor_ids
        for sensor_id in registered
    )

    false_negatives = sum(
        status_by_sensor[sensor_id] != "NO_DATA"
        for sensor_id in expected_missing_sensor_ids
    )

    registered_count = len(registered)
    expected_missing_count = len(expected_missing_sensor_ids)

    missing_percentage = (
        expected_missing_count / registered_count * 100
        if registered_count else 0.0
    )

    detection_rate = (
        correctly_detected / expected_missing_count * 100
        if expected_missing_count else None
    )

    return {
        "registered_sensor_count": registered_count,
        "observed_sensor_count": len(observed_sensor_ids),
        "expected_missing_sensor_count": expected_missing_count,
        "missing_observation_percentage": round(
            missing_percentage, 2
        ),
        "status_counts": {
            "ACTIVE": status_counts.get("ACTIVE", 0),
            "OVERDUE": status_counts.get("OVERDUE", 0),
            "NO_DATA": status_counts.get("NO_DATA", 0),
        },
        "correctly_detected_missing_sensors": correctly_detected,
        "false_positive_no_data_count": false_positives,
        "false_negative_no_data_count": false_negatives,
        "missing_sensor_detection_rate_percent": (
            round(detection_rate, 2)
            if detection_rate is not None else None
        ),
    }


def aggregate_sensor_health(batch_results):
    """Aggregate sensor-health measurements across batches."""

    health_results = [
        batch["sensor_health"]
        for batch in batch_results
        if batch.get("sensor_health") is not None
    ]

    if not health_results:
        return None

    registered_assessments = sum(
        item["registered_sensor_count"]
        for item in health_results
    )

    expected_missing = sum(
        item["expected_missing_sensor_count"]
        for item in health_results
    )

    correctly_detected = sum(
        item["correctly_detected_missing_sensors"]
        for item in health_results
    )

    false_positives = sum(
        item["false_positive_no_data_count"]
        for item in health_results
    )

    false_negatives = sum(
        item["false_negative_no_data_count"]
        for item in health_results
    )

    active_count = sum(
        item["status_counts"]["ACTIVE"]
        for item in health_results
    )

    overdue_count = sum(
        item["status_counts"]["OVERDUE"]
        for item in health_results
    )

    no_data_count = sum(
        item["status_counts"]["NO_DATA"]
        for item in health_results
    )

    missing_percentage = (
        expected_missing / registered_assessments * 100
        if registered_assessments else 0.0
    )

    detection_rate = (
        correctly_detected / expected_missing * 100
        if expected_missing else None
    )

    return {
        "batch_count": len(health_results),
        "registered_sensor_assessments": registered_assessments,
        "active_count": active_count,
        "overdue_count": overdue_count,
        "no_data_count": no_data_count,
        "expected_missing_sensor_reports": expected_missing,
        "correctly_detected_missing_sensor_reports": (
            correctly_detected
        ),
        "false_positive_no_data_count": false_positives,
        "false_negative_no_data_count": false_negatives,
        "missing_observation_percentage": round(
            missing_percentage, 2
        ),
        "missing_sensor_detection_rate_percent": (
            round(detection_rate, 2)
            if detection_rate is not None else None
        ),
    }


def run_one_workflow(
    workflow_name,
    batch,
    registered_sensor_ids,
    configuration,
):
    """Execute one workflow against one batch."""

    observations = [
        item["observation"]
        for item in batch["records"]
    ]

    received_at = datetime.fromisoformat(
        batch["received_at"]
    )

    sensor_statuses = None
    sensor_health = None

    if workflow_name == "A_UNFILTERED":

        output = run_unfiltered(observations)

    elif workflow_name == "B_RULE_BASED":

        output = run_rule_based(
            observations,
            registered_sensor_ids,
            received_at=received_at,
            max_delay_seconds=configuration["max_delay_seconds"],
            max_rainfall_mm=configuration["max_rainfall_mm"],
        )

    elif workflow_name == "C_PROPOSED":

        output = run_proposed(
            observations,
            registered_sensor_ids,
            received_at=received_at,
            timeout_seconds=configuration["timeout_seconds"],
            max_delay_seconds=configuration["max_delay_seconds"],
            max_rainfall_mm=configuration["max_rainfall_mm"],
            include_flagged_in_risk=False,
        )

        pipeline_output = output["pipeline_output"]

        sensor_statuses = pipeline_output["sensor_statuses"]

        sensor_health = assess_sensor_health(
            sensor_statuses,
            registered_sensor_ids,
            observations,
        )

    else:
        raise ValueError(
            f"Unknown workflow: {workflow_name}"
        )

    if len(output["records"]) != len(batch["records"]):
        raise RuntimeError(
            f"{workflow_name} returned an unexpected "
            f"record count for {batch['batch_id']}."
        )

    enriched_records = []

    for source, result in zip(
        batch["records"],
        output["records"],
    ):
        enriched_records.append({
            "record_id": source["record_id"],
            "ground_truth": source["ground_truth"],
            "workflow_result": result,
        })

    normalized_records = [
        {
            **item["workflow_result"],
            "record_id": item["record_id"],
            "ground_truth": item["ground_truth"],
        }
        for item in enriched_records
    ]

    return {
        "workflow": workflow_name,
        "batch_id": batch["batch_id"],
        "received_at": batch["received_at"],
        "metrics": count_workflow_results(normalized_records),
        "sensor_health": sensor_health,
        "sensor_statuses": sensor_statuses,
        "records": enriched_records,
    }


def run_scenario(scenario):
    """Execute all workflows against every batch in a scenario."""

    workflow_batches = {
        name: [] for name in WORKFLOW_NAMES
    }

    for batch in scenario["batches"]:

        for workflow_name in WORKFLOW_NAMES:

            result = run_one_workflow(
                workflow_name,
                batch,
                scenario["registered_sensor_ids"],
                scenario["configuration"],
            )

            workflow_batches[workflow_name].append(result)

    workflow_summaries = {}

    for workflow_name, batches in workflow_batches.items():

        all_records = [
            record
            for batch_result in batches
            for record in batch_result["records"]
        ]

        normalized = [
            {
                **item["workflow_result"],
                "record_id": item["record_id"],
                "ground_truth": item["ground_truth"],
            }
            for item in all_records
        ]

        workflow_summaries[workflow_name] = {
            "metrics": count_workflow_results(normalized),
            "sensor_health": (
                aggregate_sensor_health(batches)
                if workflow_name == "C_PROPOSED"
                else None
            ),
            "batch_count": len(batches),
            "batches": batches,
        }

    return {
        "scenario_id": scenario["scenario_id"],
        "degradation_type": scenario["degradation_type"],
        "severity": scenario["severity"],
        "injected_fault_count": scenario["injected_fault_count"],
        "expected_original_count": scenario["expected_original_count"],
        "observed_record_count": scenario["observed_record_count"],
        "workflows": workflow_summaries,
    }


def main():

    data = load_scenarios()
    results = []

    print("EXPERIMENT 2: COMPARATIVE DATA DEGRADATION")
    print("=" * 75)

    for scenario in data["scenarios"]:

        scenario_result = run_scenario(scenario)
        results.append(scenario_result)

        print(
            f"\n{scenario['scenario_id']}"
            f" | injected faults: "
            f"{scenario['injected_fault_count']}"
        )

        for workflow_name, workflow_result in (
            scenario_result["workflows"].items()
        ):

            metrics = workflow_result["metrics"]

            print(
                f"  {workflow_name:<16}"
                f" input={metrics['input_count']:<5}"
                f" forwarded={metrics['forwarded_count']:<5}"
                f" eligible={metrics['risk_eligible_count']:<5}"
                f" duplicates={metrics['duplicate_count']:<5}"
                f" delayed_flags={metrics['delayed_flag_count']}"
            )

        proposed_health = (
            scenario_result["workflows"]["C_PROPOSED"][
                "sensor_health"
            ]
        )

        if proposed_health is not None:

            print("  PROPOSED SENSOR HEALTH:")

            print(
                f"    Registered assessments: "
                f"{proposed_health['registered_sensor_assessments']}"
            )

            print(
                f"    ACTIVE: {proposed_health['active_count']}"
                f" | OVERDUE: {proposed_health['overdue_count']}"
                f" | NO_DATA: {proposed_health['no_data_count']}"
            )

            print(
                f"    Expected missing reports: "
                f"{proposed_health['expected_missing_sensor_reports']}"
            )

            print(
                f"    Correctly detected: "
                f"{proposed_health['correctly_detected_missing_sensor_reports']}"
            )

            print(
                f"    Missing observation: "
                f"{proposed_health['missing_observation_percentage']}%"
            )

            print(
                f"    Missing sensor detection rate: "
                f"{proposed_health['missing_sensor_detection_rate_percent']}"
            )

    output = {
        "experiment_id": "data-degradation-v1",
        "description": (
            "Comparative execution of unfiltered, rule-based "
            "and proposed workflows under controlled data "
            "degradation scenarios, including sensor-health "
            "monitoring evaluation."
        ),
        "scenario_count": len(results),
        "workflow_names": WORKFLOW_NAMES,
        "results": results,
    }

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(output, file, indent=2)

    print("\n" + "=" * 75)
    print(f"Scenarios executed: {len(results)}")
    print(f"Workflow executions: {len(results) * 3}")
    print(f"Raw results saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
