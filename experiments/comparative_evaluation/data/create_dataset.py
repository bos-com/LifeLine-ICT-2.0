import json
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent

dataset = {
    "experiment_id": "controlled-baseline-v1",
    "description": (
        "Small deterministic synthetic dataset for comparative "
        "evaluation of three observation-ingestion workflows."
    ),
    "received_at": "2025-01-01T12:00:00+00:00",
    "registered_sensor_ids": ["RAIN-01", "RAIN-02"],
    "config": {
        "timeout_seconds": 900,
        "max_delay_seconds": 900,
        "max_rainfall_mm": 500,
        "include_flagged_in_risk": False
    },
    "records": [
        {
            "record_id": "R001",
            "observation": {
                "record_id": "R001",
                "sensor_id": "RAIN-01",
                "rainfall_mm": 12.0,
                "observed_at": "2025-01-01T11:50:00+00:00"
            },
            "ground_truth": {
                "is_invalid": False,
                "is_duplicate": False,
                "is_delayed": False,
                "is_suspicious": False,
                "is_registered": True,
                "expected_downstream_eligible": True
            }
        },
        {
            "record_id": "R002",
            "observation": {
                "record_id": "R002",
                "sensor_id": "RAIN-02",
                "rainfall_mm": 0.0,
                "observed_at": "2025-01-01T11:52:00+00:00"
            },
            "ground_truth": {
                "is_invalid": False,
                "is_duplicate": False,
                "is_delayed": False,
                "is_suspicious": False,
                "is_registered": True,
                "expected_downstream_eligible": True
            }
        },
        {
            "record_id": "R003",
            "observation": {
                "record_id": "R003",
                "sensor_id": "RAIN-01",
                "rainfall_mm": -5.0,
                "observed_at": "2025-01-01T11:54:00+00:00"
            },
            "ground_truth": {
                "is_invalid": True,
                "invalid_reason": "Negative rainfall",
                "is_duplicate": False,
                "is_delayed": False,
                "is_suspicious": False,
                "is_registered": True,
                "expected_downstream_eligible": False
            }
        },
        {
            "record_id": "R004",
            "observation": {
                "record_id": "R004",
                "sensor_id": "RAIN-02",
                "observed_at": "2025-01-01T11:55:00+00:00"
            },
            "ground_truth": {
                "is_invalid": True,
                "invalid_reason": "Missing rainfall measurement",
                "is_duplicate": False,
                "is_delayed": False,
                "is_suspicious": False,
                "is_registered": True,
                "expected_downstream_eligible": False
            }
        },
        {
            "record_id": "R005",
            "observation": {
                "record_id": "R005",
                "sensor_id": "RAIN-01",
                "rainfall_mm": 8.0,
                "observed_at": "not-a-timestamp"
            },
            "ground_truth": {
                "is_invalid": True,
                "invalid_reason": "Malformed timestamp",
                "is_duplicate": False,
                "is_delayed": False,
                "is_suspicious": False,
                "is_registered": True,
                "expected_downstream_eligible": False
            }
        },
        {
            "record_id": "R006",
            "observation": {
                "record_id": "R006",
                "sensor_id": "RAIN-02",
                "rainfall_mm": 7.0,
                "observed_at": "2025-01-01T12:05:00+00:00"
            },
            "ground_truth": {
                "is_invalid": True,
                "invalid_reason": "Future observation timestamp",
                "is_duplicate": False,
                "is_delayed": False,
                "is_suspicious": False,
                "is_registered": True,
                "expected_downstream_eligible": False
            }
        },
        {
            "record_id": "R007",
            "observation": {
                "record_id": "R007",
                "sensor_id": "RAIN-01",
                "rainfall_mm": 15.0,
                "observed_at": "2025-01-01T11:30:00+00:00"
            },
            "ground_truth": {
                "is_invalid": False,
                "is_duplicate": False,
                "is_delayed": True,
                "is_suspicious": False,
                "is_registered": True,
                "expected_downstream_eligible": False
            }
        },
        {
            "record_id": "R008",
            "observation": {
                "record_id": "R008",
                "sensor_id": "RAIN-01",
                "rainfall_mm": 12.0,
                "observed_at": "2025-01-01T11:50:00+00:00"
            },
            "ground_truth": {
                "is_invalid": False,
                "is_duplicate": True,
                "duplicate_of": "R001",
                "is_delayed": False,
                "is_suspicious": False,
                "is_registered": True,
                "expected_downstream_eligible": False
            }
        },
        {
            "record_id": "R009",
            "observation": {
                "record_id": "R009",
                "sensor_id": "RAIN-02",
                "rainfall_mm": 600.0,
                "observed_at": "2025-01-01T11:56:00+00:00"
            },
            "ground_truth": {
                "is_invalid": False,
                "is_duplicate": False,
                "is_delayed": False,
                "is_suspicious": True,
                "is_registered": True,
                "expected_downstream_eligible": False
            }
        },
        {
            "record_id": "R010",
            "observation": {
                "record_id": "R010",
                "sensor_id": "RAIN-99",
                "rainfall_mm": 4.0,
                "observed_at": "2025-01-01T11:57:00+00:00"
            },
            "ground_truth": {
                "is_invalid": False,
                "is_duplicate": False,
                "is_delayed": False,
                "is_suspicious": False,
                "is_registered": False,
                "expected_downstream_eligible": False
            }
        },
        {
            "record_id": "R011",
            "observation": "malformed-record",
            "ground_truth": {
                "is_invalid": True,
                "invalid_reason": "Observation is not a mapping",
                "is_duplicate": False,
                "is_delayed": False,
                "is_suspicious": False,
                "is_registered": False,
                "expected_downstream_eligible": False
            }
        }
    ]
}

output_path = OUTPUT_DIR / "controlled_dataset.json"

with output_path.open("w", encoding="utf-8") as file:
    json.dump(dataset, file, indent=2)

print(f"Dataset created: {output_path}")
print(f"Total records: {len(dataset['records'])}")
print(
    "Invalid records:",
    sum(r["ground_truth"]["is_invalid"] for r in dataset["records"])
)
print(
    "Duplicate records:",
    sum(r["ground_truth"]["is_duplicate"] for r in dataset["records"])
)
print(
    "Delayed records:",
    sum(r["ground_truth"]["is_delayed"] for r in dataset["records"])
)
print(
    "Expected downstream-eligible records:",
    sum(
        r["ground_truth"]["expected_downstream_eligible"]
        for r in dataset["records"]
    )
)
