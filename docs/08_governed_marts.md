# Lesson 8 — Build governed product and operations marts

## Goal

Create the tables that dashboards, self-service analytics, and the future MCP assistant can safely query. The rule is simple: every metric must be defined once in an analytics mart, not reimplemented independently in a dashboard.

## Model map

```text
STAGING (clean source grains)
      |
      +--> int_booking_funnel_sessions --> fct_booking_sessions --> mart_product_daily
      |
      +--> int_trip_enriched -----------> fct_trips -----------> mart_operations_daily
                                               |
                                               +--> fct_expenses
```

## Metric definitions

| Metric | Definition | Model |
| --- | --- | --- |
| Search-to-book conversion | booked sessions / search sessions | `mart_product_daily` |
| In-policy booking rate | in-policy trips / booked trips | `mart_operations_daily` |
| Out-of-policy spend | booked cost of policy-failing trips | `mart_operations_daily` |
| Support-contact rate | trips with ≥1 support case / booked trips | `mart_operations_daily` |
| Receipt capture rate | expense lines with receipt / all linked expense lines | `mart_operations_daily` |

## Build all models and tests

```powershell
.\scripts\run_dbt.ps1 -Operation build
```

Expected result: every model and test passes. The database will now contain `INTERMEDIATE` views and `ANALYTICS` tables.

## Validate two business questions in Snowsight

```sql
USE ROLE TRAVEL_ANALYTICS_DEV;
USE WAREHOUSE TRAVEL_ANALYTICS_XS;

SELECT *
FROM TRAVEL_ANALYTICS.ANALYTICS.MART_PRODUCT_DAILY
ORDER BY session_date DESC
LIMIT 7;

SELECT *
FROM TRAVEL_ANALYTICS.ANALYTICS.MART_OPERATIONS_DAILY
ORDER BY booking_date DESC
LIMIT 7;
```

## Interview talking point

If a dashboard claims a new conversion rate, ask: “What is the grain, numerator, denominator, and controlled filter?” This project answers those questions in versioned SQL and tested models before visualization.

## Debugging guide

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `Division by zero` / null rate | A date has no eligible denominator | The models use `nullif`; preserve that behavior and show a null rate rather than inventing zero. |
| KPI is duplicated | An event-level table was joined directly to a trip-level table | Aggregate to the intended grain in `INTERMEDIATE` before joining. |
| Relationship test fails | A source load is incomplete or a join key was altered | Trace the failing key through RAW → STAGING; do not disable the test. |
| A dashboard differs from the mart | Dashboard reimplements a metric | Point the dashboard to the governed mart and document the definition. |
