"""Land live Geoapify hotel-property discovery records in Snowflake RAW.

The job queries only distinct synthetic-trip destination codes, which map to
version-controlled city-center coordinates. It does not send trip IDs,
employees, bookings, expenses, payment data, or hotel search dates to Geoapify.
The result is a bounded property-discovery snapshot, not hotel inventory.
"""

from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone

import pandas as pd
import snowflake.connector
from dotenv import load_dotenv
from snowflake.connector.pandas_tools import write_pandas

from src.travel_analytics.geoapify import fetch_hotel_properties
from src.travel_analytics.load_raw_to_snowflake import get_snowflake_connection_settings


RAW_HOTEL_PROPERTIES_TABLE = "RAW_HOTEL_PROPERTIES"


def build_hotel_property_snapshot(
    destination_codes: list[str], api_key: str
) -> list[dict[str, object]]:
    """Fetch one bounded hotel-property result set per unique destination."""
    records: list[dict[str, object]] = []
    for destination_code in sorted(set(destination_codes)):
        records.extend(fetch_hotel_properties(destination_code, api_key))
    return records


def load_live_hotel_properties(*, replace: bool = False) -> int:
    """Fetch external property discovery metadata for known trip destinations."""
    load_dotenv()
    api_key = os.getenv("GEOAPIFY_API_KEY")
    if not api_key:
        raise RuntimeError("Missing required environment variable: GEOAPIFY_API_KEY")
    connection_settings = get_snowflake_connection_settings()

    with snowflake.connector.connect(**connection_settings) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                select distinct destination_city_code
                from raw_trips
                order by destination_city_code
                """
            )
            destination_codes = [row[0] for row in cursor.fetchall()]

    records = build_hotel_property_snapshot(destination_codes, api_key)
    if not records:
        return 0

    frame = pd.DataFrame(records)
    frame["retrieved_at"] = datetime.now(timezone.utc).replace(tzinfo=None)
    with snowflake.connector.connect(**connection_settings) as connection:
        with connection.cursor() as cursor:
            if replace:
                cursor.execute(f"truncate table {RAW_HOTEL_PROPERTIES_TABLE}")

        success, _, row_count, _ = write_pandas(
            connection,
            frame,
            RAW_HOTEL_PROPERTIES_TABLE,
            database=os.environ["SNOWFLAKE_DATABASE"],
            schema="RAW",
            auto_create_table=False,
            overwrite=False,
            quote_identifiers=False,
            use_logical_type=True,
        )
        if not success:
            raise RuntimeError("Snowflake reported an unsuccessful live-hotel-property load")
    return row_count


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Truncate only RAW_HOTEL_PROPERTIES before this snapshot load.",
    )
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    row_count = load_live_hotel_properties(replace=arguments.replace)
    print(f"{RAW_HOTEL_PROPERTIES_TABLE}: {row_count} rows loaded")


if __name__ == "__main__":
    main()
