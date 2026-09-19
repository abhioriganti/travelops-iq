from datetime import date

from src.travel_analytics.ingest_live_weather import (
    _group_destination_dates,
    build_weather_observations,
)


def test_group_destination_dates_deduplicates_trip_destination_dates():
    grouped = _group_destination_dates(
        [
            ("CHI", date(2026, 6, 4)),
            ("CHI", date(2026, 6, 4)),
            ("LON", date(2026, 6, 5)),
        ]
    )

    assert grouped == {"CHI": {date(2026, 6, 4)}, "LON": {date(2026, 6, 5)}}


def test_build_weather_observations_keeps_only_dates_used_by_trips():
    calls = []

    def fake_fetch(city_code, start_date, end_date):
        calls.append((city_code, start_date, end_date))
        return [
            {"location_code": city_code, "weather_date": "2026-06-04"},
            {"location_code": city_code, "weather_date": "2026-06-05"},
            {"location_code": city_code, "weather_date": "2026-06-06"},
        ]

    observations = build_weather_observations(
        {"CHI": {date(2026, 6, 4), date(2026, 6, 6)}},
        fetch_weather=fake_fetch,
    )

    assert calls == [("CHI", date(2026, 6, 4), date(2026, 6, 6))]
    assert observations == [
        {"location_code": "CHI", "weather_date": "2026-06-04"},
        {"location_code": "CHI", "weather_date": "2026-06-06"},
    ]
