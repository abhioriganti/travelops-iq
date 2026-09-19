"""Small, dependency-free client for Duffel sandbox flight-offer snapshots.

TravelOpsIQ uses this module only with a ``duffel_test_`` token.  It creates a
single anonymous offer request and normalizes the returned offers for a RAW
landing table.  It deliberately does not create orders, collect payment data,
or send employee, trip, or booking data to Duffel.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable, Mapping
from datetime import date, timedelta
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen


DUFFEL_OFFER_REQUESTS_URL = "https://api.duffel.com/air/offer_requests"
DUFFEL_API_VERSION = "v2"
DEFAULT_SANDBOX_SEARCH = {
    "origin": "LHR",
    "destination": "JFK",
    # Duffel requires a future date even in its test environment.
    "departure_date": date.today() + timedelta(days=30),
    "cabin_class": "economy",
}
_IATA_CODE = re.compile(r"^[A-Z]{3}$")
_ISO_DURATION = re.compile(
    r"^P(?:(?P<days>\d+)D)?(?:T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?)?$"
)


def _normalize_iata_code(value: str, field_name: str) -> str:
    normalized = value.strip().upper()
    if not _IATA_CODE.fullmatch(normalized):
        raise ValueError(f"{field_name} must be a three-letter IATA code")
    return normalized


def build_sandbox_offer_request(
    *, origin: str, destination: str, departure_date: date, cabin_class: str = "economy"
) -> dict[str, Any]:
    """Build a minimal anonymous, one-way Duffel sandbox offer request."""
    normalized_origin = _normalize_iata_code(origin, "origin")
    normalized_destination = _normalize_iata_code(destination, "destination")
    if normalized_origin == normalized_destination:
        raise ValueError("origin and destination must differ")
    if cabin_class not in {"economy", "premium_economy", "business", "first"}:
        raise ValueError("cabin_class must be economy, premium_economy, business, or first")

    return {
        "data": {
            "cabin_class": cabin_class,
            "slices": [
                {
                    "origin": normalized_origin,
                    "destination": normalized_destination,
                    "departure_date": departure_date.isoformat(),
                }
            ],
            "passengers": [{"type": "adult"}],
        }
    }


def build_sandbox_headers(access_token: str) -> dict[str, str]:
    """Return API headers and reject a live token in this sandbox-only module."""
    token = access_token.strip()
    if not token.startswith("duffel_test_"):
        raise ValueError("DUFFEL_ACCESS_TOKEN must be a Duffel test token (duffel_test_...)")
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Duffel-Version": DUFFEL_API_VERSION,
        "Authorization": f"Bearer {token}",
    }


def _post_json(url: str, headers: Mapping[str, str], payload: Mapping[str, Any]) -> Mapping[str, Any]:
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=dict(headers),
        method="POST",
    )
    try:
        with urlopen(request, timeout=30) as response:  # noqa: S310 - fixed Duffel API host
            return json.load(response)
    except HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Duffel request failed with HTTP {error.code}: {details}") from error


def duration_to_minutes(value: str | None) -> int | None:
    """Convert Duffel's ISO-8601 duration to minutes without another package."""
    if value is None:
        return None
    match = _ISO_DURATION.fullmatch(value)
    if not match:
        raise ValueError(f"Unsupported ISO-8601 duration: {value!r}")
    parts = {name: int(number or 0) for name, number in match.groupdict().items()}
    return parts["days"] * 1440 + parts["hours"] * 60 + parts["minutes"]


def _first_segment(offer: Mapping[str, Any]) -> Mapping[str, Any]:
    slices = offer.get("slices")
    if not isinstance(slices, list) or not slices:
        raise ValueError("Duffel offer is missing slices")
    first_slice = slices[0]
    if not isinstance(first_slice, Mapping):
        raise ValueError("Duffel offer contains an invalid slice")
    segments = first_slice.get("segments")
    if not isinstance(segments, list) or not segments or not isinstance(segments[0], Mapping):
        raise ValueError("Duffel offer is missing segments")
    return segments[0]


def normalize_offer_records(
    response: Mapping[str, Any],
    *,
    origin: str,
    destination: str,
    departure_date: date,
    cabin_class: str,
) -> list[dict[str, Any]]:
    """Extract a deliberately narrow, non-personal snapshot from Duffel data."""
    data = response.get("data")
    if not isinstance(data, Mapping):
        raise ValueError("Duffel response is missing a data object")
    offer_request_id = data.get("id")
    offers = data.get("offers")
    if not isinstance(offer_request_id, str) or not isinstance(offers, list):
        raise ValueError("Duffel response is missing an offer request ID or offers")

    records: list[dict[str, Any]] = []
    for offer in offers:
        if not isinstance(offer, Mapping):
            raise ValueError("Duffel response contains an invalid offer")
        owner = offer.get("owner")
        if not isinstance(owner, Mapping):
            raise ValueError("Duffel offer is missing its owner")
        first_segment = _first_segment(offer)
        slices = offer["slices"]
        segment_count = sum(
            len(item.get("segments", [])) for item in slices if isinstance(item, Mapping)
        )
        records.append(
            {
                "offer_request_id": offer_request_id,
                "offer_id": offer.get("id"),
                "origin_iata": _normalize_iata_code(origin, "origin"),
                "destination_iata": _normalize_iata_code(destination, "destination"),
                "departure_date": departure_date.isoformat(),
                # Cabin class belongs to the offer request contract. The API
                # does not consistently repeat it on each returned offer.
                "cabin_class": cabin_class,
                "owner_iata": owner.get("iata_code"),
                "owner_name": owner.get("name"),
                "total_amount": offer.get("total_amount"),
                "total_currency": offer.get("total_currency"),
                "tax_amount": offer.get("tax_amount"),
                "tax_currency": offer.get("tax_currency"),
                "segment_count": segment_count,
                "stop_count": max(segment_count - 1, 0),
                "journey_duration_minutes": duration_to_minutes(offer.get("total_duration")),
                "first_departing_at": first_segment.get("departing_at"),
                "last_expires_at": offer.get("expires_at"),
                "source": "duffel_test",
                "environment": "test",
            }
        )

    return records


def fetch_sandbox_offer_records(
    access_token: str,
    *,
    origin: str = DEFAULT_SANDBOX_SEARCH["origin"],
    destination: str = DEFAULT_SANDBOX_SEARCH["destination"],
    departure_date: date = DEFAULT_SANDBOX_SEARCH["departure_date"],
    cabin_class: str = DEFAULT_SANDBOX_SEARCH["cabin_class"],
    post_json: Callable[[str, Mapping[str, str], Mapping[str, Any]], Mapping[str, Any]] = _post_json,
) -> list[dict[str, Any]]:
    """Create one Duffel test offer request and normalize its offer records."""
    payload = build_sandbox_offer_request(
        origin=origin,
        destination=destination,
        departure_date=departure_date,
        cabin_class=cabin_class,
    )
    response = post_json(DUFFEL_OFFER_REQUESTS_URL, build_sandbox_headers(access_token), payload)
    return normalize_offer_records(
        response,
        origin=origin,
        destination=destination,
        departure_date=departure_date,
        cabin_class=cabin_class,
    )
