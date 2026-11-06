"""Workflow A: unfiltered observation pass-through."""


def run_unfiltered(observations):
    """Forward every input record without validation or deduplication."""
    results = []

    for index, observation in enumerate(observations):
        results.append({
            "index": index,
            "status": "UNFILTERED",
            "risk_eligible": True,
            "forwarded": True,
            "quality_flags": [],
            "duplicate_of_index": None,
        })

    return {
        "workflow": "A_UNFILTERED",
        "records": results,
        "input_count": len(observations),
        "forwarded_count": len(results),
    }
