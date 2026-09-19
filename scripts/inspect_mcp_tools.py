"""Start the local MCP server and list its advertised tools via stdio."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYTHON = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"


async def main() -> None:
    parameters = StdioServerParameters(
        command=str(PYTHON),
        args=["-m", "src.travel_analytics.mcp.server"],
        cwd=PROJECT_ROOT,
    )
    async with stdio_client(parameters) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools = await session.list_tools()
            print("MCP protocol check passed.")
            for tool in tools.tools:
                print(f"- {tool.name}")


if __name__ == "__main__":
    asyncio.run(main())
