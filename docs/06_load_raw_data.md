# Lesson 6 — Load synthetic source data into Snowflake RAW

## Goal

Load the local, synthetic CSVs into source-shaped Snowflake tables using Python. This is an ingestion layer, not a dashboard layer: it adds `ingested_at` for lineage, but does not rename columns, remove duplicates, or define KPIs.

## 1. Create the landing tables

Open the existing SQL File in Snowsight and run [sql/03_create_raw_tables.sql](../sql/03_create_raw_tables.sql). It grants `CREATE STAGE` and `CREATE FILE FORMAT` only in `RAW`, then sets the intended development role, warehouse, database, and schema and creates six tables safely with `IF NOT EXISTS`. The scoped extra permissions are required because Snowflake's pandas loader creates temporary staging objects.

Expected result: `SHOW TABLES` lists `RAW_EMPLOYEES`, `RAW_TRIPS`, `RAW_BOOKING_EVENTS`, `RAW_EXPENSES`, `RAW_POLICY_EVALUATIONS`, and `RAW_SUPPORT_CASES`.

## 2. Run the Python loader

In PowerShell at the repository root:

```powershell
.\.venv\Scripts\python.exe .\src\travel_analytics\load_raw_to_snowflake.py --input-dir .\data\generated --replace
```

`--replace` truncates only the six known synthetic RAW tables before loading. It makes an intentional rerun idempotent. Never use this option against a real production raw-data table without an agreed retention strategy.

Expected output:

```text
RAW_EMPLOYEES: 250 rows loaded
RAW_TRIPS: 1200 rows loaded
RAW_BOOKING_EVENTS: 5808 rows loaded
RAW_EXPENSES: 930 rows loaded
RAW_POLICY_EVALUATIONS: 1200 rows loaded
RAW_SUPPORT_CASES: 157 rows loaded
```

## 3. Verify in Snowflake

Run this in Snowsight:

```sql
USE ROLE TRAVEL_ANALYTICS_DEV;
USE WAREHOUSE TRAVEL_ANALYTICS_XS;
USE DATABASE TRAVEL_ANALYTICS;
USE SCHEMA RAW;

SELECT 'raw_employees' AS table_name, COUNT(*) AS row_count FROM raw_employees
UNION ALL SELECT 'raw_trips', COUNT(*) FROM raw_trips
UNION ALL SELECT 'raw_booking_events', COUNT(*) FROM raw_booking_events
UNION ALL SELECT 'raw_expenses', COUNT(*) FROM raw_expenses
UNION ALL SELECT 'raw_policy_evaluations', COUNT(*) FROM raw_policy_evaluations
UNION ALL SELECT 'raw_support_cases', COUNT(*) FROM raw_support_cases
ORDER BY table_name;
```

## Debugging guide

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `Missing source files` | Generator has not run, or `--input-dir` is wrong | Regenerate to `data/generated`, then rerun. |
| `Object does not exist` | The DDL script was not run, or wrong database/schema is active | Run the table-creation script and check its `USE` statements. |
| `Insufficient privileges` | Python is connecting with the wrong role | Verify `.env` has `SNOWFLAKE_ROLE=TRAVEL_ANALYTICS_DEV`; rerun `dbt_debug.ps1`. |
| `Incorrect username or password` | `.env` and the local dbt user are out of sync | Reset only `TRAVEL_ANALYTICS_DBT`’s password, update `.env`, rerun the connection check. |
| Row count is double the expected count | Loader was rerun without `--replace` | Run again with `--replace` for these synthetic source snapshots. |
