# Lesson 1 — Set up safely and cheaply

## Goal

Create a repeatable local development environment and free trial accounts without exposing credentials or accidentally spending money. At the end, `dbt debug` should authenticate to your own Snowflake trial account.

## What you need

| Tool | Why it is in the project | What to do |
| --- | --- | --- |
| Git | versioning, code review, reproducibility | Already installed on this machine. Create a repository inside this project folder before committing. |
| Python 3.11 or 3.12 | synthetic data, loaders, quality checks, MCP server | Install alongside the existing Python 3.13. A dedicated 3.11/3.12 environment reduces dependency surprises. |
| VS Code | editing, terminal, SQL/dbt extensions | Recommended but optional. |
| Snowflake trial | warehouse, SQL, data models | Sign up for the 30-day trial; no payment method is required for the trial. |
| dbt-snowflake | tested, versioned transformations | Install it in this project’s virtual environment. |
| ThoughtSpot | self-service semantic layer and dashboards | Start a free trial; later evaluate Developer Edition only if its restrictions work for the portfolio demo. |
| Docker | optional local services only | Not required for this project. Ignore Docker until a later lesson needs it. |

Do **not** pay for ThoughtSpot or add a card simply for this portfolio project. A trial is sufficient for the first dashboard; ThoughtSpot also advertises a Developer Edition for qualifying embedded-development use. Check its current terms before relying on it.

## 1. Install a stable Python side-by-side

Your machine currently has Python 3.13. Keep it; install Python 3.11 or 3.12 from the official Python downloads page. During install, choose **Add Python to PATH**.

Confirm the launcher can find it:

```powershell
py -3.11 --version
```

If this fails, reboot the terminal after installation. Do not uninstall the existing interpreter.

## 2. Create the project environment

From this repository root, run:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
dbt --version
```

Expected result: `dbt-snowflake` appears under **Plugins**. If it is absent, you installed `dbt-core` without the Snowflake adapter; run `pip install dbt-snowflake` while `.venv` is activated.

### Common setup failures

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `py -3.11` cannot find Python | Python launcher did not register that version | Re-run the installer with the launcher/PATH options, then open a new terminal. |
| PowerShell says scripts are disabled | Execution policy blocks virtual-environment activation | Use `Set-ExecutionPolicy -Scope Process Bypass` in that terminal, then activate again. This is temporary. |
| `ModuleNotFoundError` after install | terminal uses global Python rather than `.venv` | Run `Get-Command python`; it should point to `.venv\\Scripts\\python.exe`. |
| dbt cannot find the adapter | only dbt-core is installed | Install `dbt-snowflake` in the activated environment. |

## 3. Create the Snowflake trial account

1. Create a Snowflake trial account with a personal email you control. Do not add a credit card.
2. Choose a cloud/region near you; the exact cloud is not important for this learning project.
3. In Snowsight, record the **account identifier** shown in your URL or account selector. It is needed by dbt.
4. Leave the default warehouse auto-suspend enabled. In our first SQL lesson we will create a dedicated `X-SMALL` warehouse with `AUTO_SUSPEND = 60`.
5. Never use `ACCOUNTADMIN` from dbt. We will create a least-privilege development role.

Snowflake trials last 30 days or until free usage is exhausted. Warehouses consume credits only while running; keep them X-Small and auto-suspend quickly.

## 4. Create a ThoughtSpot trial account

1. Start a ThoughtSpot trial from its official site.
2. Do not add a payment method for this project.
3. We will connect it only to `ANALYTICS` views after dbt tests pass—never directly to raw event tables.
4. Do not create an API token yet; later we will use the smallest read-only permission needed.

## 5. Keep secrets out of source control

When asked in a later lesson, copy `.env.example` to `.env` locally. It is ignored by Git. Prefer a Snowflake key pair for services; use password auth only to get started and never commit it in `profiles.yml`.

## Completion check

Reply with the output of the commands below with secrets redacted. We will then create Snowflake roles, database, schemas, and your first dbt profile together.

```powershell
py -3.11 --version
.\.venv\Scripts\Activate.ps1
dbt --version
```
