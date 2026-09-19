"""Generate deterministic, synthetic source data for TravelOpsIQ.

The data is intentionally fictional. Its relationships model a travel-product
journey (search -> booking -> trip -> expense/support/policy) without using
any real traveler, company, supplier, or customer data.
"""

from __future__ import annotations

import argparse
import json
import random
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd


DEFAULT_END_DATE = date(2026, 9, 1)
DEPARTMENTS = ["Sales", "Engineering", "Product", "Finance", "Operations"]
ORIGINS = ["AUS", "BOS", "CHI", "DAL", "DEN", "LAX", "NYC", "SEA"]
DESTINATIONS = ["AMS", "ATL", "LON", "MIA", "SFO", "TYO", "WAS"]
AIRLINES = ["AeroLink", "CloudJet", "Northstar Air", "Skyward"]
HOTEL_CHAINS = ["Harbor Hotels", "Northstar Suites", "Pioneer Inns", "Urban Stay"]
SUPPORT_REASONS = ["itinerary_change", "flight_disruption", "receipt_help", "policy_question"]
POLICY_RULES = ["advance_purchase", "cabin_class", "hotel_rate_cap", "preferred_supplier"]


def _timestamp(day: date, hour: int, rng: random.Random) -> datetime:
    """Return a realistic UTC-naive timestamp on a selected day."""
    return datetime.combine(day, datetime.min.time()) + timedelta(
        hours=hour,
        minutes=rng.randrange(0, 60),
        seconds=rng.randrange(0, 60),
    )


def _write_csv(frame: pd.DataFrame, output_dir: Path, filename: str) -> int:
    output_path = output_dir / filename
    frame.to_csv(output_path, index=False)
    return len(frame)


def generate_data(
    output_dir: Path,
    *,
    seed: int = 42,
    employee_count: int = 250,
    trip_count: int = 1_200,
    end_date: date = DEFAULT_END_DATE,
) -> dict[str, int]:
    """Generate a connected set of source tables and return their row counts."""
    if employee_count < 1 or trip_count < 1:
        raise ValueError("employee_count and trip_count must both be positive")

    rng = random.Random(seed)
    output_dir.mkdir(parents=True, exist_ok=True)
    start_date = end_date - timedelta(days=89)

    employees = pd.DataFrame(
        [
            {
                "employee_id": f"EMP{i:04d}",
                "department": rng.choice(DEPARTMENTS),
                "country_code": rng.choice(["US", "US", "US", "GB", "DE"]),
                "employee_created_at": _timestamp(start_date - timedelta(days=rng.randrange(30, 730)), 9, rng),
            }
            for i in range(1, employee_count + 1)
        ]
    )

    trips: list[dict[str, object]] = []
    policies: list[dict[str, object]] = []
    expenses: list[dict[str, object]] = []
    support_cases: list[dict[str, object]] = []
    booked_events: list[dict[str, object]] = []

    for index in range(1, trip_count + 1):
        trip_id = f"TRIP{index:06d}"
        employee_id = rng.choice(employees["employee_id"].tolist())
        booking_day = start_date + timedelta(days=rng.randrange(0, 90))
        departure_day = booking_day + timedelta(days=rng.randrange(2, 45))
        return_day = departure_day + timedelta(days=rng.randrange(1, 6))
        origin = rng.choice(ORIGINS)
        destination = rng.choice([city for city in DESTINATIONS if city != origin])
        is_in_policy = rng.random() < 0.84
        trip_status = rng.choices(
            ["completed", "booked", "cancelled"], weights=[75, 18, 7], k=1
        )[0]
        booked_cost = round(rng.uniform(220, 2_400), 2)
        session_id = f"SESSION{index:07d}"
        booking_timestamp = _timestamp(booking_day, rng.randrange(7, 21), rng)

        trips.append(
            {
                "trip_id": trip_id,
                "employee_id": employee_id,
                "booking_session_id": session_id,
                "booking_timestamp": booking_timestamp,
                "departure_date": departure_day,
                "return_date": return_day,
                "origin_city_code": origin,
                "destination_city_code": destination,
                "airline_name": rng.choice(AIRLINES),
                "hotel_chain": rng.choice(HOTEL_CHAINS),
                "booked_cost_usd": booked_cost,
                "trip_status": trip_status,
            }
        )

        policy_rule = rng.choice(POLICY_RULES)
        policies.append(
            {
                "policy_evaluation_id": f"POLICY{index:06d}",
                "trip_id": trip_id,
                "policy_rule": policy_rule,
                "policy_result": "pass" if is_in_policy else "fail",
                "is_material_violation": not is_in_policy,
                "exception_reason": None if is_in_policy else f"{policy_rule}_exception",
                "evaluated_at": booking_timestamp,
            }
        )

        for step, event_type in enumerate(
            ["search_submitted", "results_viewed", "checkout_started", "booking_confirmed"]
        ):
            booked_events.append(
                {
                    "event_id": f"EVENT{index:06d}_{step + 1}",
                    "session_id": session_id,
                    "trip_id": trip_id,
                    "employee_id": employee_id,
                    "event_type": event_type,
                    "event_timestamp": booking_timestamp + timedelta(minutes=step * rng.randrange(2, 8)),
                    "channel": rng.choice(["web", "mobile"]),
                }
            )

        if trip_status == "completed":
            for item_number in range(1, rng.randrange(1, 4)):
                category = rng.choice(["meal", "ground_transport", "hotel_incidental"])
                expenses.append(
                    {
                        "expense_id": f"EXP{index:06d}_{item_number}",
                        "trip_id": trip_id,
                        "employee_id": employee_id,
                        "expense_category": category,
                        "amount_usd": round(rng.uniform(18, 240), 2),
                        "has_receipt": rng.random() < 0.9,
                        "approval_status": rng.choices(["approved", "submitted"], weights=[80, 20], k=1)[0],
                        "submitted_at": _timestamp(return_day + timedelta(days=rng.randrange(0, 8)), 11, rng),
                    }
                )

        if rng.random() < 0.14:
            opened_at = booking_timestamp + timedelta(hours=rng.randrange(1, 72))
            resolution_hours = rng.randrange(1, 49)
            support_cases.append(
                {
                    "support_case_id": f"CASE{index:06d}",
                    "trip_id": trip_id,
                    "issue_type": rng.choice(SUPPORT_REASONS),
                    "opened_at": opened_at,
                    "resolved_at": opened_at + timedelta(hours=resolution_hours),
                    "resolution_channel": rng.choice(["ai_agent", "human_agent", "self_service"]),
                }
            )

    abandoned_events: list[dict[str, object]] = []
    for index in range(1, int(trip_count * 0.28) + 1):
        session_id = f"SESSION_ABANDONED{index:06d}"
        employee_id = rng.choice(employees["employee_id"].tolist())
        event_time = _timestamp(start_date + timedelta(days=rng.randrange(0, 90)), rng.randrange(7, 21), rng)
        for step, event_type in enumerate(["search_submitted", "results_viewed", "checkout_started"]):
            abandoned_events.append(
                {
                    "event_id": f"ABANDON{index:06d}_{step + 1}",
                    "session_id": session_id,
                    "trip_id": None,
                    "employee_id": employee_id,
                    "event_type": event_type,
                    "event_timestamp": event_time + timedelta(minutes=step * rng.randrange(2, 8)),
                    "channel": rng.choice(["web", "mobile"]),
                }
            )

    row_counts = {
        "employees": _write_csv(employees, output_dir, "employees.csv"),
        "trips": _write_csv(pd.DataFrame(trips), output_dir, "trips.csv"),
        "booking_events": _write_csv(pd.DataFrame(booked_events + abandoned_events), output_dir, "booking_events.csv"),
        "expenses": _write_csv(pd.DataFrame(expenses), output_dir, "expenses.csv"),
        "policy_evaluations": _write_csv(pd.DataFrame(policies), output_dir, "policy_evaluations.csv"),
        "support_cases": _write_csv(pd.DataFrame(support_cases), output_dir, "support_cases.csv"),
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(
            {
                "seed": seed,
                "employee_count": employee_count,
                "trip_count": trip_count,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "row_counts": row_counts,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return row_counts


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("data/generated"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--employees", type=int, default=250)
    parser.add_argument("--trips", type=int, default=1_200)
    parser.add_argument("--end-date", type=date.fromisoformat, default=DEFAULT_END_DATE)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    row_counts = generate_data(
        args.output_dir,
        seed=args.seed,
        employee_count=args.employees,
        trip_count=args.trips,
        end_date=args.end_date,
    )
    print(json.dumps({"output_dir": str(args.output_dir), "row_counts": row_counts}, indent=2))


if __name__ == "__main__":
    main()
