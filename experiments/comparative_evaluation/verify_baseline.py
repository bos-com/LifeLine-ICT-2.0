import json
from pathlib import Path
from collections import Counter

dataset_path = Path("data/controlled_dataset.json")
results_path = Path("results/raw/baseline_results.json")

dataset = json.loads(dataset_path.read_text(encoding="utf-8"))
results = json.loads(results_path.read_text(encoding="utf-8"))

ground_records = dataset["records"]
workflows = results["workflows"]

def expected_status(ground_truth):
    if ground_truth["is_invalid"]:
        return "REJECTED"

    if ground_truth["is_duplicate"]:
        return "DUPLICATE"

    if (
        ground_truth["is_delayed"]
        or ground_truth["is_suspicious"]
        or not ground_truth["is_registered"]
    ):
        return "FLAGGED"

    return "ACCEPTED"


overall_pass = True

print("BASELINE RECORD-LEVEL VERIFICATION")
print("=" * 55)
print(f"Dataset: {dataset['experiment_id']}")
print(f"Records: {len(ground_records)}")

for workflow_name in ("B_RULE_BASED", "C_PROPOSED"):
    workflow = workflows[workflow_name]
    actual_records = workflow["records"]

    print(f"\n{workflow_name}")
    print("-" * 55)

    workflow_pass = True

    if len(actual_records) != len(ground_records):
        print(
            f"FAIL: Expected {len(ground_records)} records, "
            f"found {len(actual_records)}"
        )
        workflow_pass = False

    for index, source in enumerate(ground_records):
        truth = source["ground_truth"]
        actual = actual_records[index]

        expected = expected_status(truth)
        actual_status = actual["status"]

        checks = {
            "status": actual_status == expected,
            "risk_eligible": (
                actual["risk_eligible"]
                == truth["expected_downstream_eligible"]
            ),
            "forwarded": (
                actual["forwarded"]
                == (expected not in ("REJECTED", "DUPLICATE"))
            ),
        }

        if expected == "DUPLICATE":
            checks["duplicate_reference"] = (
                actual["duplicate_of_index"] is not None
            )
        else:
            checks["duplicate_reference"] = (
                actual["duplicate_of_index"] is None
            )

        passed = all(checks.values())
        workflow_pass = workflow_pass and passed

        label = "PASS" if passed else "FAIL"
        print(
            f"{label} {source['record_id']}: "
            f"expected={expected}, actual={actual_status}, "
            f"checks={checks}"
        )

    counts = Counter(record["status"] for record in actual_records)

    expected_counts = {
        "ACCEPTED": 2,
        "FLAGGED": 3,
        "REJECTED": 5,
        "DUPLICATE": 1,
    }

    count_check = all(
        counts.get(status, 0) == expected_count
        for status, expected_count in expected_counts.items()
    )

    forwarded_count = sum(
        record["forwarded"] for record in actual_records
    )
    eligible_count = sum(
        record["risk_eligible"] for record in actual_records
    )

    summary_check = (
        count_check
        and forwarded_count == 5
        and eligible_count == 2
    )

    workflow_pass = workflow_pass and summary_check
    overall_pass = overall_pass and workflow_pass

    print("\nOutcome counts:", dict(counts))
    print("Forwarded:", forwarded_count)
    print("Downstream eligible:", eligible_count)
    print("Workflow verification:", "PASS" if workflow_pass else "FAIL")

print("\n" + "=" * 55)
print("OVERALL RESULT:", "PASS" if overall_pass else "FAIL")

if not overall_pass:
    raise SystemExit(1)
