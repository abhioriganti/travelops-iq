# Duffel Flight-Offer Sandbox

## Purpose and boundary

This optional integration demonstrates an authenticated external flight-offer
API ingestion pattern. It intentionally uses a Duffel **test** token and never
creates an order. Duffel test offers may come from its sandbox airline and do
not have realistic schedules or prices. They are integration-test data, not
live travel inventory or market-pricing evidence.

The flow sends only an anonymous route, departure date, cabin class, and one
adult passenger type. It never sends TravelOpsIQ employee, trip, booking,
expense, payment, or contact information to Duffel.

## One-time setup

1. Create a test token in Duffel Dashboard → Developers → Access tokens. The
   token needs **Read and Write** scope because submitting an anonymous offer
   request requires Duffel's `air.offer_requests.create` permission. This does
   not create a booking, collect a payment, or spend money in test mode.
2. Add it only to local `.env`:

   ```env
   DUFFEL_ACCESS_TOKEN=duffel_test_your_token_here
   ```

3. Do not commit or share the token. `.env` is ignored by Git.

## Run the snapshot

First run [`sql/07_create_flight_offer_raw_table.sql`](../sql/07_create_flight_offer_raw_table.sql)
in Snowflake as `TRAVEL_ANALYTICS_DEV`.

Then, from the project root:

```powershell
.\.venv\Scripts\python.exe -m src.travel_analytics.ingest_flight_offers --replace
.\scripts\run_dbt.ps1 -Operation build -Select "+mart_flight_offer_snapshot_summary"
```

The default route is LHR → JFK in economy, departing 30 days from the day you
run the command. Duffel requires a future date even in test mode. You can
provide another sandbox request without changing code:

```powershell
.\.venv\Scripts\python.exe -m src.travel_analytics.ingest_flight_offers `
  --origin LHR --destination JFK --departure-date 2026-10-20 --cabin-class economy --replace
```

## Verify in Snowflake

```sql
select
    environment,
    source,
    count(*) as offer_count,
    min(total_amount) as lowest_offer_amount,
    max(total_amount) as highest_offer_amount,
    max(retrieved_at) as latest_retrieved_at
from TRAVEL_ANALYTICS.RAW.RAW_FLIGHT_OFFER_SNAPSHOTS
group by 1, 2;

select *
from TRAVEL_ANALYTICS.ANALYTICS.MART_FLIGHT_OFFER_SNAPSHOT_SUMMARY
order by retrieved_at desc;
```

## Interview framing

Say: “I used Duffel's authenticated test environment to demonstrate a safe
flight-offer ingestion pattern. The pipeline is isolated from traveler data and
does not make bookings. The dashboard labels it as sandbox data because the
provider does not represent test prices or schedules as market-realistic.”
