# Lesson 3 — Create the Snowflake development foundation

## Goal

Provision a small, cost-controlled warehouse and a separate development role for this portfolio project. We use `ACCOUNTADMIN` only for this one-time administrative step; dbt, Python, ThoughtSpot, and the MCP service will not use it.

## Do not create a Project or Notebook

Snowsight Projects and Notebooks are optional Snowflake-managed workspaces. They are useful for exploratory work, but would duplicate the local Git repository we are building. This project needs repeatable SQL, dbt, and Python code under version control instead.

Create a **SQL worksheet**. In the current Snowsight UI, use the `+` button near the top left and choose **SQL Worksheet** (the label may be `Worksheet` in some accounts). A notebook is not needed.

## Run the bootstrap script

1. Open [sql/01_bootstrap_snowflake.sql](../sql/01_bootstrap_snowflake.sql) locally.
2. Copy and run everything down to, but excluding, the commented `GRANT ROLE ... TO USER ...` line.
3. In the worksheet, run:

   ```sql
   SELECT CURRENT_USER() AS current_user;
   ```

4. Copy the returned username into the grant statement, then run it. The username is normally an unquoted identifier, for example:

   ```sql
   GRANT ROLE TRAVEL_ANALYTICS_DEV TO USER JANE_DOE;
   ```

5. Run the verification section using the new role.

## What each object means

| Object | Purpose | Cost/security choice |
| --- | --- | --- |
| `TRAVEL_ANALYTICS_XS` | Compute for loads and dbt transformations | X-Small, auto-suspends after 60 seconds. |
| `TRAVEL_ANALYTICS_DEV` | Human/development role | No account-wide administrative powers. |
| `RAW` | Source-shaped data from Python | No business metrics are defined here. |
| `STAGING` | Clean, typed dbt models | One canonical model per source. |
| `INTERMEDIATE` | Reusable joins and business rules | Prevents duplicating complex SQL in dashboards. |
| `ANALYTICS` | KPI marts and governed views | The only layer for ThoughtSpot/MCP. |
| `DBT_DEV` | Safe dbt default schema | Prevents accidental writes to a raw source schema. |

## Common errors and debugging

| Error | Cause | Fix |
| --- | --- | --- |
| `Insufficient privileges` | Current role is not `ACCOUNTADMIN` | In the role selector, choose `ACCOUNTADMIN`, then rerun only the failed statement. |
| `User does not exist` in `GRANT ROLE` | Username was guessed or quoted incorrectly | Use `SELECT CURRENT_USER()` and replace the placeholder exactly. |
| Warehouse stays running | Auto-suspend was omitted or changed | Run `ALTER WAREHOUSE TRAVEL_ANALYTICS_XS SET AUTO_SUSPEND = 60;`. |
| Object already exists | You safely reran the script | `IF NOT EXISTS` makes rerunning it safe; continue. |

## Completion evidence

Share a screenshot or redacted output of:

```sql
USE ROLE TRAVEL_ANALYTICS_DEV;
USE WAREHOUSE TRAVEL_ANALYTICS_XS;
SHOW SCHEMAS IN DATABASE TRAVEL_ANALYTICS;
```

Then we will configure `profiles.yml`, verify `dbt debug`, and generate the first synthetic source dataset.
