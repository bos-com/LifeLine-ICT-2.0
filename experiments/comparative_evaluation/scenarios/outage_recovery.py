"""Controlled sensor outage and recovery experiment.

Uses the production sensor-monitoring component.
The simulation harness supplies the reporting timeline and polling.
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from ai.common.monitoring.sensor_monitor import assess_sensor_status


# ---------------------------------------------------------
# Experiment configuration
# ---------------------------------------------------------

SENSOR_ID = "RAIN-01"

REPORT_INTERVAL_SECONDS = 300       # 5 minutes
TIMEOUT_SECONDS = 900               # 15 minutes
POLL_INTERVAL_SECONDS = 60          # 1 minute

START = datetime(2025, 1, 1, 0, 0, tzinfo=timezone.utc)
RECOVERY_REPORT_AT = START + timedelta(seconds=2430)  # 40 min 30 sec
SIMULATION_END = START + timedelta(minutes=50)

# The initial valid report is received at the start.
last_seen_at = START

# The timeout boundary is the point at which the sensor
# becomes overdue immediately after the boundary.
outage_threshold_crossed_at = START + timedelta(
    seconds=TIMEOUT_SECONDS
)

timeline = []
first_overdue_at = None
recovery_recognized_at = None
previous_status = None
recovery_report_applied = False


# ---------------------------------------------------------
# Simulate monitoring polls and a returning heartbeat
# ---------------------------------------------------------

poll_time = START

while poll_time <= SIMULATION_END:

    # Apply the returning valid heartbeat when it has arrived.
    # The next monitoring poll can then recognise recovery.
    if (
        not recovery_report_applied
        and poll_time >= RECOVERY_REPORT_AT
    ):
        last_seen_at = RECOVERY_REPORT_AT
        recovery_report_applied = True

    result = assess_sensor_status(
        SENSOR_ID,
        last_seen_at,
        now=poll_time,
        timeout_seconds=TIMEOUT_SECONDS,
    )

    status = result.status

    # Record status transitions, not every repeated poll.
    if status != previous_status:
        timeline.append({
            "checked_at": poll_time.isoformat(),
            "status": status,
            "seconds_since_last_seen": result.seconds_since_last_seen,
        })

    if status == "OVERDUE" and first_overdue_at is None:
        first_overdue_at = poll_time

    if (
        first_overdue_at is not None
        and recovery_report_applied
        and status == "ACTIVE"
        and recovery_recognized_at is None
    ):
        recovery_recognized_at = poll_time

    previous_status = status
    poll_time += timedelta(seconds=POLL_INTERVAL_SECONDS)


# ---------------------------------------------------------
# Calculate experiment metrics
# ---------------------------------------------------------

if first_overdue_at is None:
    raise RuntimeError("The experiment did not detect an overdue sensor.")

if recovery_recognized_at is None:
    raise RuntimeError("The experiment did not recognise sensor recovery.")

detection_delay = (
    first_overdue_at - outage_threshold_crossed_at
).total_seconds()

recovery_recognition_delay = (
    recovery_recognized_at - RECOVERY_REPORT_AT
).total_seconds()

time_from_timeout_boundary_to_recovery = (
    RECOVERY_REPORT_AT - outage_threshold_crossed_at
).total_seconds()


# ---------------------------------------------------------
# Save results
# ---------------------------------------------------------

output = {
    "experiment_id": "sensor-outage-recovery-v1",
    "workflow": "C_PROPOSED",
    "component": "ai.common.monitoring.sensor_monitor",
    "sensor_id": SENSOR_ID,
    "configuration": {
        "report_interval_seconds": REPORT_INTERVAL_SECONDS,
        "timeout_seconds": TIMEOUT_SECONDS,
        "poll_interval_seconds": POLL_INTERVAL_SECONDS,
        "recovery_report_at": RECOVERY_REPORT_AT.isoformat(),
    },
    "timeline": timeline,
    "metrics": {
        "first_overdue_at": first_overdue_at.isoformat(),
        "recovery_recognized_at": recovery_recognized_at.isoformat(),
        "outage_detection_delay_seconds": detection_delay,
        "recovery_recognition_delay_seconds": recovery_recognition_delay,
        "time_from_timeout_boundary_to_recovery_seconds": (
            time_from_timeout_boundary_to_recovery
        ),
    },
    "comparison": {
        "A_UNFILTERED": {
            "outage_detection": None,
            "recovery_recognition": None,
            "interpretation": "Not implemented in this workflow.",
        },
        "B_RULE_BASED": {
            "outage_detection": None,
            "recovery_recognition": None,
            "interpretation": "No integrated sensor-health monitoring.",
        },
        "C_PROPOSED": {
            "outage_detection": detection_delay,
            "recovery_recognition": recovery_recognition_delay,
            "interpretation": (
                "Measured using the production sensor-monitoring "
                "component and simulated polling timeline."
            ),
        },
    },
}

output_path = Path("results/raw/outage_recovery_results.json")
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(
    json.dumps(output, indent=2),
    encoding="utf-8",
)

print("SENSOR OUTAGE AND RECOVERY EXPERIMENT")
print("=" * 50)
print(f"Sensor: {SENSOR_ID}")
print(f"Reporting interval: {REPORT_INTERVAL_SECONDS} seconds")
print(f"Timeout: {TIMEOUT_SECONDS} seconds")
print(f"Polling interval: {POLL_INTERVAL_SECONDS} seconds")

print("\nStatus transitions:")
for event in timeline:
    print(
        f"  {event['checked_at']} | {event['status']} "
        f"| elapsed={event['seconds_since_last_seen']}"
    )

print("\nMeasured results:")
print(f"  Outage detection delay: {detection_delay:.0f} seconds")
print(
    "  Recovery recognition delay: "
    f"{recovery_recognition_delay:.0f} seconds"
)
print(
    "  Time from timeout boundary to recovery report: "
    f"{time_from_timeout_boundary_to_recovery:.0f} seconds"
)

print(f"\nResults saved to: {output_path}")
