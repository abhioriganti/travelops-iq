# Lesson 10: Read-only MCP analytics service

## Goal

Expose a small, safe set of governed Snowflake KPI questions to an MCP-compatible
AI client. This is a local developer demonstration, not a production service
or an integration with any third-party travel platform.

The server reads only `ANALYTICS.MART_PRODUCT_DAILY` and
`ANALYTICS.MART_OPERATIONS_DAILY`. It cannot query RAW data, employee-level
tables, or SQL supplied by an AI client.

## Why this structure

- `sql/05_create_mcp_reader.sql` creates a distinct least-privilege identity.
- `src/travel_analytics/mcp/queries.py` holds fixed SQL templates and input
  validation; it is straightforward to test and review.
- `src/travel_analytics/mcp/server.py` exposes those reviewed questions as MCP
  tools and contains the Snowflake connection boundary.
- `tests/test_mcp_queries.py` proves that tools use parameterized SQL, selected
  marts only, and reject arbitrary metric names.
- `scripts/run_mcp.ps1` runs the server locally over standard input/output.

This separation is common in production: credentials and database I/O stay at
the boundary, while the business-query policy is small, version-controlled, and
unit tested.

## Step 1: Create the service identity

In a Snowflake SQL File, run `sql/05_create_mcp_reader.sql` as `ACCOUNTADMIN`.
Before running it, replace the password placeholder with a new long unique
password. Do not use your personal password, the dbt password, or the
ThoughtSpot password.

Expected grants are only warehouse/database/schema `USAGE` plus two `SELECT`
grants on the daily KPI marts. There must be no grants on `RAW`, `STAGING`, or
`INTERMEDIATE`.

## Step 2: Add local-only configuration

In the existing ignored `.env` file, add the following values. They are not
commands and must not contain quotation marks around the password.

```dotenv
SNOWFLAKE_MCP_ACCOUNT=your-account-identifier
SNOWFLAKE_MCP_USER=TRAVEL_ANALYTICS_MCP_SERVICE
SNOWFLAKE_MCP_PASSWORD=your-new-mcp-service-password
SNOWFLAKE_MCP_ROLE=TRAVEL_ANALYTICS_MCP_READER
SNOWFLAKE_MCP_WAREHOUSE=TRAVEL_ANALYTICS_XS
SNOWFLAKE_MCP_DATABASE=TRAVEL_ANALYTICS
```

## Step 3: Verify the safe query policy locally

Run this from PowerShell at the project root:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_mcp_queries.py -q -p no:cacheprovider
```

Expected result: `4 passed`.

## Step 4: Smoke-check the new service identity

Run the following command. It makes one approved aggregate query as the MCP
service user; it does not start a network service or expose credentials.

```powershell
.\.venv\Scripts\python.exe .\scripts\verify_mcp_service.py
```

Expected result: JSON with aggregate product-funnel KPI values and
`"source": "MART_PRODUCT_DAILY"`.

## Step 5: Verify the MCP protocol

This starts the server in a short-lived local process and asks it to advertise
its tools. It does not invoke a Snowflake query.

```powershell
.\.venv\Scripts\python.exe .\scripts\inspect_mcp_tools.py
```

Expected result: `MCP protocol check passed.` followed by three tool names.

## Step 6: Run the local server

```powershell
.\scripts\run_mcp.ps1
```

It will wait silently for an MCP client on standard input/output. That is normal;
do not type SQL into this window. Stop it with `Ctrl+C`.

## Step 7: Use it from a local Codex client

This project includes a local-only `.codex/config.toml` registration. It has no
credentials and is ignored by Git because its Python path is specific to this
machine. Restart your local Codex IDE extension, Codex CLI session, or ChatGPT
desktop app after opening this trusted project. Then use `/mcp` to confirm that
`travel_analytics` exposes three tools.

Try this prompt in that local client:

```text
Use the travel_analytics MCP tools to summarize product funnel performance from
2026-06-01 through 2026-08-31. State the source table and do not query data
outside the available tools.
```

The server runs locally through stdio; ChatGPT in a web browser does not read
this project configuration.

## Approved tools

| Tool | What it returns |
| --- | --- |
| `get_product_funnel_summary` | Aggregate funnel totals and weighted conversion rates |
| `get_operations_summary` | Aggregate booking, policy, spend, support, and expense KPIs |
| `get_kpi_trend` | One of six allow-listed daily trends |

All date inputs require `YYYY-MM-DD` and are limited to 180 days. Aggregate
ratios are calculated as weighted ratios across the requested period, rather
than by averaging daily rates.

## Debugging guide

| Symptom | Most likely cause | Fix |
| --- | --- | --- |
| `Missing MCP environment variables` | One or more `SNOWFLAKE_MCP_...` entries is absent from `.env` | Add the names above; do not paste values into chat. |
| `Incorrect username or password` | Service-user password differs from `.env` | Reset that service user's password in Snowflake, then update only `.env`. |
| `Insufficient privileges` | The role or two table grants were not applied | Run the verification statements at the end of the SQL file as `ACCOUNTADMIN`. |
| `Unsupported ... metric` | A client asked for a metric outside the allow-list | Use a listed metric or deliberately add a reviewed query template and test. |
| Import error mentioning `FastMCP` | An old MCP tutorial targets the 1.x SDK | This project uses the installed v2 `MCPServer` API. |
