"""Retrieve real historical weather for TravelOpsIQ route enrichment.

This module deliberately contains no Snowflake logic.  It translates the
synthetic city codes used by the project into fixed coordinates, calls the
Open-Meteo historical-weather API, and returns a small source-shaped record
that a later ingestion step can persist in RAW.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import date
from typing import Any
from urllib.parse import urlencode
from urllib.request import urlopen


OPEN_METEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
DAILY_VARIABLES = (
    "temperature_2m_max",
    "precipitation_sum",
    "wind_speed_10m_max",
    "weather_code",
)


@dataclass(frozen=True)
class CityLocation:
    """A stable mapping between a project city code and API coordinates."""

    code: str
    name: str
    country_code: str
    latitude: float
    longitude: float


# These coordinates are deliberately versioned with the project instead of
# geocoding dynamically, making runs deterministic and avoiding an extra API.
CITY_LOCATIONS = {
    "AMS": CityLocation("AMS", "Amsterdam", "NL", 52.3676, 4.9041),
    "ATL": CityLocation("ATL", "Atlanta", "US", 33.7490, -84.3880),
    "AUS": CityLocation("AUS", "Austin", "US", 30.2672, -97.7431),
    "BOS": CityLocation("BOS", "Boston", "US", 42.3601, -71.0589),
    "CHI": CityLocation("CHI", "Chicago", "US", 41.8781, -87.6298),
    "DAL": CityLocation("DAL", "Dallas", "US", 32.7767, -96.7970),
    "DEN": CityLocation("DEN", "Denver", "US", 39.7392, -104.9903),
    "LAX": CityLocation("LAX", "Los Angeles", "US", 34.0522, -118.2437),
    "LON": CityLocation("LON", "London", "GB", 51.5072, -0.1276),
    "MIA": CityLocation("MIA", "Miami", "US", 25.7617, -80.1918),
    "NYC": CityLocation("NYC", "New York City", "US", 40.7128, -74.0060),
    "SEA": CityLocation("SEA", "Seattle", "US", 47.6062, -122.3321),
    "SFO": CityLocation("SFO", "San Francisco", "US", 37.7749, -122.4194),
    "TYO": CityLocation("TYO", "Tokyo", "JP", 35.6762, 139.6503),
    "WAS": CityLocation("WAS", "Washington, DC", "US", 38.9072, -77.0369),
}


def get_city_location(city_code: str) -> CityLocation:
    """Return a supported city location or raise a clear validation error."""
    normalized_code = city_code.strip().upper()
    try:
        return CITY_LOCATIONS[normalized_code]
    except KeyError as error:
        raise ValueError(f"Unsupported city code: {city_code!r}") from error


def build_historical_weather_url(city_code: str, weather_date: date) -> str:
    """Build the one-day Open-Meteo archive request for a supported city."""
    location = get_city_location(city_code)
    parameters = urlencode(
        {
            "latitude": location.latitude,
            "longitude": location.longitude,
            "start_date": weather_date.isoformat(),
            "end_date": weather_date.isoformat(),
            "daily": ",".join(DAILY_VARIABLES),
            "timezone": "auto",
        }
    )
    return f"{OPEN_METEO_ARCHIVE_URL}?{parameters}"


def _read_json(url: str, timeout_seconds: float) -> Mapping[str, Any]:
    with urlopen(url, timeout=timeout_seconds) as response:  # noqa: S310 - fixed trusted host
        return json.load(response)


def _daily_value(daily: Mapping[str, Any], field: str, weather_date: date) -> Any:
    dates = daily.get("time")
    values = daily.get(field)
    if not isinstance(dates, list) or not isinstance(values, list):
        raise ValueError(f"Open-Meteo response is missing daily {field!r} values")

    try:
        index = dates.index(weather_date.isoformat())
    except ValueError as error:
        raise ValueError("Open-Meteo response does not contain the requested weather date") from error

    try:
        return values[index]
    except IndexError as error:
        raise ValueError(f"Open-Meteo response has no value for daily {field!r}") from error


def fetch_historical_weather(
    city_code: str,
    weather_date: date,
    *,
    timeout_seconds: float = 20.0,
    request_json: Callable[[str, float], Mapping[str, Any]] = _read_json,
) -> dict[str, Any]:
    """Fetch selected daily weather metrics for one project city and date.

    ``request_json`` is injectable so tests can validate parsing without a
    network call. The returned record is intentionally narrow and contains no
    traveler-level information.
    """
    location = get_city_location(city_code)
    response = request_json(build_historical_weather_url(location.code, weather_date), timeout_seconds)
    daily = response.get("daily")
    if not isinstance(daily, Mapping):
        raise ValueError("Open-Meteo response is missing a daily data section")

    return {
        "weather_date": weather_date.isoformat(),
        "location_code": location.code,
        "location_name": location.name,
        "country_code": location.country_code,
        "latitude": response.get("latitude", location.latitude),
        "longitude": response.get("longitude", location.longitude),
        "temperature_max_c": _daily_value(daily, "temperature_2m_max", weather_date),
        "precipitation_sum_mm": _daily_value(daily, "precipitation_sum", weather_date),
        "wind_speed_max_kmh": _daily_value(daily, "wind_speed_10m_max", weather_date),
        "weather_code": _daily_value(daily, "weather_code", weather_date),
        "source": "open_meteo_archive",
    }
