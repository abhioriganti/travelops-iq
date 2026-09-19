# Scheduled Live-Data Refresh

## Purpose and boundary

[`scripts/run_live_data_refresh.ps1`](../scripts/run_live_data_refresh.ps1)
refreshes the project's three approved external enrichments and then runs a
full dbt build:

1. Open-Meteo historical weather for approved destination coordinates and past
   departure dates
2. Duffel **test-mode** anonymous flight offers for the configured sandbox
   route
3. Geoapify hotel-property discovery around approved destination coordinates
4. dbt staging models, marts, and tests

It is a local operator workflow. It reads credentials only from the ignored
local `.env`; no token is put in Git, Task Scheduler arguments, or command
output. The flight flow stays in Duffel test mode and creates no order.

## Prerequisites

Before the first run, ensure all three RAW tables already exist, `.env` has
Snowflake plus Duffel and Geoapify values, and `%USERPROFILE%\.dbt\profiles.yml`
is configured. Follow the individual enrichment runbooks if a table has not
yet been created:

- [Live weather enrichment](12_live_weather_enrichment.md)
- [Duffel flight-offer sandbox](13_duffel_flight_offer_sandbox.md)
- [Live hotel-property discovery](14_live_hotel_property_discovery.md)

## Run manually first

From the repository root, preview the workflow without calling an API or
Snowflake:

```powershell
.\scripts\run_live_data_refresh.ps1 -DryRun
```

### PowerShell execution policy

If PowerShell reports that script execution is disabled, allow locally created
scripts for **your user only** before scheduling the workflow:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Do not run PowerShell as administrator and do not set the policy to
`Unrestricted`. If an organization-managed policy prevents this change, leave
that policy in place and ask the administrator for the approved local-script
process.

Run the refresh:

```powershell
.\scripts\run_live_data_refresh.ps1
```

The default mode uses `--replace` for each RAW external snapshot. This keeps
the published marts current and avoids combining repeated snapshots into an
unintended total. Use `-Append` only when deliberately retaining snapshot
history and when downstream aggregation has been reviewed for that use case:

```powershell
.\scripts\run_live_data_refresh.ps1 -Append
```

The script stops at the first failed ingestion and does not run dbt afterward,
so a failed external refresh cannot silently publish stale transformed data as
a successful run.

## Schedule with Windows Task Scheduler

Schedule only after a manual run succeeds.

1. Open **Task Scheduler** and choose **Create Basic Task**.
2. Name it `TravelOpsIQ Live Data Refresh` and choose a conservative trigger,
   such as once each morning.
3. For **Start a program**, use `powershell.exe`.
4. Set **Add arguments** to the following, replacing the path only if your
   project is stored elsewhere:

   ```text
   -NoProfile -File "C:\Users\abhis\projects\Navan Project\scripts\run_live_data_refresh.ps1"
   ```

5. Set **Start in** to:

   ```text
   C:\Users\abhis\projects\Navan Project
   ```

6. Prefer **Run only when user is logged on** for this local portfolio
   workflow. It avoids storing a Windows password in the scheduled task.
7. Run the task once manually from Task Scheduler and confirm a zero
   **Last Run Result**. If it fails, run the script in PowerShell to see the
   failing step.

Do not put API tokens, Snowflake passwords, or `.env` values in task names,
arguments, descriptions, screenshots, GitHub Actions, or ThoughtSpot.

## ThoughtSpot follow-up

Snowflake marts are rebuilt by the script. ThoughtSpot visuals use the same
models, so they show the newest data after the connection refresh/cache policy
allows it. The dashboard labels must remain accurate: Duffel is test-mode
offer data, and Geoapify results are capped property-discovery samples.

## Interview framing

Say: “I added a local scheduled refresh that sequences bounded external API
loads before the dbt build. It fails closed, keeps credentials outside source
control, and refreshes governed marts consumed by ThoughtSpot.”
