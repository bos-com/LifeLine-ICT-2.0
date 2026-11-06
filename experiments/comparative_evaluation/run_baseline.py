"""Run the deterministic three-workflow comparative baseline."""

import json
from datetime import datetime
from pathlib import Path

from workflows.unfiltered import run_unfiltered
from workflows.rule_based import run_rule_based
from workflows.proposed import run_proposed


ROOT = Path(__file__).parent
DATASET_PATH = ROOT / "data" / "controlled_dataset.json"
OUTPUT_PATH = ROOT / "results" / "raw" / "baseline_results.json"


def main():
    with DATASET_PATH.open(encoding="utf-8") as file:
        dataset = json.load(file)

    observations = [
        item["observation"] for item in dataset["records"]
    ]

    received_at = datetime.fromisoformat(dataset["received_at"])
    registered_ids = dataset["registered_sensor_ids"]
    config = dataset["config"]

    workflows = {
        "A_UNFILTERED": run_unfiltered(observations),

        "B_RULE_BASED": run_rule_based(
            observations,
            registered_ids,
            received_at=received_at,
            max_delay_seconds=config["max_delay_seconds"],
            max_rainfall_mm=config["max_rainfall_mm"],
        ),

        "C_PROPOSED": run_proposed(
            observations,
            registered_ids,
            received_at=received_at,
            timeout_seconds=config["timeout_seconds"],
            max_delay_seconds=config["max_delay_seconds"],
            max_rainfall_mm=config["max_rainfall_mm"],
            include_flagged_in_risk=config["include_flagged_in_risk"],
        ),
    }

    output = {
        "experiment_id": dataset["experiment_id"],
        "dataset": str(DATASET_PATH.name),
        "workflows": workflows,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(output, file, indent=2)

    print("Comparative baseline completed.")
    print(f"Input observations: {len(observations)}")

    for name, result in workflows.items():
        print(f"\n{name}")
        print(f"  Forwarded: {result['forwarded_count']}")

        for status in (
            "UNFILTERED", "ACCEPTED", "FLAGGED",
            "REJECTED", "DUPLICATE"
        ):
            count = sum(
                record["status"] == status
                for record in result["records"]
            )
            if count:
                print(f"  {status}: {count}")

        print(
            "  Downstream eligible:",
            sum(
                record["risk_eligible"]
                for record in result["records"]
            ),
        )

    print(f"\nRaw results saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
