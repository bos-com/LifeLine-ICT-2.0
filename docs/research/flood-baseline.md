# Flood Intelligence Baseline

## Purpose

This document describes the initial explainable rainfall-threshold baseline
for the LifeLine-ICT-2.0 flood intelligence module.

The baseline is a research prototype for testing input validation, missing-data
handling, configurable thresholds and transparent risk classification. It is
not a validated flood-prediction model or an operational warning service.

## Inputs

- `daily_rainfall_mm`: daily rainfall in millimetres.
- `three_day_rainfall_mm`: cumulative rainfall over three days in millimetres.

Both measurements must be present, numeric, finite and non-negative for a
complete classification.

## Provisional thresholds

The initial defaults are:

- Daily rainfall threshold: 25 mm.
- Three-day cumulative rainfall threshold: 60 mm.

These defaults reflect thresholds used in earlier research work. They must be
validated against appropriate local rainfall observations, documented flood
events and the intended deployment environment before operational use.

Thresholds are configurable when calling `assess_flood_risk`.

## Classification rules

| Condition | Baseline classification |
|---|---|
| Neither threshold exceeded | LOW |
| Exactly one threshold exceeded | MODERATE |
| Both thresholds exceeded | HIGH |
| Any required measurement missing or invalid | UNKNOWN |

The implementation uses strict greater-than comparisons. A value equal to a
threshold does not count as exceeding it.

`UNKNOWN` is a data-quality outcome, not a low-risk classification. The
baseline retains quality flags to explain why classification was withheld.

## Resilience considerations

The initial implementation addresses missing and invalid rainfall inputs.
It does not yet implement sensor redundancy, sensor-drift detection,
imputation, offline buffering, synchronization, geospatial risk assessment,
or machine-learning prediction.

Those capabilities require separate implementation and testing.

## Validation plan

Validation should include:

1. Unit tests for threshold boundaries and classifications.
2. Missing and invalid input tests.
3. Tests using documented rainfall observations.
4. Evaluation against independently sourced flood-event labels.
5. Missing-data, sensor-failure, noise and delayed-data experiments.
6. Appropriate precision, recall, F1-score, false-alarm and missed-event
   reporting where labelled data support those measures.
7. Documentation of dataset sources, time periods, preprocessing and
   experimental limitations.

No predictive accuracy is claimed by this baseline document. Test results
must be recorded after the tests have actually been executed.
