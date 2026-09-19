# Live weather enrichment

## Purpose

TravelOpsIQ keeps its booking, expense, policy, and support events fully
synthetic and deterministic. This optional integration adds public historical
weather observations for the synthetic trip destinations. It demonstrates an
external API ingestion pattern without using traveler, customer, or private
supplier data.

## Data contract

The Python job reads only distinct `destination_city_code` and `departure_date`
pairs from `RAW.RAW_TRIPS`. It sends an approved city coordinate and date range
to Open-Meteo; it does **not** send trip IDs, employee IDs, booking details, or
other internal data to the API.

The landing table is `RAW.RAW_WEATHER_OBSERVATIONS`:

- location and observation date
- maximum temperature, precipitation, wind speed, and weather code
- source label and UTC retrieval time

Only departure dates before Snowflake's `CURRENT_DATE()` are loaded. This makes
the source explicitly historical weather, not a forecast represented as an
observation.

## Run the landing-table DDL

In Snowsight, run [sql/06_create_weather_raw_table.sql](../sql/06_create_weather_raw_table.sql)
while using the `TRAVEL_ANALYTICS_DEV` role.

## Run the ingestion job

From PowerShell at the repository root:

```powershell
.\.venv\Scripts\python.exe .\src\travel_analytics\ingest_live_weather.py --replace
```

`--replace` truncates only `RAW_WEATHER_OBSERVATIONS` before loading a fresh
external-source snapshot. It does not touch any synthetic RAW source tables.

## Verify in Snowflake

```sql
USE ROLE TRAVEL_ANALYTICS_DEV;
USE WAREHOUSE TRAVEL_ANALYTICS_XS;
USE DATABASE TRAVEL_ANALYTICS;
USE SCHEMA RAW;

SELECT
    source,
    COUNT(*) AS observation_count,
    MIN(weather_date) AS first_weather_date,
    MAX(weather_date) AS last_weather_date,
    MAX(retrieved_at) AS latest_retrieved_at
FROM raw_weather_observations
GROUP BY source;
```

## Next transformation step

dbt will clean this source and join destination weather to trips by destination
city code and departure date. The derived mart will contain only aggregated
travel-risk metrics for ThoughtSpot and MCP use.
