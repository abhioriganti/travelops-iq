# Lesson 2 — Project charter and metric contract

## Portfolio product: Travel Operations Command Center

Build a trusted analytics layer for a fictional corporate-travel platform. It tracks how employees search, book, travel, expense, and receive support. The project demonstrates the same lifecycle highlighted in the role: data models, automated workflows, quality controls, self-service analytics, and a responsible AI interface.

## Stakeholders and decisions

| Stakeholder | Decision | Trusted metric |
| --- | --- | --- |
| Product manager | Which checkout step should we improve? | Search-to-book conversion, checkout abandonment, time-to-book |
| Travel operations lead | Where is service friction highest? | Support-contact rate, disruption rate, resolution time |
| Finance/policy owner | Is policy adoption improving? | In-policy booking rate, out-of-policy spend, savings captured |
| Supplier manager | Which supplier or route needs attention? | Cancellation rate, delay rate, average booked cost |

## Data sources (all synthetic)

| Source | Grain | Important fields |
| --- | --- | --- |
| `raw_booking_events` | one event in a booking journey | event timestamp, session, user, trip, event type, channel |
| `raw_trips` | one booked trip | trip, employee, policy, supplier, route, booked cost, status |
| `raw_expenses` | one expense claim | expense, trip, category, amount, receipt flag, approval status |
| `raw_policy_evaluations` | one policy decision | trip, rule, result, exception reason |
| `raw_support_cases` | one support case | trip, issue type, opened/resolved timestamps, resolution channel |

## Metrics with precise definitions

1. **Search-to-book conversion** = distinct sessions with `booking_confirmed` / distinct sessions with `search_submitted`. Filter to completed sessions and a chosen calendar period.
2. **In-policy booking rate** = booked trips with no policy violation / all booked trips. A missing policy evaluation is *unknown*, not compliant.
3. **Out-of-policy spend** = sum of booked cost for trips with at least one material violation. Do not double-count a trip with multiple rules.
4. **Support-contact rate** = trips with one or more support cases / booked trips.
5. **Expense receipt capture rate** = submitted expenses with a receipt / all submitted expenses.

Every metric needs an owner, grain, filters, numerator, denominator, data-quality expectation, and known limitation. This prevents different dashboards from reporting conflicting numbers.

## Target architecture

```text
Python synthetic generator
          |
          v
Snowflake RAW tables --> dbt STAGING --> dbt INTERMEDIATE --> dbt ANALYTICS marts
  immutable sources       typed/clean       business logic         governed KPI views
                                                                  |              |
                                                                  v              v
                                                         ThoughtSpot      Read-only MCP tools
                                                         Liveboards       natural-language Q&A
```

The MCP server will never query raw tables or execute arbitrary SQL. It will expose bounded tools such as `get_kpi_summary` and `find_policy_violations`, each backed by approved analytic views and parameter validation.

## Definition of done

- `dbt build` passes with source, uniqueness, relationship, accepted-value, and custom metric tests.
- A daily product and operations mart is documented and queryable.
- A ThoughtSpot Liveboard answers the four stakeholder decisions above.
- A small Python report catches deliberate bad records before they reach the dashboard.
- The MCP demo answers allowed read-only questions and rejects unapproved/ad-hoc SQL.
- README contains architecture, setup, data dictionary, metric definitions, cost controls, and a 3-minute demo script.

## Interview narrative

Describe the project in this order: start with a stakeholder decision, state the metric contract, explain the warehouse/dbt layers and tests that make it reliable, show the ThoughtSpot self-service experience, then demonstrate the safe AI/MCP layer. Emphasize tradeoffs: synthetic data, constrained tools, least privilege, and warehouse cost controls.
