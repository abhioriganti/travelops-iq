import pytest

from src.travel_analytics.mcp.queries import (
    operations_summary_statement,
    product_summary_statement,
    trend_statement,
)


def test_product_summary_is_parameterized_and_uses_only_its_mart():
    statement, parameters = product_summary_statement("2026-06-01", "2026-08-31")

    assert "MART_PRODUCT_DAILY" in statement
    assert "MART_OPERATIONS_DAILY" not in statement
    assert statement.count("%s") == 2
    assert [value.isoformat() for value in parameters] == ["2026-06-01", "2026-08-31"]


def test_operations_summary_is_parameterized_and_uses_only_its_mart():
    statement, _ = operations_summary_statement("2026-06-01", "2026-08-31")

    assert "MART_OPERATIONS_DAILY" in statement
    assert "MART_PRODUCT_DAILY" not in statement
    assert statement.count("%s") == 2


def test_trend_rejects_arbitrary_metric_and_invalid_range():
    with pytest.raises(ValueError, match="Unsupported product metric"):
        trend_statement("product", "select * from raw_employees", "2026-06-01", "2026-08-31")

    with pytest.raises(ValueError, match="start_date"):
        trend_statement("operations", "booked_trips", "2026-08-31", "2026-06-01")


def test_allowed_trend_uses_the_expected_table():
    statement, parameters = trend_statement(
        "operations", "in_policy_booking_rate", "2026-06-01", "2026-08-31"
    )

    assert "MART_OPERATIONS_DAILY" in statement
    assert "sum(in_policy_trips) / nullif(sum(booked_trips), 0)" in statement
    assert [value.isoformat() for value in parameters] == ["2026-06-01", "2026-08-31"]
