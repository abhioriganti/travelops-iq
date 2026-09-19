# TravelOpsIQ

**Governed travel product and operations analytics, from raw events to
self-service insights and a read-only AI interface.**

TravelOpsIQ is an independent, end-to-end analytics engineering portfolio
project. It models a business-travel journey across booking, policy, spend,
expenses, and support, then makes trusted KPIs available through ThoughtSpot
and a constrained Model Context Protocol (MCP) service.

> Core travel, expense, policy, and support data is deterministic and
> synthetic. Separate enrichment flows retrieve public historical weather from
> Open-Meteo, live hotel-property discovery metadata from Geoapify Places, and
> anonymous flight offers from Duffel's test environment. The project contains
> no customer data, payment data, real bookings, or production third-party
> travel-platform access.

## What it demonstrates

- Python ingestion and deterministic synthetic-data generation
- Snowflake schema design and least-privilege service identities
- dbt staging, intermediate, fact, dimension, and daily mart models
- Automated data-quality tests and repeatable local validation
- ThoughtSpot semantic models and a six-chart operations Liveboard
- A local MCP server that exposes approved, parameterized aggregate queries
- Live public-weather ingestion, transparent risk classification, and a
  governed travel-risk mart
- Authenticated Duffel sandbox flight-offer ingestion with explicit test-data
  lineage and no booking workflow
- Live Geoapify hotel-property discovery with bounded destination searches and
  explicit non-inventory lineage
- GitHub Actions CI that runs Python tests and validates dbt parsing without
  using warehouse or API credentials
- A local scheduled-refresh command that sequences approved external loads
  before a full dbt build, while keeping credentials in ignored local config

## Continuous integration

Every pull request to `main` runs Python unit tests and `dbt parse` through
GitHub Actions. The workflow uses placeholder Snowflake values only to render
the example dbt profile; it does not query Snowflake, call external APIs, or
use repository secrets.

## Architecture

```mermaid
flowchart LR
    A[Python synthetic-data generator] --> B[Snowflake RAW]
    X[Open-Meteo historical API] --> W[Python weather ingestion]
    W --> B
    Z[Geoapify Places API] --> P[Python hotel-property ingestion]
    P --> B
    Y[Duffel test API] --> Q[Python flight-offer ingestion]
    Q --> B
    B --> C[dbt STAGING]
    C --> D[dbt INTERMEDIATE]
    D --> E[Snowflake ANALYTICS marts]
    E --> F[ThoughtSpot models and Liveboard]
    E --> G[Read-only MCP service]
    G --> H[Codex]
```

## Portfolio previews

### ThoughtSpot operations Liveboard

The **Travel Operations Command Center** makes trusted product and operations
KPIs available as self-service weekly trends.

![TravelOpsIQ ThoughtSpot operations Liveboard](docs/assets/travelopsiq-liveboard.png)

### Read-only MCP analytics interface

Codex discovers the local `travel_analytics` MCP server and invokes only its
approved product-funnel, operations-summary, and KPI-trend tools.

![TravelOpsIQ MCP product funnel demonstration](docs/assets/travelopsiq-mcp-demo.png)

## Key analytics outputs

The governed daily marts answer questions such as:

- Where does the booking funnel lose travelers?
- How do booking volume and conversion move over time?
- How much spend occurs outside policy?
- Which periods have elevated support-contact rates or resolution time?
- Which historical departure dates had meaningful destination-weather exposure?

The ThoughtSpot **Travel Operations Command Center** includes trends for booked
trips, in-policy booking rate, out-of-policy spend, search-to-book conversion,
checkout-to-book conversion, and booked-session volume.

## Live weather enrichment

The optional weather flow enriches synthetic trip destinations with public
historical observations from the [Open-Meteo Historical Weather
API](https://open-meteo.com/en/docs/historical-weather-api). It sends only
version-controlled city coordinates and date ranges to the API—never trip IDs,
employee IDs, booking details, or expense data.

`MART_TRAVEL_RISK_DAILY` provides daily aggregate metrics including
weather-impacted trip rate, high-risk trips, and booking value exposed to
medium/high weather conditions. Risk is a transparent portfolio proxy based on
weather severity, wind, and precipitation; it is not a claim of actual flight
disruption. See the [live-weather runbook](docs/12_live_weather_enrichment.md)
for the source contract and reproducible commands.

## Duffel flight-offer sandbox integration

The optional flight-offer flow authenticates to Duffel using a local
`duffel_test_` token, submits a minimal anonymous search, and lands the
returned offers in `RAW_FLIGHT_OFFER_SNAPSHOTS`. It sends only origin,
destination, departure date, cabin, and one adult passenger type. It does not
send project records, collect payment details, or create an order.

Duffel labels this environment as a sandbox; its schedules and prices are not
realistic. The governed `MART_FLIGHT_OFFER_SNAPSHOT_SUMMARY` therefore
demonstrates ingestion and offer-shape analytics only, not live market pricing.
See the [flight-offer sandbox runbook](docs/13_duffel_flight_offer_sandbox.md).

## Live hotel-property discovery

The optional hotel flow queries Geoapify Places around version-controlled city
coordinates used by the synthetic trip data. It produces a bounded property
discovery snapshot in `RAW_HOTEL_PROPERTIES`, then publishes aggregate counts
and distances in `MART_DESTINATION_HOTEL_DISCOVERY`.

This flow provides live external property metadata only. It does **not**
provide hotel rates, availability, room inventory, booking functionality, or
any claim of market coverage. See the [hotel-property discovery
runbook](docs/14_live_hotel_property_discovery.md).

## Scheduled refresh

Run all approved live enrichments and rebuild governed marts with:

```powershell
.\scripts\run_live_data_refresh.ps1
```

It runs Open-Meteo weather, Duffel **test-mode** offers, Geoapify
hotel-property discovery, then a full dbt build. By default it replaces each
external RAW snapshot to prevent accidental accumulation of repeated results.
The [scheduled-refresh runbook](docs/15_scheduled_live_data_refresh.md)
includes a dry run, Windows Task Scheduler setup, and security boundaries.

## Governed AI access

The MCP service is intentionally constrained:

- Its Snowflake role has `USAGE` on the warehouse, database, and analytics
  schema plus `SELECT` on only two daily KPI marts.
- It has no access to RAW, STAGING, INTERMEDIATE, or employee-level data.
- It exposes no arbitrary SQL tool.
- All dates are validated and all SQL values are parameterized.

The available tools are `get_product_funnel_summary`,
`get_operations_summary`, and `get_kpi_trend`.

## Technology

| Area | Tools |
| --- | --- |
| Data generation and ingestion | Python, pandas, Faker, Snowflake Connector, Open-Meteo API, Geoapify Places API |
| Transformation and testing | SQL, dbt, dbt-snowflake |
| Warehouse | Snowflake |
| Business intelligence | ThoughtSpot |
| AI integration | MCP Python SDK, Codex |
| Quality checks | pytest, dbt tests |

## Project structure

```text
dbt/       dbt models, tests, macros, and source definitions
docs/      architecture notes, setup runbooks, and demo guide
scripts/   repeatable developer checks and local commands
sql/       Snowflake bootstrap and least-privilege role scripts
src/       synthetic data, ingestion, and MCP application code
tests/     Python unit tests
```

## Reproduce locally

Follow the documentation in order:

1. [Environment setup](docs/01_setup.md)
2. [Metric contract](docs/02_project_charter.md)
3. [Snowflake foundation](docs/03_snowflake_bootstrap.md)
4. [Python data generation and RAW ingestion](docs/05_synthetic_data.md)
5. [dbt transformations and governed marts](docs/07_dbt_staging.md)
6. [ThoughtSpot setup](docs/09_thoughtspot_setup.md)
7. [Read-only MCP service](docs/10_read_only_mcp.md)

For the completed five-minute walkthrough, use the
[interview demo runbook](docs/11_interview_demo.md).

## Verification evidence

- Synthetic-data unit test: `1 passed`
- Full dbt build: `69` passing checks
- MCP query-policy tests: `4 passed`
- MCP protocol discovery: three advertised tools
- End-to-end MCP calls: product summary, operations summary, and daily trend

## Production hardening next steps

- Use Snowflake key-pair or workload-identity authentication instead of local
  passwords.
- Store secrets in a vault and deploy the MCP service behind authenticated
  Streamable HTTP.
- Extend CI with dependency pinning, model-contract checks, and protected-branch
  requirements.
- Add freshness monitoring, warehouse cost controls, and alerting.

## Security note

Never commit `.env`, passwords, tokens, generated exports, dbt artifacts, or
local editor configuration. The included `.gitignore` excludes these files.
