"""Smoke-check the MCP service identity without starting an MCP client."""

from __future__ import annotations

import json
import sys
from pathlib import Path

# A directly executed script starts with scripts/ on sys.path. Add the project
# root so the source package is importable without requiring a global install.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.travel_analytics.mcp.server import get_product_funnel_summary


def main() -> None:
    # These dates cover the deterministic synthetic-data demo period.
    result = get_product_funnel_summary("2026-06-01", "2026-08-31")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
