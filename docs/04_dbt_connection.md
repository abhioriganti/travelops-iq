# Lesson 4 — Connect dbt to Snowflake

## Goal

Prove that the local dbt project can authenticate as `TRAVEL_ANALYTICS_DEV` and can use only the `TRAVEL_ANALYTICS_XS` warehouse and `TRAVEL_ANALYTICS` database.

## Choose the right identity

If you signed in to Snowsight with Google, keep using that account for the web UI. Do not use a different Snowflake account: it will not contain the database, role, and warehouse created in Lesson 3.

Instead, create the dedicated `TRAVEL_ANALYTICS_DBT` user inside the current trial account. It is a local-development identity with only the development role. This prevents a future automated job from using an administrator’s Google sign-in. In a production system, it would use key-pair authentication or OAuth; password authentication is a temporary learning-step convenience.

1. Open [sql/02_create_dbt_user.sql](../sql/02_create_dbt_user.sql).
2. Replace the password placeholder with a new, long, unique password you create solely for this lab.
3. Run it as `ACCOUNTADMIN` in Snowsight.
4. Confirm `SHOW USERS` returns one row.

Never share that password in chat, screenshots, or source code.

## 1. Get the preferred dbt account identifier

In Snowsight, still using `TRAVEL_ANALYTICS_DEV`, run:

```sql
SELECT CURRENT_ORGANIZATION_NAME() || '-' || CURRENT_ACCOUNT_NAME() AS dbt_account;
```

Use that result for `SNOWFLAKE_ACCOUNT`. It is an account address, not a credential. Snowflake documents the `organization-account_name` format as the preferred identifier for client connections.

## 2. Create local-only configuration

In PowerShell at the repository root:

```powershell
Copy-Item .env.example .env
notepad .env
```

Before creating the dbt profile, protect any existing project configuration:

```powershell
Test-Path "$env:USERPROFILE\.dbt\profiles.yml"
```

If the result is `False`, create and copy the profile:

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.dbt"
Copy-Item .\dbt\profiles.yml.example "$env:USERPROFILE\.dbt\profiles.yml"
```

If the result is `True`, do not overwrite it; merge the profile deliberately so
you do not disrupt an existing dbt project.

Enter your own values in `.env`:

```text
SNOWFLAKE_ACCOUNT=organization-account_name-from-the-query
SNOWFLAKE_USER=TRAVEL_ANALYTICS_DBT
SNOWFLAKE_PASSWORD=<your-local-dbt-service-password>
SNOWFLAKE_ROLE=TRAVEL_ANALYTICS_DEV
SNOWFLAKE_WAREHOUSE=TRAVEL_ANALYTICS_XS
SNOWFLAKE_DATABASE=TRAVEL_ANALYTICS
SNOWFLAKE_SCHEMA=DBT_DEV
```

Save and close Notepad. `.env` is ignored by Git. Do not send its content, password, MFA prompt, or access token to anyone.

This lesson uses local password authentication because it is easiest to understand and requires no paid tool. In a production service we would use a service identity plus key-pair authentication or SSO/OAuth—not a developer’s password.

## 3. Verify the connection

Run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\dbt_debug.ps1
```

The helper script loads `.env` into the process only, then runs `dbt debug`; it never prints secret values.

## Expected result

`All checks passed!` with the profile, project, adapter, and connection tests succeeding. The warehouse may briefly resume for the connection test and should suspend after 60 seconds.

## Debugging guide

| Symptom | Most likely cause | Fix |
| --- | --- | --- |
| `env_var ... not set` | `.env` is absent or misspelled | Confirm it is named exactly `.env` in the repository root. |
| `Incorrect username or password` | login values are wrong or password has changed | Sign in to Snowsight to verify the password, then update only `.env`. |
| `Account must be specified` / cannot connect | account identifier used the locator or URL | Use the `organization-account_name` SQL query above—not a full URL. |
| `Insufficient privileges` | wrong role/default role | Check `.env` says `TRAVEL_ANALYTICS_DEV`; verify the grant succeeded. |
| `Could not find profile` | file is not in `%USERPROFILE%\\.dbt\\profiles.yml` | Repeat the copy command and run the helper script again. |
