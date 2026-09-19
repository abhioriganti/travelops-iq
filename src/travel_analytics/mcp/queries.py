"""Bounded, parameterized SQL builders for the MCP analytics tools.

No function in this module accepts arbitrary SQL, table names, or column names.
That restriction is intentional: an AI client can ask only pre-approved business
questions against the two governed daily marts.
"""

from __future__ import annotations

from datetime import date
from typing import Final


MAX_LOOKBACK_DAYS: Final = 180

PRODUCT_TRENDS: Final = {
    "search_to_book_conversion_rate": (
        "Search-to-book conversion rate",
        "sum(booked_sessions) / nullif(sum(search_sessions), 0)",
        "session_date",
    ),
    "checkout_to_book_conversion_rate": (
        "Checkout-to-book conversion rate",
        "sum(booked_sessions) / nullif(sum(checkout_sessions), 0)",
        "session_date",
    ),
    "booked_sessions": ("Booked sessions", "sum(booked_sessions)", "session_date"),
}

OPERATIONS_TRENDS: Final = {
    "booked_trips": ("Booked trips", "sum(booked_trips)", "booking_date"),
    "in_policy_booking_rate": (
        "In-policy booking rate",
        "sum(in_policy_trips) / nullif(sum(booked_trips), 0)",
        "booking_date",
    ),
    "out_of_policy_spend_usd": (
        "Out-of-policy spend (USD)",
        "sum(out_of_policy_spend_usd)",
        "booking_date",
    ),
}


def parse_date_range(start_date: str, end_date: str) -> tuple[date, date]:
    """Validate an inclusive ISO-8601 date range safe for the fixed tools."""
    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except ValueError as error:
        raise ValueError("Dates must use YYYY-MM-DD format.") from error

    if start > end:
        raise ValueError("start_date must be on or before end_date.")
    if (end - start).days > MAX_LOOKBACK_DAYS:
        raise ValueError(f"Date range must be {MAX_LOOKBACK_DAYS} days or fewer.")
    return start, end


def product_summary_statement(start_date: str, end_date: str) -> tuple[str, tuple[date, date]]:
    start, end = parse_date_range(start_date, end_date)
    return (
        """
        select
            min(session_date) as start_date,
            max(session_date) as end_date,
            sum(search_sessions) as search_sessions,
            sum(result_view_sessions) as result_view_sessions,
            sum(checkout_sessions) as checkout_sessions,
            sum(booked_sessions) as booked_sessions,
            round(sum(booked_sessions) / nullif(sum(search_sessions), 0), 4)
                as search_to_book_conversion_rate,
            round(sum(booked_sessions) / nullif(sum(checkout_sessions), 0), 4)
                as checkout_to_book_conversion_rate,
            round(avg(average_booked_session_minutes), 2) as average_booked_session_minutes
        from MART_PRODUCT_DAILY
        where session_date between %s and %s
        """,
        (start, end),
    )


def operations_summary_statement(start_date: str, end_date: str) -> tuple[str, tuple[date, date]]:
    start, end = parse_date_range(start_date, end_date)
    return (
        """
        select
            min(booking_date) as start_date,
            max(booking_date) as end_date,
            sum(booked_trips) as booked_trips,
            sum(completed_trips) as completed_trips,
            sum(cancelled_trips) as cancelled_trips,
            round(sum(gross_booking_value_usd), 2) as gross_booking_value_usd,
            round(sum(in_policy_trips) / nullif(sum(booked_trips), 0), 4) as in_policy_booking_rate,
            round(sum(out_of_policy_spend_usd), 2) as out_of_policy_spend_usd,
            round(sum(trips_with_support_contact) / nullif(sum(booked_trips), 0), 4)
                as support_contact_rate,
            round(avg(average_support_resolution_hours), 2) as average_support_resolution_hours,
            round(sum(trip_linked_expense_amount_usd), 2) as trip_linked_expense_amount_usd
        from MART_OPERATIONS_DAILY
        where booking_date between %s and %s
        """,
        (start, end),
    )


def trend_statement(
    domain: str, metric: str, start_date: str, end_date: str
) -> tuple[str, tuple[date, date]]:
    """Return daily trend SQL for one allow-listed metric and date range."""
    start, end = parse_date_range(start_date, end_date)
    allowed_metrics = PRODUCT_TRENDS if domain == "product" else OPERATIONS_TRENDS if domain == "operations" else None
    if allowed_metrics is None:
        raise ValueError("domain must be either 'product' or 'operations'.")
    if metric not in allowed_metrics:
        options = ", ".join(sorted(allowed_metrics))
        raise ValueError(f"Unsupported {domain} metric. Choose one of: {options}.")

    display_name, expression, date_column = allowed_metrics[metric]
    table_name = "MART_PRODUCT_DAILY" if domain == "product" else "MART_OPERATIONS_DAILY"
    return (
        f"""
        select
            {date_column} as metric_date,
            round({expression}, 4) as metric_value,
            '{display_name}' as metric_name
        from {table_name}
        where {date_column} between %s and %s
        group by 1
        order by 1
        """,
        (start, end),
    )
