
"""Generate the controlled baseline dataset for Experiment 2."""

import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path


EXPERIMENT_ID = "data-degradation-v1"

NUMBER_OF_SENSORS = 100
REPORTING_ROUNDS = 10
REPORTING_INTERVAL_SECONDS = 300

# Keep sensor-health timeout separate from data-delivery delay threshold.
TIMEOUT_SECONDS = 900
MAX_DELAY_SECONDS = 900
MAX_RAINFALL_MM = 500

NORMAL_TRANSMISSION_DELAY_SECONDS = 60
RANDOM_SEED = 42

START_TIME = datetime(2025, 1, 1, 0, 0, tzinfo=timezone.utc)

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = BASE_DIR / "degradation_dataset.json"


def generate_dataset():
    random.seed(RANDOM_SEED)

    registered_sensor_ids = [
        f"RAIN-{number:03d}"
        for number in range(1, NUMBER_OF_SENSORS + 1)
    ]

    batches = []
    record_number = 1

    for round_number in range(REPORTING_ROUNDS):
        observed_at = START_TIME + timedelta(
            seconds=round_number * REPORTING_INTERVAL_SECONDS
        )

        received_at = observed_at + timedelta(
            seconds=NORMAL_TRANSMISSION_DELAY_SECONDS
        )

        records = []

        for sensor_id in registered_sensor_ids:
            rainfall_mm = round(random.uniform(0, 40), 2)

            record = {
                "record_id": f"R{record_number:04d}",
                "observation": {
                    "sensor_id": sensor_id,
                    "rainfall_mm": rainfall_mm,
                    "observed_at": observed_at.isoformat(),
                },
                "ground_truth": {
                    "expected": True,
                    "valid": True,
                    "duplicate": False,
                    "delayed": False,
                    "missing": False,
                    "original_sensor_id": sensor_id,
                    "original_observed_at": observed_at.isoformat(),
                },
            }

            records.append(record)
            record_number += 1

        batches.append({
            "batch_id": f"BATCH-{round_number + 1:02d}",
            "expected_observed_at": observed_at.isoformat(),
            "received_at": received_at.isoformat(),
            "records": records,
        })

    dataset = {
        "experiment_id": EXPERIMENT_ID,
        "description": (
            "Controlled baseline observations from registered rainfall "
            "sensors for comparative data-degradation experiments."
        ),
        "random_seed": RANDOM_SEED,
        "configuration": {
            "number_of_sensors": NUMBER_OF_SENSORS,
            "reporting_rounds": REPORTING_ROUNDS,
            "reporting_interval_seconds": REPORTING_INTERVAL_SECONDS,
            "timeout_seconds": TIMEOUT_SECONDS,
            "max_delay_seconds": MAX_DELAY_SECONDS,
            "max_rainfall_mm": MAX_RAINFALL_MM,
            "normal_transmission_delay_seconds":
                NORMAL_TRANSMISSION_DELAY_SECONDS,
        },
        "registered_sensor_ids": registered_sensor_ids,
        "expected_observation_count": (
            NUMBER_OF_SENSORS * REPORTING_ROUNDS
        ),
        "batch_count": len(batches),
        "batches": batches,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(dataset, file, indent=2)

    print("BASELINE DATASET GENERATED")
    print("=" * 55)
    print(f"Experiment ID: {EXPERIMENT_ID}")
    print(f"Registered sensors: {NUMBER_OF_SENSORS}")
    print(f"Reporting rounds: {REPORTING_ROUNDS}")
    print(f"Expected observations: {record_number - 1}")
    print(f"Batches: {len(batches)}")
    print(f"Timeout threshold: {TIMEOUT_SECONDS} seconds")
    print(f"Maximum delay threshold: {MAX_DELAY_SECONDS} seconds")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    generate_dataset()
