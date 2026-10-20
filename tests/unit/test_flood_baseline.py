import pytest

from ai.hazards.flood.baseline import assess_flood_risk


def test_below_both_thresholds_is_low():
    result = assess_flood_risk(10.0, 30.0)

    assert result.status == "VALID"
    assert result.risk_level == "LOW"
    assert result.quality_flags == ()


def test_daily_threshold_exceeded_is_moderate():
    result = assess_flood_risk(30.0, 40.0)

    assert result.risk_level == "MODERATE"
    assert result.daily_threshold_exceeded is True
    assert result.three_day_threshold_exceeded is False


def test_three_day_threshold_exceeded_is_moderate():
    result = assess_flood_risk(10.0, 70.0)

    assert result.risk_level == "MODERATE"


def test_both_thresholds_exceeded_is_high():
    result = assess_flood_risk(30.0, 70.0)

    assert result.risk_level == "HIGH"


def test_missing_daily_rainfall_is_unknown():
    result = assess_flood_risk(None, 70.0)

    assert result.status == "INSUFFICIENT_DATA"
    assert result.risk_level == "UNKNOWN"
    assert "MISSING_DAILY_RAINFALL_MM" in result.quality_flags


def test_missing_three_day_rainfall_is_unknown():
    result = assess_flood_risk(30.0, None)

    assert result.risk_level == "UNKNOWN"
    assert "MISSING_THREE_DAY_RAINFALL_MM" in result.quality_flags


@pytest.mark.parametrize("value", [-1, float("inf"), float("nan"), "invalid"])
def test_invalid_daily_rainfall_is_flagged(value):
    result = assess_flood_risk(value, 20.0)

    assert result.status == "INSUFFICIENT_DATA"
    assert result.risk_level == "UNKNOWN"
    assert "INVALID_DAILY_RAINFALL_MM" in result.quality_flags


def test_zero_rainfall_is_valid():
    result = assess_flood_risk(0.0, 0.0)

    assert result.status == "VALID"
    assert result.risk_level == "LOW"


def test_thresholds_are_configurable():
    result = assess_flood_risk(
        20.0,
        40.0,
        daily_threshold_mm=15.0,
        three_day_threshold_mm=50.0,
    )

    assert result.risk_level == "MODERATE"


def test_negative_threshold_is_rejected():
    with pytest.raises(ValueError):
        assess_flood_risk(10.0, 20.0, daily_threshold_mm=-1.0)


def test_result_can_be_converted_to_dictionary():
    result = assess_flood_risk(None, 20.0)
    output = result.to_dict()

    assert output["risk_level"] == "UNKNOWN"
    assert isinstance(output["quality_flags"], list)
