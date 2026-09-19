# Live Hotel-Property Discovery

## Purpose and boundary

This optional enrichment demonstrates live external hotel-property discovery
with the Geoapify Places API. The job queries the `accommodation.hotel`
category within a 10 km radius of each destination city center present in the
synthetic-trip dataset, returning at most 50 properties per city.

`MART_DESTINATION_HOTEL_DISCOVERY.is_result_limit_reached` is true when a city
returned 50 records. Treat those rows as capped discovery samples, not complete
hotel counts for that destination.

It does not query or store hotel room availability, rates, room inventory,
booking data, guest data, payment data, or any TravelOpsIQ employee/trip
identifier. The result is a bounded property-discovery snapshot, not a
representation of complete hotel-market coverage.

## One-time setup

Add a Geoapify API key only to local `.env`:

```env
GEOAPIFY_API_KEY=your_key_here
```

The key is ignored by Git. Do not commit, paste, or screenshot it.

## Run the workflow

Run [`sql/08_create_hotel_properties_raw_table.sql`](../sql/08_create_hotel_properties_raw_table.sql)
in Snowflake as `TRAVEL_ANALYTICS_DEV`.

Then run from the project root:

```powershell
.\.venv\Scripts\python.exe -m src.travel_analytics.ingest_live_hotels --replace
.\scripts\run_dbt.ps1 -Operation build -Select "+mart_destination_hotel_discovery"
```

## Verify in Snowflake

```sql
select
    source,
    count(*) as property_count,
    count(distinct destination_city_code) as destination_count,
    max(retrieved_at) as latest_retrieved_at
from TRAVEL_ANALYTICS.RAW.RAW_HOTEL_PROPERTIES
group by 1;

select *
from TRAVEL_ANALYTICS.ANALYTICS.MART_DESTINATION_HOTEL_DISCOVERY
order by discovered_hotel_count desc, destination_city_code;
```

## Interview framing

Say: “I enriched an otherwise synthetic travel dataset with live hotel-property
discovery from Geoapify. I scoped the external request to approved city-center
coordinates, capped each result set, and modeled the output as property
discovery—not hotel inventory, availability, or pricing.”
