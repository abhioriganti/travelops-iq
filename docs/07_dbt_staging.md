# Lesson 7 — Build and test the dbt staging layer

## Goal

Turn raw source tables into clean, typed, documented, testable models. Staging models retain the source grain—one row per employee, trip, event, expense, policy decision, or support case—while normalizing types and controlled values.

## Why a staging layer exists

Do not let dashboards join `RAW` tables directly. In production, raw sources often have inconsistent casing, database-specific types, columns that change names, and data-quality defects. The staging models make those choices once, under version control, and downstream users rely on the cleaned interface.

The schema-routing macro makes models land in the existing `STAGING` schema. The macro is a deliberate teaching simplification; multi-environment production deployments commonly prefix schemas with the target name (for example, `DEV_STAGING`).

## Run dbt build

From the repository root:

```powershell
.\scripts\run_dbt.ps1 -Operation build -Select "source:raw path:models/staging"
```

Expected outcome: six staging views build in `TRAVEL_ANALYTICS.STAGING` and all source/model tests pass.

## Inspect the results

In Snowsight:

```sql
USE ROLE TRAVEL_ANALYTICS_DEV;
USE WAREHOUSE TRAVEL_ANALYTICS_XS;

SELECT trip_status, COUNT(*) AS trips
FROM TRAVEL_ANALYTICS.STAGING.STG_TRIPS
GROUP BY trip_status
ORDER BY trips DESC;
```

## Debugging guide

| Symptom | Cause | Fix |
| --- | --- | --- |
| `Object does not exist` for a RAW table | Loader was not run or the database/schema differs | Run the Lesson 6 loader and verify its output. |
| `Insufficient privileges` creating a view | dbt profile role is wrong | Verify `.env` contains `TRAVEL_ANALYTICS_DEV`; rerun `dbt_debug.ps1`. |
| dbt writes to `DBT_DEV_STAGING` | Schema naming macro is missing/not parsed | Confirm `dbt/macros/generate_schema_name.sql` exists, then rerun. |
| A uniqueness or relationship test fails | The source-data contract was broken | Inspect the failing IDs first; do not delete tests to make the build green. |
