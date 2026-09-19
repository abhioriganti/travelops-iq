"""Land Open-Meteo destination weather observations in Snowflake RAW.

The job reads only distinct destination/date pairs from the project's existing
synthetic trips, retrieves public historical weather once per destination date
range, and stores a narrow external-source snapshot. It never sends employee,
trip, or booking data to the weather API.
"""

from __future__ import annotations

import argparse
import os
from collections import defaultdict
from collections.abc import Callable, Iterable, Mapping
from datetime import date, datetime, timezone
from typing import Any

import pandas as pd
import snowflake.connector
from dotenv import load_dotenv
from snowflake.connector.pandas_tools import write_pandas

from src.travel_analytics.load_raw_to_snowflake import get_snowflake_connection_settings
from src.travel_analytics.weather import fetch_historical_weather_range


RAW_WEATHER_TABLE = "RAW_WEATHER_OBSERVATIONS"


def _group_destination_dates(rows: Iterable[tuple[str, date]]) -> dict[str, set[date]]:
    grouped: dict[str, set[date]] = defaultdict(set)
    for destination_code, departure_date in rows:
        if not isinstance(departure_date, date):
            raise ValueError("RAW_TRIPS departure_date must be a date")
        grouped[destination_code].add(departure_date)
    return dict(grouped)


def build_weather_observations(
    destination_dates: Mapping[str, set[date]],
    *,
    fetch_weather: Callable[[str, date, date], list[dict[str, Any]]] = fetch_historical_weather_range,
) -> list[dict[str, Any]]:
    """Retrieve only the destination/date observations required by RAW_TRIPS."""
    observations: list[dict[str, Any]] = []
    for destination_code in sorted(destination_dates):
        requested_dates = destination_dates[destination_code]
        response_records = fetch_weather(
            destination_code, min(requested_dates), max(requested_dates)
        )
        requested_date_strings = {value.isoformat() for value in requested_dates}
        observations.extend(
            record for record in response_records if record["weather_date"] in requested_date_strings
        )
    return sorted(observations, key=lambda record: (record["weather_date"], record["location_code"]))


def load_live_weather(*, replace: bool = False) -> int:
    """Fetch public weather for known synthetic trip destinations and write RAW."""
    load_dotenv()
    connection_settings = get_snowflake_connection_settings()

    with snowflake.connector.connect(**connection_settings) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                select distinct destination_city_code, departure_date
                from raw_trips
                where departure_date < current_date()
                order by destination_city_code, departure_date
                """
            )
            destination_dates = _group_destination_dates(cursor.fetchall())

    observations = build_weather_observations(destination_dates)
    if not observations:
        return 0

    frame = pd.DataFrame(observations)
    frame["retrieved_at"] = datetime.now(timezone.utc).replace(tzinfo=None)

    with snowflake.connector.connect(**connection_settings) as connection:
        with connection.cursor() as cursor:
            if replace:
                cursor.execute(f"truncate table {RAW_WEATHER_TABLE}")

        success, _, row_count, _ = write_pandas(
            connection,
            frame,
            RAW_WEATHER_TABLE,
            database=os.environ["SNOWFLAKE_DATABASE"],
            schema="RAW",
            auto_create_table=False,
            overwrite=False,
            quote_identifiers=False,
            use_logical_type=True,
        )
        if not success:
            raise RuntimeError("Snowflake reported an unsuccessful live-weather load")
    return row_count


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Truncate only RAW_WEATHER_OBSERVATIONS before this snapshot load.",
    )
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    print(f"{RAW_WEATHER_TABLE}: {load_live_weather(replace=arguments.replace)} rows loaded")


if __name__ == "__main__":
    main()
