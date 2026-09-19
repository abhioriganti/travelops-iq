"""Retrieve current hotel-property discovery records from Geoapify Places.

This module queries only version-controlled city coordinates. It returns
property discovery metadata, not hotel availability, room rates, or booking
inventory, and it contains no Snowflake or traveler-level data access.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from typing import Any
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen

from src.travel_analytics.weather import get_city_location


GEOAPIFY_PLACES_URL = "https://api.geoapify.com/v2/places"
HOTEL_CATEGORY = "accommodation.hotel"
DEFAULT_RADIUS_METERS = 10_000
DEFAULT_LIMIT = 50


def build_hotel_places_url(
    city_code: str,
    api_key: str,
    *,
    radius_meters: int = DEFAULT_RADIUS_METERS,
    limit: int = DEFAULT_LIMIT,
) -> str:
    """Build a bounded Geoapify hotel-property discovery request."""
    if not api_key.strip():
        raise ValueError("GEOAPIFY_API_KEY cannot be empty")
    if radius_meters <= 0:
        raise ValueError("radius_meters must be positive")
    if not 1 <= limit <= 500:
        raise ValueError("limit must be between 1 and 500")

    location = get_city_location(city_code)
    parameters = urlencode(
        {
            "categories": HOTEL_CATEGORY,
            "filter": f"circle:{location.longitude},{location.latitude},{radius_meters}",
            "bias": f"proximity:{location.longitude},{location.latitude}",
            "limit": limit,
            "apiKey": api_key,
        }
    )
    return f"{GEOAPIFY_PLACES_URL}?{parameters}"


def _read_json(url: str, timeout_seconds: float) -> Mapping[str, Any]:
    try:
        with urlopen(url, timeout=timeout_seconds) as response:  # noqa: S310 - fixed Geoapify host
            return json.load(response)
    except HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Geoapify request failed with HTTP {error.code}: {details}") from error


def _coordinates(feature: Mapping[str, Any]) -> tuple[float, float]:
    geometry = feature.get("geometry")
    if not isinstance(geometry, Mapping) or geometry.get("type") != "Point":
        raise ValueError("Geoapify feature is missing Point geometry")
    coordinates = geometry.get("coordinates")
    if not isinstance(coordinates, list) or len(coordinates) < 2:
        raise ValueError("Geoapify feature is missing coordinates")
    return float(coordinates[0]), float(coordinates[1])


def normalize_hotel_property_records(
    city_code: str, response: Mapping[str, Any]
) -> list[dict[str, Any]]:
    """Normalize selected place fields and exclude non-property metadata."""
    features = response.get("features")
    if not isinstance(features, list):
        raise ValueError("Geoapify response is missing a features list")

    location = get_city_location(city_code)
    records: list[dict[str, Any]] = []
    for feature in features:
        if not isinstance(feature, Mapping):
            raise ValueError("Geoapify response contains an invalid feature")
        properties = feature.get("properties")
        if not isinstance(properties, Mapping):
            raise ValueError("Geoapify feature is missing properties")
        place_id = properties.get("place_id")
        if not isinstance(place_id, str) or not place_id:
            raise ValueError("Geoapify feature is missing place_id")
        longitude, latitude = _coordinates(feature)
        categories = properties.get("categories", [])
        if not isinstance(categories, list):
            raise ValueError("Geoapify feature has invalid categories")

        records.append(
            {
                "destination_city_code": location.code,
                "destination_city_name": location.name,
                "place_id": place_id,
                "property_name": properties.get("name"),
                "formatted_address": properties.get("formatted"),
                "country_code": properties.get("country_code"),
                "property_latitude": latitude,
                "property_longitude": longitude,
                "distance_meters": properties.get("distance"),
                "categories": ",".join(str(category) for category in categories),
                "has_website": bool(properties.get("website")),
                "source": "geoapify_places",
            }
        )
    return records


def fetch_hotel_properties(
    city_code: str,
    api_key: str,
    *,
    radius_meters: int = DEFAULT_RADIUS_METERS,
    limit: int = DEFAULT_LIMIT,
    timeout_seconds: float = 20.0,
    request_json: Callable[[str, float], Mapping[str, Any]] = _read_json,
) -> list[dict[str, Any]]:
    """Fetch a bounded set of current hotel properties near one city center."""
    url = build_hotel_places_url(
        city_code, api_key, radius_meters=radius_meters, limit=limit
    )
    response = request_json(url, timeout_seconds)
    return normalize_hotel_property_records(city_code, response)
