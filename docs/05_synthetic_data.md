# Lesson 5 — Generate synthetic travel-product source data

## Goal

Create reproducible, fictional operational data before loading anything into Snowflake. This protects privacy and makes every later dbt test and dashboard demo repeatable.

## Why these tables

| File | Grain | Decision it supports |
| --- | --- | --- |
| `employees.csv` | one employee | Who is using the product? |
| `trips.csv` | one booked trip | What was booked, at what cost, and what happened? |
| `booking_events.csv` | one product event | Where do travelers abandon the booking funnel? |
| `expenses.csv` | one expense line | Are receipts and approvals complete? |
| `policy_evaluations.csv` | one trip-policy decision | What spend is out of policy? |
| `support_cases.csv` | one support case | Which journeys create operational friction? |

The generator deliberately includes abandoned booking sessions, policy failures, cancelled trips, missing receipts, and varied support channels. A dashboard with perfectly clean data tells no useful product or operations story.

## Run the automated test first

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_generate_synthetic_data.py -q -p no:cacheprovider
```

Expected output: `1 passed`.

The test checks the core data contract: unique trip IDs, one policy evaluation per trip, referential links from product events to trips, and a manifest that matches the files created.

## Generate the local source files

```powershell
.\.venv\Scripts\python.exe .\src\travel_analytics\generate_synthetic_data.py --output-dir .\data\generated
```

Expected output is a JSON object with file row counts. The default fixed seed and end date make reruns reproducible. The generated CSVs are ignored by Git because they are build artefacts, just like dbt's `target/` directory.

## Inspect one file without opening a spreadsheet

```powershell
Get-Content .\data\generated\trips.csv -TotalCount 4
Get-Content .\data\generated\manifest.json
```

## Debugging guide

| Symptom | Interpretation | Fix |
| --- | --- | --- |
| `ModuleNotFoundError: pandas` | Terminal did not use `.venv` | Use the full `.venv\\Scripts\\python.exe` command above. |
| `No module named src` when testing | Command was run outside the repository root | Run `Get-Location`, then `cd` to this project folder. |
| `PermissionError` below `AppData\\Local\\Temp\\pytest-*` | A Windows policy blocked pytest's default temporary directory | This test uses a fresh `test_runs/` workspace created by the developer's session, not pytest's default temporary folder. Use the documented command with `-p no:cacheprovider`. |
| Test failure about IDs | Generator changed its contract | Fix the source generator or test; do not remove the assertion. |
| Existing files unexpectedly changed | You used different seed/count/date arguments | Rerun with the documented defaults or document the new run parameters. |
