"""Explainable threshold-based flood-risk baseline.

This module classifies rainfall indicators. It does not calculate a
validated flood probability or replace official flood warnings.
"""

from dataclasses import asdict, dataclass
from math import isfinite
from typing import Optional


@dataclass(frozen=True)
class FloodRiskResult:
    status: str
    risk_level: str
    daily_rainfall_mm: Optional[float]
    three_day_rainfall_mm: Optional[float]
    daily_threshold_exceeded: Optional[bool]
    three_day_threshold_exceeded: Optional[bool]
    quality_flags: tuple[str, ...]
    explanation: str

    def to_dict(self) -> dict:
        """Return a JSON-friendly representation of the result."""
        result = asdict(self)
        result["quality_flags"] = list(self.quality_flags)
        return result


def _validate_measurement(
    name: str,
    value: Optional[float],
) -> tuple[Optional[float], Optional[str]]:
    """Validate a non-negative, finite rainfall measurement."""
    if value is None:
        return None, f"MISSING_{name.upper()}"

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None, f"INVALID_{name.upper()}"

    numeric_value = float(value)

    if not isfinite(numeric_value) or numeric_value < 0:
        return None, f"INVALID_{name.upper()}"

    return numeric_value, None


def assess_flood_risk(
    daily_rainfall_mm: Optional[float],
    three_day_rainfall_mm: Optional[float],
    *,
    daily_threshold_mm: float = 25.0,
    three_day_threshold_mm: float = 60.0,
) -> FloodRiskResult:
    """Classify rainfall indicators using configurable thresholds.

    Both measurements must be present and valid for a risk classification.
    Exceeding one threshold produces MODERATE; exceeding both produces HIGH.
    Missing or invalid measurements produce UNKNOWN rather than LOW.

    Thresholds are configurable research defaults and require local validation.
    """
    for name, threshold in (
        ("daily_threshold_mm", daily_threshold_mm),
        ("three_day_threshold_mm", three_day_threshold_mm),
    ):
        if (
            isinstance(threshold, bool)
            or not isinstance(threshold, (int, float))
            or not isfinite(float(threshold))
            or threshold < 0
        ):
            raise ValueError(f"{name} must be a finite, non-negative number")

    daily, daily_issue = _validate_measurement(
        "daily_rainfall_mm", daily_rainfall_mm
    )
    three_day, three_day_issue = _validate_measurement(
        "three_day_rainfall_mm", three_day_rainfall_mm
    )

    flags = tuple(
        issue for issue in (daily_issue, three_day_issue) if issue is not None
    )

    if flags:
        return FloodRiskResult(
            status="INSUFFICIENT_DATA",
            risk_level="UNKNOWN",
            daily_rainfall_mm=daily,
            three_day_rainfall_mm=three_day,
            daily_threshold_exceeded=None if daily_issue else (
                daily > float(daily_threshold_mm)
            ),
            three_day_threshold_exceeded=None if three_day_issue else (
                three_day > float(three_day_threshold_mm)
            ),
            quality_flags=flags,
            explanation=(
                "Risk classification withheld because one or more rainfall "
                "measurements are missing or invalid."
            ),
        )

    daily_exceeded = daily > float(daily_threshold_mm)
    three_day_exceeded = three_day > float(three_day_threshold_mm)

    if daily_exceeded and three_day_exceeded:
        level = "HIGH"
        explanation = (
            "Both rainfall thresholds are exceeded. Further local validation "
            "and contextual information are required for operational decisions."
        )
    elif daily_exceeded or three_day_exceeded:
        level = "MODERATE"
        explanation = (
            "One rainfall threshold is exceeded. Review local conditions and "
            "other available indicators."
        )
    else:
        level = "LOW"
        explanation = (
            "Neither rainfall threshold is exceeded. This does not guarantee "
            "that flooding is absent."
        )

    return FloodRiskResult(
        status="VALID",
        risk_level=level,
        daily_rainfall_mm=daily,
        three_day_rainfall_mm=three_day,
        daily_threshold_exceeded=daily_exceeded,
        three_day_threshold_exceeded=three_day_exceeded,
        quality_flags=(),
        explanation=explanation,
    )
