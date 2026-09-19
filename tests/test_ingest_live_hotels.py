from src.travel_analytics.ingest_live_hotels import build_hotel_property_snapshot


def test_build_hotel_property_snapshot_calls_each_city_once(monkeypatch):
    calls = []

    def fake_fetch(city_code, api_key):
        calls.append((city_code, api_key))
        return [{"destination_city_code": city_code, "place_id": f"place_{city_code}"}]

    monkeypatch.setattr("src.travel_analytics.ingest_live_hotels.fetch_hotel_properties", fake_fetch)

    records = build_hotel_property_snapshot(["CHI", "LON", "CHI"], "test-key")

    assert calls == [("CHI", "test-key"), ("LON", "test-key")]
    assert records == [
        {"destination_city_code": "CHI", "place_id": "place_CHI"},
        {"destination_city_code": "LON", "place_id": "place_LON"},
    ]
