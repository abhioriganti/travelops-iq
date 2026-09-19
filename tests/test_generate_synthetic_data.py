import json
import tempfile
from pathlib import Path

import pandas as pd

from src.travel_analytics.generate_synthetic_data import generate_data


def test_generator_creates_connected_source_data():
    # Do not use pytest's default temporary folder. On managed Windows devices it
    # can be inaccessible; this parent is created by the developer running tests.
    test_workspace_parent = Path("test_runs")
    test_workspace_parent.mkdir(exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="generator_", dir=test_workspace_parent) as directory:
        output_dir = Path(directory)
        counts = generate_data(output_dir, seed=7, employee_count=10, trip_count=25)

        trips = pd.read_csv(output_dir / "trips.csv")
        events = pd.read_csv(output_dir / "booking_events.csv")
        policy_evaluations = pd.read_csv(output_dir / "policy_evaluations.csv")
        manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))

        assert counts["employees"] == 10
        assert counts["trips"] == 25
        assert trips["trip_id"].is_unique
        assert policy_evaluations["trip_id"].nunique() == 25
        assert set(trips["trip_id"]).issubset(set(events["trip_id"].dropna()))
        assert manifest["row_counts"] == counts
