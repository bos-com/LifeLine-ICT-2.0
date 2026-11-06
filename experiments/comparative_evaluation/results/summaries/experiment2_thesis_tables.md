# Experiment 2: Independent Verification and Results

This report presents independently recalculated results for the controlled data-degradation experiment. The baseline schedule and experimental ground truth are used as verification references.

**Interpretation note:** Missing-observation completeness uses unique expected sensor-time observations. Duplicate transmissions are not counted as additional unique observations.

## Table 1. Scenario completeness and degradation profile

| scenario | degradation_type | severity | expected_observations | received_records_including_duplicates | unique_observations_received | missing_unique_observations | completeness_percent | injected_duplicate_records | ground_truth_delayed_records |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| missing_5pct | MISSING_OBSERVATIONS | {'percentage': 0.05} | 1000 | 950 | 950 | 50 | 95.0 | 0 | 0 |
| missing_10pct | MISSING_OBSERVATIONS | {'percentage': 0.1} | 1000 | 900 | 900 | 100 | 90.0 | 0 | 0 |
| missing_20pct | MISSING_OBSERVATIONS | {'percentage': 0.2} | 1000 | 800 | 800 | 200 | 80.0 | 0 | 0 |
| missing_40pct | MISSING_OBSERVATIONS | {'percentage': 0.4} | 1000 | 600 | 600 | 400 | 60.0 | 0 | 0 |
| delayed_1x | DELAYED_OBSERVATIONS | {'multiplier': 1, 'delay_seconds': 300} | 1000 | 1000 | 1000 | 0 | 100.0 | 0 | 0 |
| delayed_2x | DELAYED_OBSERVATIONS | {'multiplier': 2, 'delay_seconds': 600} | 1000 | 1000 | 1000 | 0 | 100.0 | 0 | 0 |
| delayed_5x | DELAYED_OBSERVATIONS | {'multiplier': 5, 'delay_seconds': 1500} | 1000 | 1000 | 1000 | 0 | 100.0 | 0 | 1000 |
| duplicates_1pct | DUPLICATE_TRANSMISSIONS | {'percentage': 0.01} | 1000 | 1010 | 1000 | 0 | 100.0 | 10 | 0 |
| duplicates_5pct | DUPLICATE_TRANSMISSIONS | {'percentage': 0.05} | 1000 | 1050 | 1000 | 0 | 100.0 | 50 | 0 |
| duplicates_10pct | DUPLICATE_TRANSMISSIONS | {'percentage': 0.1} | 1000 | 1100 | 1000 | 0 | 100.0 | 100 | 0 |

## Table 2. Comparative workflow performance

| scenario | workflow | input_records | forwarded_records | risk_eligible_records | unique_forwarded_observations | expected_delayed_records | delayed_true_positives | delayed_false_positives | delayed_false_negatives | delay_precision | delay_recall | expected_duplicate_records | duplicates_suppressed_correctly | false_duplicate_classifications | duplicate_suppression_recall |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| missing_5pct | A_UNFILTERED | 950 | 950 | 950 | 950 | 0 | 0 | 0 | 0 |  |  | 0 | 0 | 0 |  |
| missing_5pct | B_RULE_BASED | 950 | 950 | 950 | 950 | 0 | 0 | 0 | 0 |  |  | 0 | 0 | 0 |  |
| missing_5pct | C_PROPOSED | 950 | 950 | 950 | 950 | 0 | 0 | 0 | 0 |  |  | 0 | 0 | 0 |  |
| missing_10pct | A_UNFILTERED | 900 | 900 | 900 | 900 | 0 | 0 | 0 | 0 |  |  | 0 | 0 | 0 |  |
| missing_10pct | B_RULE_BASED | 900 | 900 | 900 | 900 | 0 | 0 | 0 | 0 |  |  | 0 | 0 | 0 |  |
| missing_10pct | C_PROPOSED | 900 | 900 | 900 | 900 | 0 | 0 | 0 | 0 |  |  | 0 | 0 | 0 |  |
| missing_20pct | A_UNFILTERED | 800 | 800 | 800 | 800 | 0 | 0 | 0 | 0 |  |  | 0 | 0 | 0 |  |
| missing_20pct | B_RULE_BASED | 800 | 800 | 800 | 800 | 0 | 0 | 0 | 0 |  |  | 0 | 0 | 0 |  |
| missing_20pct | C_PROPOSED | 800 | 800 | 800 | 800 | 0 | 0 | 0 | 0 |  |  | 0 | 0 | 0 |  |
| missing_40pct | A_UNFILTERED | 600 | 600 | 600 | 600 | 0 | 0 | 0 | 0 |  |  | 0 | 0 | 0 |  |
| missing_40pct | B_RULE_BASED | 600 | 600 | 600 | 600 | 0 | 0 | 0 | 0 |  |  | 0 | 0 | 0 |  |
| missing_40pct | C_PROPOSED | 600 | 600 | 600 | 600 | 0 | 0 | 0 | 0 |  |  | 0 | 0 | 0 |  |
| delayed_1x | A_UNFILTERED | 1000 | 1000 | 1000 | 1000 | 0 | 0 | 0 | 0 |  |  | 0 | 0 | 0 |  |
| delayed_1x | B_RULE_BASED | 1000 | 1000 | 1000 | 1000 | 0 | 0 | 0 | 0 |  |  | 0 | 0 | 0 |  |
| delayed_1x | C_PROPOSED | 1000 | 1000 | 1000 | 1000 | 0 | 0 | 0 | 0 |  |  | 0 | 0 | 0 |  |
| delayed_2x | A_UNFILTERED | 1000 | 1000 | 1000 | 1000 | 0 | 0 | 0 | 0 |  |  | 0 | 0 | 0 |  |
| delayed_2x | B_RULE_BASED | 1000 | 1000 | 1000 | 1000 | 0 | 0 | 0 | 0 |  |  | 0 | 0 | 0 |  |
| delayed_2x | C_PROPOSED | 1000 | 1000 | 1000 | 1000 | 0 | 0 | 0 | 0 |  |  | 0 | 0 | 0 |  |
| delayed_5x | A_UNFILTERED | 1000 | 1000 | 1000 | 1000 | 1000 | 0 | 0 | 1000 |  | 0.0 | 0 | 0 | 0 |  |
| delayed_5x | B_RULE_BASED | 1000 | 1000 | 0 | 1000 | 1000 | 1000 | 0 | 0 | 1.0 | 1.0 | 0 | 0 | 0 |  |
| delayed_5x | C_PROPOSED | 1000 | 1000 | 0 | 1000 | 1000 | 1000 | 0 | 0 | 1.0 | 1.0 | 0 | 0 | 0 |  |
| duplicates_1pct | A_UNFILTERED | 1010 | 1010 | 1010 | 1000 | 0 | 0 | 0 | 0 |  |  | 10 | 0 | 0 | 0.0 |
| duplicates_1pct | B_RULE_BASED | 1010 | 1000 | 1000 | 1000 | 0 | 0 | 0 | 0 |  |  | 10 | 10 | 0 | 1.0 |
| duplicates_1pct | C_PROPOSED | 1010 | 1000 | 1000 | 1000 | 0 | 0 | 0 | 0 |  |  | 10 | 10 | 0 | 1.0 |
| duplicates_5pct | A_UNFILTERED | 1050 | 1050 | 1050 | 1000 | 0 | 0 | 0 | 0 |  |  | 50 | 0 | 0 | 0.0 |
| duplicates_5pct | B_RULE_BASED | 1050 | 1000 | 1000 | 1000 | 0 | 0 | 0 | 0 |  |  | 50 | 50 | 0 | 1.0 |
| duplicates_5pct | C_PROPOSED | 1050 | 1000 | 1000 | 1000 | 0 | 0 | 0 | 0 |  |  | 50 | 50 | 0 | 1.0 |
| duplicates_10pct | A_UNFILTERED | 1100 | 1100 | 1100 | 1000 | 0 | 0 | 0 | 0 |  |  | 100 | 0 | 0 | 0.0 |
| duplicates_10pct | B_RULE_BASED | 1100 | 1000 | 1000 | 1000 | 0 | 0 | 0 | 0 |  |  | 100 | 100 | 0 | 1.0 |
| duplicates_10pct | C_PROPOSED | 1100 | 1000 | 1000 | 1000 | 0 | 0 | 0 | 0 |  |  | 100 | 100 | 0 | 1.0 |

## Table 3. Proposed workflow sensor-health assessment

| scenario | registered_sensor_assessments | active | overdue | no_data | expected_missing_reports | correctly_detected_missing_reports | false_positive_no_data | false_negative_no_data | missing_observation_percent | detection_rate_percent |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| missing_5pct | 1000 | 950 | 0 | 50 | 50 | 50 | 0 | 0 | 5.0 | 100.0 |
| missing_10pct | 1000 | 900 | 0 | 100 | 100 | 100 | 0 | 0 | 10.0 | 100.0 |
| missing_20pct | 1000 | 800 | 0 | 200 | 200 | 200 | 0 | 0 | 20.0 | 100.0 |
| missing_40pct | 1000 | 600 | 0 | 400 | 400 | 400 | 0 | 0 | 40.0 | 100.0 |
| delayed_1x | 1000 | 1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0.0 |  |
| delayed_2x | 1000 | 1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0.0 |  |
| delayed_5x | 1000 | 1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0.0 |  |
| duplicates_1pct | 1000 | 1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0.0 |  |
| duplicates_5pct | 1000 | 1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0.0 |  |
| duplicates_10pct | 1000 | 1000 | 0 | 0 | 0 | 0 | 0 | 0 | 0.0 |  |

## Verification outcome

The JSON verification report contains the individual verification checks, their outcomes and failure details. Only verified findings should be used as final research claims.
