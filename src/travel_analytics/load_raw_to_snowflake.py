"""Load synthetic CSV source tables into Snowflake's RAW schema.

This loader is deliberately separate from transformation logic. It lands
source-shaped data with an ingestion timestamp; dbt owns cleaning and business
definitions in later layers.
"""

from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import snowflake.connector
from dotenv import load_dotenv
from snowflake.connector.pandas_tools import write_pandas


TABLE_FILES = {
    "RAW_EMPLOYEES": "employees.csv",
    "RAW_TRIPS": "trips.csv",
    "RAW_BOOKING_EVENTS": "booking_events.csv",
    "RAW_EXPENSES": "expenses.csv",
    "RAW_POLICY_EVALUATIONS": "policy_evaluations.csv",
    "RAW_SUPPORT_CASES": "support_cases.csv",
}
REQUIRED_ENVIRONMENT_VARIABLES = [
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_PASSWORD",
    "SNOWFLAKE_ROLE",
    "SNOWFLAKE_WAREHOUSE",
    "SNOWFLAKE_DATABASE",
]


def get_snowflake_connection_settings() -> dict[str, str]:
    missing = [name for name in REQUIRED_ENVIRONMENT_VARIABLES if not os.getenv(name)]
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")
    return {
        "account": os.environ["SNOWFLAKE_ACCOUNT"],
        "user": os.environ["SNOWFLAKE_USER"],
        "password": os.environ["SNOWFLAKE_PASSWORD"],
        "role": os.environ["SNOWFLAKE_ROLE"],
        "warehouse": os.environ["SNOWFLAKE_WAREHOUSE"],
        "database": os.environ["SNOWFLAKE_DATABASE"],
        "schema": "RAW",
    }


def load_raw_data(input_dir: Path, *, replace: bool = False) -> dict[str, int]:
    """Load all expected source CSVs and return rows successfully written per table."""
    missing_files = [filename for filename in TABLE_FILES.values() if not (input_dir / filename).is_file()]
    if missing_files:
        raise FileNotFoundError(f"Missing source files in {input_dir}: {', '.join(missing_files)}")

    load_dotenv()
    # RAW stores a UTC-normalized timestamp without timezone metadata (TIMESTAMP_NTZ).
    loaded_at = datetime.now(timezone.utc).replace(tzinfo=None)
    results: dict[str, int] = {}

    with snowflake.connector.connect(**get_snowflake_connection_settings()) as connection:
        with connection.cursor() as cursor:
            for table_name, filename in TABLE_FILES.items():
                frame = pd.read_csv(input_dir / filename)
                frame["ingested_at"] = loaded_at

                if replace:
                    cursor.execute(f"TRUNCATE TABLE {table_name}")

                success, _, row_count, _ = write_pandas(
                    connection,
                    frame,
                    table_name,
                    database=os.environ["SNOWFLAKE_DATABASE"],
                    schema="RAW",
                    auto_create_table=False,
                    overwrite=False,
                    quote_identifiers=False,
                    use_logical_type=True,
                )
                if not success:
                    raise RuntimeError(f"Snowflake reported an unsuccessful load for {table_name}")
                results[table_name] = row_count

    return results


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=Path("data/generated"))
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Truncate each known RAW table before loading its deterministic source CSV.",
    )
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    results = load_raw_data(arguments.input_dir, replace=arguments.replace)
    for table_name, row_count in results.items():
        print(f"{table_name}: {row_count} rows loaded")


if __name__ == "__main__":
    main()
