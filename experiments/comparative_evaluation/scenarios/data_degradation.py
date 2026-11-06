
"""Generate controlled missing-data, delay and duplicate scenarios.

The original degradation_dataset.json is never modified.
Each generated scenario is independently reproducible.
"""

import copy
import json
import random
from pathlib import Path


# ---------------------------------------------------------
# Paths and configuration
# ---------------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = PROJECT_DIR / "data" / "degradation_dataset.json"

OUTPUT_FILE = (
    PROJECT_DIR / "data" / "degraded_scenarios.json"
)

RANDOM_SEED = 42

MISSING_LEVELS = [0.05, 0.10, 0.20, 0.40]
DELAY_MULTIPLIERS = [1, 2, 5]
DUPLICATE_LEVELS = [0.01, 0.05, 0.10]


def load_baseline():
    """Load and validate the original controlled dataset."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Baseline dataset not found: {INPUT_FILE}"
        )

    with INPUT_FILE.open("r", encoding="utf-8") as file:
        dataset = json.load(file)

    if dataset.get("experiment_id") != "data-degradation-v1":
        raise ValueError("Unexpected baseline experiment ID.")

    return dataset


def scenario_base(dataset, scenario_id, degradation_type, severity, seed):
    """Create common metadata for a scenario."""

    return {
        "scenario_id": scenario_id,
        "degradation_type": degradation_type,
        "severity": severity,
        "random_seed": seed,
        "registered_sensor_ids": dataset["registered_sensor_ids"],
        "configuration": dataset["configuration"],
        "expected_original_count": dataset[
            "expected_observation_count"
        ],
        "batches": [],
    }


def inject_missing(dataset, percentage, scenario_number):
    """Remove an exact percentage of observations from each batch."""

    seed = RANDOM_SEED + scenario_number
    rng = random.Random(seed)

    percentage_label = int(percentage * 100)

    scenario = scenario_base(
        dataset,
        f"missing_{percentage_label}pct",
        "MISSING_OBSERVATIONS",
        {"percentage": percentage},
        seed,
    )

    total_missing = 0
    missing_record_ids = []

    for original_batch in dataset["batches"]:

        batch = copy.deepcopy(original_batch)
        records = batch["records"]

        missing_count = round(len(records) * percentage)

        selected = rng.sample(
            records,
            missing_count
        )

        selected_ids = {
            record["record_id"]
            for record in selected
        }

        missing_record_ids.extend(selected_ids)

        batch["records"] = [
            record
            for record in records
            if record["record_id"] not in selected_ids
        ]

        batch["expected_record_count"] = len(records)
        batch["missing_record_count"] = missing_count

        total_missing += missing_count
        scenario["batches"].append(batch)

    scenario["injected_fault_count"] = total_missing
    scenario["observed_record_count"] = (
        scenario["expected_original_count"] - total_missing
    )
    scenario["missing_record_ids"] = sorted(missing_record_ids)

    return scenario


def inject_delays(dataset, multiplier, scenario_number):
    """Set every batch's ingestion time to the specified delay."""

    seed = RANDOM_SEED + scenario_number

    interval = dataset["configuration"][
        "reporting_interval_seconds"
    ]

    delay_seconds = multiplier * interval

    scenario = scenario_base(
        dataset,
        f"delayed_{multiplier}x",
        "DELAYED_OBSERVATIONS",
        {
            "multiplier": multiplier,
            "delay_seconds": delay_seconds,
        },
        seed,
    )

    total_delayed = 0

    from datetime import datetime, timedelta

    for original_batch in dataset["batches"]:

        batch = copy.deepcopy(original_batch)

        observed_at = datetime.fromisoformat(
            batch["expected_observed_at"]
        )

        received_at = observed_at + timedelta(
            seconds=delay_seconds
        )

        batch["received_at"] = received_at.isoformat()

        for record in batch["records"]:
            record["ground_truth"]["delayed"] = (
                delay_seconds > dataset["configuration"][
                    "max_delay_seconds"
                ]
            )
            record["ground_truth"]["delay_seconds"] = (
                delay_seconds
            )

            total_delayed += 1

        scenario["batches"].append(batch)

    scenario["injected_fault_count"] = total_delayed
    scenario["observed_record_count"] = total_delayed

    return scenario


def inject_duplicates(dataset, percentage, scenario_number):
    """Add exact duplicate transmissions to each batch."""

    seed = RANDOM_SEED + scenario_number
    rng = random.Random(seed)

    percentage_label = int(percentage * 100)

    scenario = scenario_base(
        dataset,
        f"duplicates_{percentage_label}pct",
        "DUPLICATE_TRANSMISSIONS",
        {"percentage": percentage},
        seed,
    )

    total_duplicates = 0

    for original_batch in dataset["batches"]:

        batch = copy.deepcopy(original_batch)
        original_records = batch["records"]

        duplicate_count = round(
            len(original_records) * percentage
        )

        selected = rng.sample(
            original_records,
            duplicate_count
        )

        duplicates = []

        for duplicate_number, original in enumerate(
            selected,
            start=1
        ):

            duplicate = copy.deepcopy(original)

            duplicate["record_id"] = (
                f"DUP-{original['record_id']}-"
                f"{duplicate_number:03d}"
            )

            duplicate["ground_truth"]["duplicate"] = True
            duplicate["ground_truth"]["original_record_id"] = (
                original["record_id"]
            )

            duplicates.append(duplicate)

        batch["records"].extend(duplicates)

        batch["original_record_count"] = len(original_records)
        batch["injected_duplicate_count"] = duplicate_count

        total_duplicates += duplicate_count
        scenario["batches"].append(batch)

    scenario["injected_fault_count"] = total_duplicates
    scenario["observed_record_count"] = (
        scenario["expected_original_count"] + total_duplicates
    )

    return scenario


def generate_scenarios():
    """Generate all ten controlled degradation scenarios."""

    dataset = load_baseline()

    scenarios = []
    scenario_number = 1

    for percentage in MISSING_LEVELS:
        scenarios.append(
            inject_missing(
                dataset,
                percentage,
                scenario_number
            )
        )
        scenario_number += 1

    for multiplier in DELAY_MULTIPLIERS:
        scenarios.append(
            inject_delays(
                dataset,
                multiplier,
                scenario_number
            )
        )
        scenario_number += 1

    for percentage in DUPLICATE_LEVELS:
        scenarios.append(
            inject_duplicates(
                dataset,
                percentage,
                scenario_number
            )
        )
        scenario_number += 1

    output = {
        "experiment_id": "data-degradation-v1",
        "description": (
            "Controlled scenarios for missing observations, "
            "delayed observations and duplicate transmissions."
        ),
        "baseline_file": str(INPUT_FILE.name),
        "scenario_count": len(scenarios),
        "scenarios": scenarios,
    }

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(output, file, indent=2)

    print("DATA DEGRADATION SCENARIOS GENERATED")
    print("=" * 55)

    for scenario in scenarios:
        print(
            f"{scenario['scenario_id']:<20}"
            f" faults={scenario['injected_fault_count']:<5}"
            f" observations={scenario['observed_record_count']}"
        )

    print("-" * 55)
    print(f"Total scenarios: {len(scenarios)}")
    print(f"Output file: {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_scenarios()
