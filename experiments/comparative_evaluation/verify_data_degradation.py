
"""Independently verify Experiment 2 and generate thesis-ready tables.

Inputs:
    data/degradation_dataset.json
    data/degraded_scenarios.json
    results/raw/data_degradation_results.json

Outputs:
    results/summaries/experiment2_verification_report.json
    results/summaries/experiment2_scenario_summary.csv
    results/summaries/experiment2_workflow_comparison.csv
    results/summaries/experiment2_sensor_health.csv
    results/summaries/experiment2_thesis_tables.md

This program does not modify experimental input files or workflow results.
"""

import csv
import json
import sys
from collections import Counter
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

BASELINE_FILE = BASE_DIR / "data" / "degradation_dataset.json"
SCENARIOS_FILE = BASE_DIR / "data" / "degraded_scenarios.json"
RESULTS_FILE = (
    BASE_DIR / "results" / "raw" / "data_degradation_results.json"
)

OUTPUT_DIR = BASE_DIR / "results" / "summaries"

WORKFLOW_NAMES = [
    "A_UNFILTERED",
    "B_RULE_BASED",
    "C_PROPOSED",
]


def load_json(path):
    """Load a JSON file or stop with a useful error."""

    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def observation_key(observation):
    """Identify an observation by sensor and observation timestamp."""

    return (
        observation.get("sensor_id"),
        observation.get("observed_at"),
    )


def ground_truth_key(ground_truth):
    """Recover the original observation identity, including duplicates."""

    return (
        ground_truth.get("original_sensor_id"),
        ground_truth.get("original_observed_at"),
    )


def percentage(numerator, denominator):
    if denominator == 0:
        return None
    return round(numerator / denominator * 100, 2)


def ratio(numerator, denominator):
    if denominator == 0:
        return None
    return round(numerator / denominator, 4)


def write_csv(path, rows):
    """Write a CSV file with stable column ordering."""

    if not rows:
        path.write_text("", encoding="utf-8")
        return

    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(rows[0].keys()),
        )
        writer.writeheader()
        writer.writerows(rows)


def write_markdown_table(file, title, rows):
    """Write a Markdown table from dictionaries."""

    file.write(f"\n## {title}\n\n")

    if not rows:
        file.write("No applicable results.\n")
        return

    headers = list(rows[0].keys())

    file.write("| " + " | ".join(headers) + " |\n")
    file.write("| " + " | ".join(["---"] * len(headers)) + " |\n")

    for row in rows:
        values = [
            "" if row[header] is None else str(row[header])
            for header in headers
        ]
        file.write("| " + " | ".join(values) + " |\n")


def expected_record_outcome(workflow_name, ground_truth):
    """Derive expected workflow behaviour from the experiment design."""

    is_duplicate = ground_truth.get("duplicate", False)
    is_delayed = ground_truth.get("delayed", False)

    if workflow_name == "A_UNFILTERED":
        return {
            "status": "UNFILTERED",
            "forwarded": True,
            "risk_eligible": True,
            "delayed_flag": False,
        }

    if is_duplicate:
        return {
            "status": "DUPLICATE",
            "forwarded": False,
            "risk_eligible": False,
            "delayed_flag": False,
        }

    if is_delayed:
        return {
            "status": "FLAGGED",
            "forwarded": True,
            "risk_eligible": False,
            "delayed_flag": True,
        }

    return {
        "status": "ACCEPTED",
        "forwarded": True,
        "risk_eligible": True,
        "delayed_flag": False,
    }


def calculate_record_metrics(records):
    """Recalculate record-level metrics from saved individual results."""

    status_counts = Counter()
    forwarded_count = 0
    eligible_count = 0
    delayed_flag_count = 0
    duplicate_count = 0

    for item in records:
        result = item["workflow_result"]

        status_counts[result["status"]] += 1
        forwarded_count += bool(result["forwarded"])
        eligible_count += bool(result["risk_eligible"])

        flags = result.get("quality_flags", [])

        delayed_flag_count += (
            "DELAYED_OBSERVATION" in flags
        )

        duplicate_count += (
            result["status"] == "DUPLICATE"
        )

    return {
        "input_count": len(records),
        "status_counts": dict(sorted(status_counts.items())),
        "forwarded_count": forwarded_count,
        "risk_eligible_count": eligible_count,
        "flagged_count": status_counts.get("FLAGGED", 0),
        "rejected_count": status_counts.get("REJECTED", 0),
        "duplicate_count": duplicate_count,
        "delayed_flag_count": delayed_flag_count,
    }


def calculate_classification_metrics(records, target):
    """Calculate binary detection metrics for delay or duplicates."""

    true_positive = 0
    false_positive = 0
    false_negative = 0
    true_negative = 0

    for item in records:
        ground_truth = item["ground_truth"]
        result = item["workflow_result"]

        expected_positive = bool(ground_truth.get(target, False))

        if target == "delayed":
            predicted_positive = (
                "DELAYED_OBSERVATION"
                in result.get("quality_flags", [])
            )
        elif target == "duplicate":
            predicted_positive = result["status"] == "DUPLICATE"
        else:
            raise ValueError(f"Unsupported classification target: {target}")

        if expected_positive and predicted_positive:
            true_positive += 1
        elif not expected_positive and predicted_positive:
            false_positive += 1
        elif expected_positive and not predicted_positive:
            false_negative += 1
        else:
            true_negative += 1

    precision = ratio(
        true_positive,
        true_positive + false_positive,
    )

    recall = ratio(
        true_positive,
        true_positive + false_negative,
    )

    return {
        "true_positive": true_positive,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "true_negative": true_negative,
        "precision": precision,
        "recall": recall,
    }


def calculate_sensor_health(batch, registered_sensor_ids):
    """Independently verify one batch of proposed sensor statuses."""

    observations = [
        item["observation"]
        for item in batch["records"]
    ]

    registered = set(registered_sensor_ids)

    observed_sensor_ids = {
        observation.get("sensor_id")
        for observation in observations
        if observation.get("sensor_id") in registered
    }

    expected_missing = registered - observed_sensor_ids

    statuses = batch.get("sensor_statuses")

    if not isinstance(statuses, list):
        raise ValueError(
            f"Missing sensor-status list in {batch['batch_id']}."
        )

    status_ids = [item["sensor_id"] for item in statuses]

    if len(status_ids) != len(set(status_ids)):
        raise ValueError(
            f"Repeated sensor IDs in status output: {batch['batch_id']}."
        )

    if set(status_ids) != registered:
        raise ValueError(
            f"Registered sensor population mismatch: {batch['batch_id']}."
        )

    status_by_sensor = {
        item["sensor_id"]: item["status"]
        for item in statuses
    }

    status_counts = Counter(
        status_by_sensor.values()
    )

    correctly_detected = sum(
        status_by_sensor[sensor_id] == "NO_DATA"
        for sensor_id in expected_missing
    )

    false_positive = sum(
        status_by_sensor[sensor_id] == "NO_DATA"
        and sensor_id not in expected_missing
        for sensor_id in registered
    )

    false_negative = sum(
        status_by_sensor[sensor_id] != "NO_DATA"
        for sensor_id in expected_missing
    )

    unexpected_statuses = [
        sensor_id
        for sensor_id in registered
        if (
            sensor_id in expected_missing
            and status_by_sensor[sensor_id] != "NO_DATA"
        )
        or (
            sensor_id not in expected_missing
            and status_by_sensor[sensor_id] != "ACTIVE"
        )
    ]

    return {
        "registered_sensor_count": len(registered),
        "observed_sensor_count": len(observed_sensor_ids),
        "expected_missing_sensor_count": len(expected_missing),
        "missing_observation_percentage": percentage(
            len(expected_missing),
            len(registered),
        ),
        "status_counts": {
            "ACTIVE": status_counts.get("ACTIVE", 0),
            "OVERDUE": status_counts.get("OVERDUE", 0),
            "NO_DATA": status_counts.get("NO_DATA", 0),
        },
        "correctly_detected_missing_sensors": correctly_detected,
        "false_positive_no_data_count": false_positive,
        "false_negative_no_data_count": false_negative,
        "missing_sensor_detection_rate_percent": percentage(
            correctly_detected,
            len(expected_missing),
        ),
        "unexpected_sensor_status_count": len(unexpected_statuses),
    }


def aggregate_sensor_health(batch_results):
    """Recalculate aggregate sensor-health measurements."""

    registered = sum(
        item["registered_sensor_count"]
        for item in batch_results
    )

    expected_missing = sum(
        item["expected_missing_sensor_count"]
        for item in batch_results
    )

    detected = sum(
        item["correctly_detected_missing_sensors"]
        for item in batch_results
    )

    active = sum(
        item["status_counts"]["ACTIVE"]
        for item in batch_results
    )

    overdue = sum(
        item["status_counts"]["OVERDUE"]
        for item in batch_results
    )

    no_data = sum(
        item["status_counts"]["NO_DATA"]
        for item in batch_results
    )

    return {
        "batch_count": len(batch_results),
        "registered_sensor_assessments": registered,
        "active_count": active,
        "overdue_count": overdue,
        "no_data_count": no_data,
        "expected_missing_sensor_reports": expected_missing,
        "correctly_detected_missing_sensor_reports": detected,
        "false_positive_no_data_count": sum(
            item["false_positive_no_data_count"]
            for item in batch_results
        ),
        "false_negative_no_data_count": sum(
            item["false_negative_no_data_count"]
            for item in batch_results
        ),
        "missing_observation_percentage": percentage(
            expected_missing,
            registered,
        ),
        "missing_sensor_detection_rate_percent": percentage(
            detected,
            expected_missing,
        ),
    }


def main():
    baseline = load_json(BASELINE_FILE)
    scenarios_data = load_json(SCENARIOS_FILE)
    results_data = load_json(RESULTS_FILE)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    checks = []

    def add_check(name, passed, details):
        checks.append({
            "check": name,
            "passed": bool(passed),
            "details": details,
        })

    # ---------------------------------------------------------
    # 1. Validate experiment identity and baseline schedule.
    # ---------------------------------------------------------

    add_check(
        "baseline_experiment_id",
        baseline.get("experiment_id") == "data-degradation-v1",
        baseline.get("experiment_id"),
    )

    add_check(
        "scenario_experiment_id",
        scenarios_data.get("experiment_id") == "data-degradation-v1",
        scenarios_data.get("experiment_id"),
    )

    add_check(
        "results_experiment_id",
        results_data.get("experiment_id") == "data-degradation-v1",
        results_data.get("experiment_id"),
    )

    baseline_batches = baseline["batches"]

    expected_schedule = {
        observation_key(record["observation"])
        for batch in baseline_batches
        for record in batch["records"]
    }

    expected_observation_count = len(expected_schedule)

    add_check(
        "baseline_expected_observation_count",
        expected_observation_count == baseline["expected_observation_count"],
        {
            "actual_unique_schedule": expected_observation_count,
            "declared_expected_count": baseline["expected_observation_count"],
        },
    )

    registered_sensor_ids = baseline["registered_sensor_ids"]

    scenario_list = scenarios_data["scenarios"]
    result_list = results_data["results"]

    scenario_map = {
        item["scenario_id"]: item
        for item in scenario_list
    }

    result_map = {
        item["scenario_id"]: item
        for item in result_list
    }

    add_check(
        "scenario_count",
        len(scenario_list) == 10 and len(result_list) == 10,
        {
            "input_scenarios": len(scenario_list),
            "result_scenarios": len(result_list),
        },
    )

    add_check(
        "scenario_id_alignment",
        set(scenario_map) == set(result_map),
        {
            "missing_results": sorted(set(scenario_map) - set(result_map)),
            "unexpected_results": sorted(set(result_map) - set(scenario_map)),
        },
    )

    add_check(
        "workflow_names",
        results_data.get("workflow_names") == WORKFLOW_NAMES,
        results_data.get("workflow_names"),
    )

    scenario_table = []
    workflow_table = []
    sensor_table = []

    total_record_checks = 0
    total_record_failures = 0

    # ---------------------------------------------------------
    # 2. Verify every degradation scenario.
    # ---------------------------------------------------------

    for scenario_id, scenario in scenario_map.items():

        if scenario_id not in result_map:
            continue

        saved_scenario = result_map[scenario_id]

        source_batches = {
            batch["batch_id"]: batch
            for batch in scenario["batches"]
        }

        observed_records = [
            record
            for batch in scenario["batches"]
            for record in batch["records"]
        ]

        observed_keys = {
            observation_key(record["observation"])
            for record in observed_records
        }

        missing_keys = expected_schedule - observed_keys
        unexpected_keys = observed_keys - expected_schedule

        unique_observed_count = len(
            expected_schedule & observed_keys
        )

        completeness = percentage(
            unique_observed_count,
            expected_observation_count,
        )

        actual_duplicate_count = sum(
            bool(record["ground_truth"].get("duplicate", False))
            for record in observed_records
        )

        actual_delayed_count = sum(
            bool(record["ground_truth"].get("delayed", False))
            for record in observed_records
        )

        add_check(
            f"{scenario_id}:observed_record_count",
            len(observed_records) == scenario["observed_record_count"],
            {
                "actual": len(observed_records),
                "declared": scenario["observed_record_count"],
            },
        )

        add_check(
            f"{scenario_id}:unique_schedule_integrity",
            not unexpected_keys,
            {
                "unique_observations": unique_observed_count,
                "unexpected_observation_keys": len(unexpected_keys),
            },
        )

        add_check(
            f"{scenario_id}:missing_observation_count",
            len(missing_keys) == (
                expected_observation_count - unique_observed_count
            ),
            {
                "missing_unique_observations": len(missing_keys),
                "expected_schedule": expected_observation_count,
            },
        )

        scenario_table.append({
            "scenario": scenario_id,
            "degradation_type": scenario["degradation_type"],
            "severity": scenario["severity"],
            "expected_observations": expected_observation_count,
            "received_records_including_duplicates": len(observed_records),
            "unique_observations_received": unique_observed_count,
            "missing_unique_observations": len(missing_keys),
            "completeness_percent": completeness,
            "injected_duplicate_records": actual_duplicate_count,
            "ground_truth_delayed_records": actual_delayed_count,
        })

        workflow_results = saved_scenario.get("workflows", {})

        add_check(
            f"{scenario_id}:workflow_presence",
            set(workflow_results) == set(WORKFLOW_NAMES),
            sorted(workflow_results),
        )

        # -----------------------------------------------------
        # 3. Verify each workflow and its individual records.
        # -----------------------------------------------------

        for workflow_name in WORKFLOW_NAMES:

            if workflow_name not in workflow_results:
                continue

            workflow = workflow_results[workflow_name]

            result_batches = {
                batch["batch_id"]: batch
                for batch in workflow["batches"]
            }

            add_check(
                f"{scenario_id}:{workflow_name}:batch_alignment",
                set(result_batches) == set(source_batches),
                {
                    "expected_batches": len(source_batches),
                    "actual_batches": len(result_batches),
                },
            )

            all_records = []
            batch_sensor_health = []

            for batch_id, source_batch in source_batches.items():

                if batch_id not in result_batches:
                    continue

                result_batch = result_batches[batch_id]

                source_by_id = {
                    item["record_id"]: item
                    for item in source_batch["records"]
                }

                result_records = result_batch["records"]

                result_by_id = {
                    item["record_id"]: item
                    for item in result_records
                }

                batch_failures = []

                if set(source_by_id) != set(result_by_id):
                    batch_failures.append(
                        "Record IDs differ between input and result."
                    )

                for record_id in set(source_by_id) & set(result_by_id):

                    source_record = source_by_id[record_id]
                    result_record = result_by_id[record_id]

                    ground_truth = source_record["ground_truth"]
                    result_ground_truth = result_record["ground_truth"]
                    actual = result_record["workflow_result"]

                    total_record_checks += 1

                    if ground_truth != result_ground_truth:
                        batch_failures.append(
                            f"{record_id}: ground truth changed."
                        )

                    expected = expected_record_outcome(
                        workflow_name,
                        ground_truth,
                    )

                    if actual.get("status") != expected["status"]:
                        batch_failures.append(
                            f"{record_id}: incorrect status "
                            f"{actual.get('status')}."
                        )

                    if actual.get("forwarded") != expected["forwarded"]:
                        batch_failures.append(
                            f"{record_id}: incorrect forwarding decision."
                        )

                    if actual.get("risk_eligible") != expected["risk_eligible"]:
                        batch_failures.append(
                            f"{record_id}: incorrect risk eligibility."
                        )

                    actual_delayed_flag = (
                        "DELAYED_OBSERVATION"
                        in actual.get("quality_flags", [])
                    )

                    if actual_delayed_flag != expected["delayed_flag"]:
                        batch_failures.append(
                            f"{record_id}: incorrect delayed-observation flag."
                        )

                total_record_failures += len(batch_failures)

                add_check(
                    f"{scenario_id}:{workflow_name}:{batch_id}:record_behaviour",
                    not batch_failures,
                    {
                        "records_checked": len(
                            set(source_by_id) & set(result_by_id)
                        ),
                        "failures": batch_failures[:20],
                        "failure_count": len(batch_failures),
                    },
                )

                all_records.extend(result_records)

                # Verify sensor health for the proposed workflow only.
                if workflow_name == "C_PROPOSED":

                    try:
                        health = calculate_sensor_health(
                            {
                                **result_batch,
                                "records": source_batch["records"],
                            },
                            registered_sensor_ids,
                        )

                        batch_sensor_health.append(health)

                        stored_health = result_batch.get("sensor_health")

                        required_health_fields = [
                            "registered_sensor_count",
                            "observed_sensor_count",
                            "expected_missing_sensor_count",
                            "missing_observation_percentage",
                            "status_counts",
                            "correctly_detected_missing_sensors",
                            "false_positive_no_data_count",
                            "false_negative_no_data_count",
                            "missing_sensor_detection_rate_percent",
                        ]

                        health_matches = (
                            isinstance(stored_health, dict)
                            and all(
                                stored_health.get(field) == health.get(field)
                                for field in required_health_fields
                            )
                        )

                        add_check(
                            f"{scenario_id}:{batch_id}:sensor_health",
                            health_matches
                            and health["unexpected_sensor_status_count"] == 0,
                            {
                                "recalculated": health,
                                "stored": stored_health,
                            },
                        )

                    except (KeyError, TypeError, ValueError) as error:

                        add_check(
                            f"{scenario_id}:{batch_id}:sensor_health",
                            False,
                            str(error),
                        )

            # Recalculate aggregate workflow metrics.
            recalculated_metrics = calculate_record_metrics(all_records)
            stored_metrics = workflow.get("metrics", {})

            metrics_match = all(
                stored_metrics.get(key) == value
                for key, value in recalculated_metrics.items()
            )

            add_check(
                f"{scenario_id}:{workflow_name}:aggregate_metrics",
                metrics_match,
                {
                    "recalculated": recalculated_metrics,
                    "stored": stored_metrics,
                },
            )

            # Recalculate delay and duplicate detection.
            delay = calculate_classification_metrics(
                all_records,
                "delayed",
            )

            duplicates = calculate_classification_metrics(
                all_records,
                "duplicate",
            )

            forwarded_records = [
                item
                for item in all_records
                if item["workflow_result"]["forwarded"]
            ]

            unique_forwarded_keys = {
                ground_truth_key(item["ground_truth"])
                for item in forwarded_records
            }

            workflow_table.append({
                "scenario": scenario_id,
                "workflow": workflow_name,
                "input_records": recalculated_metrics["input_count"],
                "forwarded_records": recalculated_metrics["forwarded_count"],
                "risk_eligible_records": recalculated_metrics[
                    "risk_eligible_count"
                ],
                "unique_forwarded_observations": len(
                    unique_forwarded_keys
                ),
                "expected_delayed_records": (
                    delay["true_positive"] + delay["false_negative"]
                ),
                "delayed_true_positives": delay["true_positive"],
                "delayed_false_positives": delay["false_positive"],
                "delayed_false_negatives": delay["false_negative"],
                "delay_precision": delay["precision"],
                "delay_recall": delay["recall"],
                "expected_duplicate_records": (
                    duplicates["true_positive"]
                    + duplicates["false_negative"]
                ),
                "duplicates_suppressed_correctly": (
                    duplicates["true_positive"]
                ),
                "false_duplicate_classifications": (
                    duplicates["false_positive"]
                ),
                "duplicate_suppression_recall": (
                    duplicates["recall"]
                ),
            })

            # -------------------------------------------------
            # 4. Verify aggregate sensor-health results.
            # -------------------------------------------------

            if workflow_name == "C_PROPOSED":

                recalculated_health = aggregate_sensor_health(
                    batch_sensor_health
                )

                stored_health = workflow.get("sensor_health")

                health_fields = list(recalculated_health.keys())

                aggregate_matches = (
                    isinstance(stored_health, dict)
                    and all(
                        stored_health.get(field)
                        == recalculated_health.get(field)
                        for field in health_fields
                    )
                )

                add_check(
                    f"{scenario_id}:aggregate_sensor_health",
                    aggregate_matches,
                    {
                        "recalculated": recalculated_health,
                        "stored": stored_health,
                    },
                )

                sensor_table.append({
                    "scenario": scenario_id,
                    "registered_sensor_assessments": (
                        recalculated_health[
                            "registered_sensor_assessments"
                        ]
                    ),
                    "active": recalculated_health["active_count"],
                    "overdue": recalculated_health["overdue_count"],
                    "no_data": recalculated_health["no_data_count"],
                    "expected_missing_reports": (
                        recalculated_health[
                            "expected_missing_sensor_reports"
                        ]
                    ),
                    "correctly_detected_missing_reports": (
                        recalculated_health[
                            "correctly_detected_missing_sensor_reports"
                        ]
                    ),
                    "false_positive_no_data": (
                        recalculated_health[
                            "false_positive_no_data_count"
                        ]
                    ),
                    "false_negative_no_data": (
                        recalculated_health[
                            "false_negative_no_data_count"
                        ]
                    ),
                    "missing_observation_percent": (
                        recalculated_health[
                            "missing_observation_percentage"
                        ]
                    ),
                    "detection_rate_percent": (
                        recalculated_health[
                            "missing_sensor_detection_rate_percent"
                        ]
                    ),
                })

    # ---------------------------------------------------------
    # 5. Save thesis-ready CSV and Markdown tables.
    # ---------------------------------------------------------

    scenario_csv = OUTPUT_DIR / "experiment2_scenario_summary.csv"
    workflow_csv = OUTPUT_DIR / "experiment2_workflow_comparison.csv"
    sensor_csv = OUTPUT_DIR / "experiment2_sensor_health.csv"
    markdown_file = OUTPUT_DIR / "experiment2_thesis_tables.md"
    report_file = OUTPUT_DIR / "experiment2_verification_report.json"

    write_csv(scenario_csv, scenario_table)
    write_csv(workflow_csv, workflow_table)
    write_csv(sensor_csv, sensor_table)

    with markdown_file.open("w", encoding="utf-8") as file:

        file.write("# Experiment 2: Independent Verification and Results\n\n")

        file.write(
            "This report presents independently recalculated results "
            "for the controlled data-degradation experiment. "
            "The baseline schedule and experimental ground truth "
            "are used as verification references.\n"
        )

        file.write(
            "\n**Interpretation note:** Missing-observation completeness "
            "uses unique expected sensor-time observations. Duplicate "
            "transmissions are not counted as additional unique "
            "observations.\n"
        )

        write_markdown_table(
            file,
            "Table 1. Scenario completeness and degradation profile",
            scenario_table,
        )

        write_markdown_table(
            file,
            "Table 2. Comparative workflow performance",
            workflow_table,
        )

        write_markdown_table(
            file,
            "Table 3. Proposed workflow sensor-health assessment",
            sensor_table,
        )

        file.write(
            "\n## Verification outcome\n\n"
            "The JSON verification report contains the individual "
            "verification checks, their outcomes and failure details. "
            "Only verified findings should be used as final research "
            "claims.\n"
        )

    # ---------------------------------------------------------
    # 6. Produce an auditable verification report.
    # ---------------------------------------------------------

    passed_checks = sum(
        check["passed"] for check in checks
    )

    failed_checks = [
        check for check in checks
        if not check["passed"]
    ]

    verification_passed = len(failed_checks) == 0

    report = {
        "experiment_id": "data-degradation-v1",
        "verification_program": "verify_data_degradation.py",
        "verification_passed": verification_passed,
        "summary": {
            "total_checks": len(checks),
            "passed_checks": passed_checks,
            "failed_checks": len(failed_checks),
            "record_level_records_checked": total_record_checks,
            "record_level_failure_count": total_record_failures,
            "scenarios_checked": len(scenario_table),
            "workflow_comparisons": len(workflow_table),
            "sensor_health_scenario_assessments": len(sensor_table),
        },
        "checks": checks,
        "failed_check_details": failed_checks,
        "generated_files": [
            str(scenario_csv),
            str(workflow_csv),
            str(sensor_csv),
            str(markdown_file),
        ],
    }

    with report_file.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    # ---------------------------------------------------------
    # 7. Print concise verification summary.
    # ---------------------------------------------------------

    print("\nEXPERIMENT 2: INDEPENDENT VERIFICATION")
    print("=" * 75)

    print(f"Scenarios checked: {len(scenario_table)}")
    print(f"Workflow comparisons: {len(workflow_table)}")
    print(f"Record-level records checked: {total_record_checks}")
    print(f"Sensor-health scenario assessments: {len(sensor_table)}")

    print("\nVERIFICATION CHECKS")
    print("-" * 75)

    print(f"Total checks: {len(checks)}")
    print(f"Passed: {passed_checks}")
    print(f"Failed: {len(failed_checks)}")

    print(
        "\nOverall verification:",
        "PASSED" if verification_passed else "FAILED",
    )

    if failed_checks:
        print("\nFAILED CHECK DETAILS")

        for item in failed_checks[:20]:
            print(f"- {item['check']}: {item['details']}")

        if len(failed_checks) > 20:
            print(
                f"... and {len(failed_checks) - 20} additional failures."
            )

    print("\nGENERATED THESIS TABLES")
    print("-" * 75)

    print(scenario_csv)
    print(workflow_csv)
    print(sensor_csv)
    print(markdown_file)

    print("\nVERIFICATION REPORT")
    print(report_file)

    print("=" * 75)

    if not verification_passed:
        sys.exit(1)


if __name__ == "__main__":
    main()
