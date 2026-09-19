from urllib.parse import parse_qs, urlparse

import pytest

from src.travel_analytics.geoapify import (
    GEOAPIFY_PLACES_URL,
    build_hotel_places_url,
    fetch_hotel_properties,
)


def _sample_response():
    return {
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "place_id": "place_chi_1",
                    "name": "Example Chicago Hotel",
                    "formatted": "1 Example St, Chicago, Illinois, United States",
                    "country_code": "us",
                    "distance": 312.4,
                    "categories": ["accommodation.hotel"],
                    "website": "https://example.test",
                },
                "geometry": {"type": "Point", "coordinates": [-87.63, 41.88]},
            }
        ]
    }


def test_build_hotel_places_url_uses_bounded_hotel_search():
    parsed_url = urlparse(build_hotel_places_url("CHI", "geoapify-test-key"))
    parameters = parse_qs(parsed_url.query)

    assert f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}" == GEOAPIFY_PLACES_URL
    assert parameters["categories"] == ["accommodation.hotel"]
    assert parameters["filter"] == ["circle:-87.6298,41.8781,10000"]
    assert parameters["limit"] == ["50"]


def test_fetch_hotel_properties_normalizes_selected_property_metadata():
    records = fetch_hotel_properties(
        "CHI",
        "geoapify-test-key",
        request_json=lambda _url, _timeout: _sample_response(),
    )

    assert records == [
        {
            "destination_city_code": "CHI",
            "destination_city_name": "Chicago",
            "place_id": "place_chi_1",
            "property_name": "Example Chicago Hotel",
            "formatted_address": "1 Example St, Chicago, Illinois, United States",
            "country_code": "us",
            "property_latitude": 41.88,
            "property_longitude": -87.63,
            "distance_meters": 312.4,
            "categories": "accommodation.hotel",
            "has_website": True,
            "source": "geoapify_places",
        }
    ]


def test_build_hotel_places_url_rejects_invalid_limit():
    with pytest.raises(ValueError, match="limit"):
        build_hotel_places_url("CHI", "key", limit=501)
