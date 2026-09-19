from datetime import date

import pytest

from src.travel_analytics.duffel import (
    DUFFEL_OFFER_REQUESTS_URL,
    build_sandbox_headers,
    build_sandbox_offer_request,
    duration_to_minutes,
    fetch_sandbox_offer_records,
)


def _sample_response():
    return {
        "data": {
            "id": "orq_test",
            "offers": [
                {
                    "id": "off_test",
                    "owner": {"iata_code": "ZZ", "name": "Duffel Airways"},
                    "total_amount": "123.45",
                    "total_currency": "GBP",
                    "tax_amount": "20.00",
                    "tax_currency": "GBP",
                    "total_duration": "PT7H30M",
                    "expires_at": "2026-09-20T12:00:00",
                    "slices": [
                        {
                            "segments": [
                                {"departing_at": "2026-09-21T08:00:00"},
                                {"departing_at": "2026-09-21T12:00:00"},
                            ]
                        }
                    ],
                }
            ],
        }
    }


def test_build_sandbox_offer_request_uses_anonymous_one_way_search():
    payload = build_sandbox_offer_request(
        origin="lhr", destination="jfk", departure_date=date(2026, 10, 1)
    )

    assert payload["data"]["slices"] == [
        {"origin": "LHR", "destination": "JFK", "departure_date": "2026-10-01"}
    ]
    assert payload["data"]["passengers"] == [{"type": "adult"}]


def test_sandbox_headers_reject_live_tokens():
    assert build_sandbox_headers("duffel_test_example")["Duffel-Version"] == "v2"
    with pytest.raises(ValueError, match="test token"):
        build_sandbox_headers("duffel_live_example")


def test_duration_to_minutes_handles_days_hours_and_minutes():
    assert duration_to_minutes("P1DT2H30M") == 1590
    assert duration_to_minutes(None) is None


def test_fetch_sandbox_offer_records_normalizes_offer_without_network_call():
    calls = []

    def fake_post(url, headers, payload):
        calls.append((url, headers, payload))
        return _sample_response()

    records = fetch_sandbox_offer_records(
        "duffel_test_example",
        origin="LHR",
        destination="JFK",
        departure_date=date(2026, 10, 1),
        post_json=fake_post,
    )

    assert calls[0][0] == DUFFEL_OFFER_REQUESTS_URL
    assert records == [
        {
            "offer_request_id": "orq_test",
            "offer_id": "off_test",
            "origin_iata": "LHR",
            "destination_iata": "JFK",
            "departure_date": "2026-10-01",
            "cabin_class": "economy",
            "owner_iata": "ZZ",
            "owner_name": "Duffel Airways",
            "total_amount": "123.45",
            "total_currency": "GBP",
            "tax_amount": "20.00",
            "tax_currency": "GBP",
            "segment_count": 2,
            "stop_count": 1,
            "journey_duration_minutes": 450,
            "first_departing_at": "2026-09-21T08:00:00",
            "last_expires_at": "2026-09-20T12:00:00",
            "source": "duffel_test",
            "environment": "test",
        }
    ]
