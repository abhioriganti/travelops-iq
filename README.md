# TravelOpsIQ

**Governed travel product and operations analytics.** An interview-ready,
end-to-end analytics-engineering portfolio project using **Python, SQL,
Snowflake, dbt, ThoughtSpot**, and a local read-only MCP service.

This project deliberately uses *synthetic data*. It is an independent portfolio
project, does not use customer data, and does not call private company APIs.

## The business problem

Product and Operations need one trusted view of the travel journey:

- Do travelers find and complete a booking efficiently?
- How much spend is in policy, out of policy, or avoided through savings?
- Which suppliers, routes, and support reasons create operational friction?
- Where should a product manager investigate conversion or compliance drops?

The finished product will give stakeholders governed metrics in ThoughtSpot and an optional conversational analytics interface backed only by curated Snowflake views.

## Learning path

Work in order. Do not skip the data contract or data-quality stages just to get a dashboard faster.

1. **Set up accounts and local tooling** — follow [docs/01_setup.md](docs/01_setup.md).
2. **Define metrics and source contracts** — follow [docs/02_project_charter.md](docs/02_project_charter.md).
3. **Generate and load synthetic operational data** with Python.
4. **Build dbt staging, intermediate, and mart models** in Snowflake.
5. **Add tests, freshness checks, and quality monitoring.**
6. **Create ThoughtSpot worksheets and Liveboards.**
7. **Build a local read-only MCP analytics assistant** over approved marts â€” follow [docs/10_read_only_mcp.md](docs/10_read_only_mcp.md).
8. **Package the result** — use [docs/11_interview_demo.md](docs/11_interview_demo.md) for the architecture, verified evidence, demo script, and interview talking points.

Every lesson will include its goal, commands, expected result, likely errors, and how to debug them. We will implement one stage at a time so you understand each decision.

## Repository layout

```text
.
├── docs/             # business requirements, setup notes, runbooks, data dictionary
├── src/              # Python ingestion, synthetic-data generation, and MCP service
├── dbt/              # dbt project: models, tests, macros, and seeds
├── tests/            # Python tests
├── scripts/          # safe developer checks and repeatable local commands
├── data/             # ignored generated files; never commit exports or credentials
├── requirements.txt  # Python dependencies for this lab
└── .env.example      # names of required secrets, never their values
```

This is an industry-standard separation of concerns: application code, transformation code, documentation, automated tests, and local-only data each have a clear home. The layout will grow only when the next lesson needs it.

## Start here

Run the prerequisite checker from PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\check_prerequisites.ps1
```

Then read [docs/01_setup.md](docs/01_setup.md). Do **not** put a Snowflake password, private key, ThoughtSpot token, or any company data in this repository or chat.
