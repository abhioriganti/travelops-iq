# Lesson 9 — Connect ThoughtSpot to governed Snowflake marts

## Goal

Give business users self-service analytics without exposing raw data or using a developer/admin identity. ThoughtSpot will connect live to the small, governed `ANALYTICS` schema through a dedicated read-only Snowflake user.

## 1. Start with the free trial

Create a ThoughtSpot free-trial account; do not add a card or purchase a plan for this portfolio project. ThoughtSpot currently documents a 30-day trial, and its pricing page also describes a Developer Edition with a free tier for eligible embedding projects. Read the current terms before relying on the longer option.

## 2. Create the least-privilege Snowflake reader

In Snowsight, open a SQL File and run [sql/04_create_thoughtspot_reader.sql](../sql/04_create_thoughtspot_reader.sql).

Before running it, replace only the password placeholder with a new, long, unique password for this service user. Do not reuse your Google, Snowflake administrator, or dbt password. Never take a screenshot that shows it.

The role receives only:

- `USAGE` on the `TRAVEL_ANALYTICS_XS` warehouse and `TRAVEL_ANALYTICS` database.
- `USAGE` and `SELECT` on `TRAVEL_ANALYTICS.ANALYTICS`.
- A future-table grant, so recreated dbt tables remain available to ThoughtSpot.

It receives no access to `RAW`, `STAGING`, or `INTERMEDIATE`.

## 3. Add a Snowflake connection in ThoughtSpot

After the ThoughtSpot trial is active, use **Admin → Data Connectors → Snowflake**. UI labels can vary by edition.

Use these values, without sharing them in chat:

| ThoughtSpot field | Value |
| --- | --- |
| Account / server URL | Snowflake Account/Server URL from Account Details |
| User | `TRAVEL_ANALYTICS_THOUGHTSPOT` |
| Password | The new reader-user password |
| Role | `TRAVEL_ANALYTICS_BI` |
| Warehouse | `TRAVEL_ANALYTICS_XS` |
| Database | `TRAVEL_ANALYTICS` |

Select only the `ANALYTICS` schema and these models:

- `DIM_EMPLOYEE`
- `FCT_TRIPS`
- `FCT_BOOKING_SESSIONS`
- `FCT_EXPENSES`
- `MART_PRODUCT_DAILY`
- `MART_OPERATIONS_DAILY`

## 4. First self-service questions

After creating the connection and worksheet, answer these before building a Liveboard:

1. What is the daily search-to-book conversion trend?
2. What share of daily booked trips is in policy?
3. Which departments have the highest support-contact rate?
4. Which policy rule drives the highest out-of-policy spend?

## Debugging guide

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Connection authentication fails | Username/password do not match the dedicated reader | Reset only `TRAVEL_ANALYTICS_THOUGHTSPOT` password, then update the connector. |
| ThoughtSpot cannot see tables | Wrong role/schema, or tables were not selected during connection setup | Confirm role is `TRAVEL_ANALYTICS_BI` and schema is exactly `ANALYTICS`. |
| Raw tables appear | Too-broad role grants | Stop; review grants with `SHOW GRANTS TO ROLE TRAVEL_ANALYTICS_BI`. |
| Tables disappear after a dbt rebuild | Missing future-table grant | Rerun the `GRANT SELECT ON FUTURE TABLES` statement. |
| Queries burn credits while idle | Warehouse is left running | Verify `TRAVEL_ANALYTICS_XS` retains 60-second auto-suspend. |
