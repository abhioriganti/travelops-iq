"""Local stdio MCP server exposing approved travel-analytics questions only."""

from __future__ import annotations

import os
from datetime import date, datetime
from decimal import Decimal
from typing import Any

import snowflake.connector
from dotenv import load_dotenv
from mcp.server.mcpserver import MCPServer

from src.travel_analytics.mcp.queries import (
    operations_summary_statement,
    product_summary_statement,
    trend_statement,
)


server = MCPServer(
    name="travel-analytics",
    title="Travel Operations Analytics",
    description="Read-only, governed product and operations KPI tools backed by Snowflake marts.",
    instructions=(
        "Use these tools only for aggregate travel analytics. Dates must be ISO-8601 "
        "and no more than 180 days apart. Do not infer individual traveler information."
    ),
)

REQUIRED_ENVIRONMENT_VARIABLES = (
    "SNOWFLAKE_MCP_ACCOUNT",
    "SNOWFLAKE_MCP_USER",
    "SNOWFLAKE_MCP_PASSWORD",
    "SNOWFLAKE_MCP_ROLE",
    "SNOWFLAKE_MCP_WAREHOUSE",
    "SNOWFLAKE_MCP_DATABASE",
)


def _connection_settings() -> dict[str, str]:
    missing = [name for name in REQUIRED_ENVIRONMENT_VARIABLES if not os.getenv(name)]
    if missing:
        raise RuntimeError(f"Missing MCP environment variables: {', '.join(missing)}")
    return {
        "account": os.environ["SNOWFLAKE_MCP_ACCOUNT"],
        "user": os.environ["SNOWFLAKE_MCP_USER"],
        "password": os.environ["SNOWFLAKE_MCP_PASSWORD"],
        "role": os.environ["SNOWFLAKE_MCP_ROLE"],
        "warehouse": os.environ["SNOWFLAKE_MCP_WAREHOUSE"],
        "database": os.environ["SNOWFLAKE_MCP_DATABASE"],
        "schema": "ANALYTICS",
    }


def _json_value(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def execute_statement(statement: str, parameters: tuple[date, date]) -> list[dict[str, Any]]:
    """Execute a pre-built parameterized statement and return JSON-safe rows."""
    load_dotenv()
    with snowflake.connector.connect(**_connection_settings()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(statement, parameters)
            columns = [column[0].lower() for column in cursor.description]
            return [
                {column: _json_value(value) for column, value in zip(columns, row, strict=True)}
                for row in cursor.fetchall()
            ]


@server.tool(description="Summarize the approved daily product funnel over an inclusive date range.")
def get_product_funnel_summary(start_date: str, end_date: str) -> dict[str, Any]:
    statement, parameters = product_summary_statement(start_date, end_date)
    return {"data": execute_statement(statement, parameters), "source": "MART_PRODUCT_DAILY"}


@server.tool(description="Summarize approved travel operations, spend, policy, and support KPIs over an inclusive date range.")
def get_operations_summary(start_date: str, end_date: str) -> dict[str, Any]:
    statement, parameters = operations_summary_statement(start_date, end_date)
    return {"data": execute_statement(statement, parameters), "source": "MART_OPERATIONS_DAILY"}


@server.tool(
    description=(
        "Get a daily trend for an allow-listed metric. Domains: product or operations. "
        "Product metrics: search_to_book_conversion_rate, checkout_to_book_conversion_rate, booked_sessions. "
        "Operations metrics: booked_trips, in_policy_booking_rate, out_of_policy_spend_usd."
    )
)
def get_kpi_trend(domain: str, metric: str, start_date: str, end_date: str) -> dict[str, Any]:
    statement, parameters = trend_statement(domain, metric, start_date, end_date)
    return {"data": execute_statement(statement, parameters), "source_domain": domain, "metric": metric}


if __name__ == "__main__":
    # stdio is intentional: it keeps this local developer service off the network.
    server.run(transport="stdio")
