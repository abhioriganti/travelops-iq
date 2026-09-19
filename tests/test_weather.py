from datetime import date
from urllib.parse import parse_qs, urlparse

import pytest

from src.travel_analytics.weather import (
    CITY_LOCATIONS,
    build_historical_weather_url,
    fetch_historical_weather,
    get_city_location,
)


def test_city_locations_cover_every_synthetic_trip_code():
    expected_codes = {
        "AMS", "ATL", "AUS", "BOS", "CHI", "DAL", "DEN", "LAX",
        "LON", "MIA", "NYC", "SEA", "SFO", "TYO", "WAS",
    }

    assert expected_codes == set(CITY_LOCATIONS)
    assert get_city_location(" chi ").name == "Chicago"


def test_build_historical_weather_url_uses_requested_city_and_date():
    parsed_url = urlparse(build_historical_weather_url("CHI", date(2026, 6, 4)))
    parameters = parse_qs(parsed_url.query)

    assert parsed_url.netloc == "archive-api.open-meteo.com"
    assert parameters["latitude"] == ["41.8781"]
    assert parameters["start_date"] == ["2026-06-04"]
    assert parameters["end_date"] == ["2026-06-04"]
    assert parameters["timezone"] == ["auto"]


def test_fetch_historical_weather_normalizes_selected_daily_metrics():
    response = {
        "latitude": 41.862915,
        "longitude": -87.64877,
        "daily": {
            "time": ["2026-06-04"],
            "temperature_2m_max": [30.1],
            "precipitation_sum": [0.0],
            "wind_speed_10m_max": [19.2],
            "weather_code": [3],
        },
    }

    record = fetch_historical_weather(
        "CHI", date(2026, 6, 4), request_json=lambda _url, _timeout: response
    )

    assert record == {
        "weather_date": "2026-06-04",
        "location_code": "CHI",
        "location_name": "Chicago",
        "country_code": "US",
        "latitude": 41.862915,
        "longitude": -87.64877,
        "temperature_max_c": 30.1,
        "precipitation_sum_mm": 0.0,
        "wind_speed_max_kmh": 19.2,
        "weather_code": 3,
        "source": "open_meteo_archive",
    }


def test_unknown_city_code_is_rejected_before_calling_api():
    with pytest.raises(ValueError, match="Unsupported city code"):
        fetch_historical_weather("XYZ", date(2026, 6, 4))
