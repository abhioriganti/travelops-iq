"""Land a narrow Duffel sandbox flight-offer snapshot in Snowflake RAW.

The job sends an anonymous origin, destination, date, cabin, and one adult to
Duffel's test API. It never sends project employees, trips, bookings, expenses,
or payment data, and it never creates an order.
"""

from __future__ import annotations

import argparse
import os
from datetime import date, datetime, timezone

import pandas as pd
import snowflake.connector
from dotenv import load_dotenv
from snowflake.connector.pandas_tools import write_pandas

from src.travel_analytics.duffel import DEFAULT_SANDBOX_SEARCH, fetch_sandbox_offer_records
from src.travel_analytics.load_raw_to_snowflake import get_snowflake_connection_settings


RAW_FLIGHT_OFFERS_TABLE = "RAW_FLIGHT_OFFER_SNAPSHOTS"


def load_flight_offer_snapshot(
    *, origin: str, destination: str, departure_date: date, cabin_class: str, replace: bool = False
) -> int:
    """Retrieve one anonymous sandbox search and write its offers to Snowflake RAW."""
    load_dotenv()
    access_token = os.getenv("DUFFEL_ACCESS_TOKEN")
    if not access_token:
        raise RuntimeError("Missing required environment variable: DUFFEL_ACCESS_TOKEN")

    records = fetch_sandbox_offer_records(
        access_token,
        origin=origin,
        destination=destination,
        departure_date=departure_date,
        cabin_class=cabin_class,
    )
    if not records:
        return 0

    frame = pd.DataFrame(records)
    # Duffel returns ISO timestamps with offsets. Normalize before the pandas
    # connector lands them in the RAW TIMESTAMP_NTZ columns.
    for column in ("first_departing_at", "last_expires_at"):
        frame[column] = pd.to_datetime(frame[column], utc=True).dt.tz_localize(None)
    frame["retrieved_at"] = datetime.now(timezone.utc).replace(tzinfo=None)

    connection_settings = get_snowflake_connection_settings()
    with snowflake.connector.connect(**connection_settings) as connection:
        with connection.cursor() as cursor:
            if replace:
                cursor.execute(f"truncate table {RAW_FLIGHT_OFFERS_TABLE}")

        success, _, row_count, _ = write_pandas(
            connection,
            frame,
            RAW_FLIGHT_OFFERS_TABLE,
            database=os.environ["SNOWFLAKE_DATABASE"],
            schema="RAW",
            auto_create_table=False,
            overwrite=False,
            quote_identifiers=False,
            use_logical_type=True,
        )
        if not success:
            raise RuntimeError("Snowflake reported an unsuccessful Duffel flight-offer load")
    return row_count


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--origin", default=DEFAULT_SANDBOX_SEARCH["origin"])
    parser.add_argument("--destination", default=DEFAULT_SANDBOX_SEARCH["destination"])
    parser.add_argument(
        "--departure-date",
        type=date.fromisoformat,
        default=DEFAULT_SANDBOX_SEARCH["departure_date"],
        help="ISO date. Defaults to 30 days from today because Duffel requires a future date.",
    )
    parser.add_argument("--cabin-class", default=DEFAULT_SANDBOX_SEARCH["cabin_class"])
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Truncate RAW_FLIGHT_OFFER_SNAPSHOTS before writing this snapshot.",
    )
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    row_count = load_flight_offer_snapshot(
        origin=arguments.origin,
        destination=arguments.destination,
        departure_date=arguments.departure_date,
        cabin_class=arguments.cabin_class,
        replace=arguments.replace,
    )
    print(f"{RAW_FLIGHT_OFFERS_TABLE}: {row_count} rows loaded")


if __name__ == "__main__":
    main()
