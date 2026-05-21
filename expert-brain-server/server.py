"""Expert Brain MCP Server — minimal spike with 2 tools."""

import sys
import os
from datetime import datetime

_STARTUP_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "startup.log")
with open(_STARTUP_LOG, "a") as _f:
    _f.write(f"{datetime.now().isoformat()} server.py launched\n")

import asyncio

# Ensure server can import its own tools regardless of CWD
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mcp.server.stdio
from mcp.server import Server
from mcp.types import Tool, TextContent

from tools.draft_insight import draft_insight
from tools.retrieve import retrieve

server = Server("expert-brain")


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="expert_brain__draft_insight",
            description="Record a draft insight from a resolved bug or lesson learned.",
            inputSchema={
                "type": "object",
                "properties": {
                    "symptom": {"type": "string", "description": "What went wrong (1 sentence)"},
                    "root_cause": {"type": "string", "description": "Technical explanation (1-2 sentences)"},
                    "resolution": {"type": "string", "description": "Verified fix or workaround (1 sentence)"},
                    "severity": {
                        "type": "string",
                        "description": "low, medium, high, or critical",
                        "default": "medium",
                    },
                    "variants": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional 2-4 query variants — different phrasings of the same problem for broader search recall",
                    },
                },
                "required": ["symptom", "root_cause", "resolution"],
            },
        ),
        Tool(
            name="expert_brain__retrieve",
            description="Search the wiki for insights matching the query.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search terms"},
                    "top_k": {"type": "integer", "description": "Max results to return", "default": 5},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="expert_brain__promote",
            description="Promote a draft insight to a live constraint (requires hit_count >= 5).",
            inputSchema={
                "type": "object",
                "properties": {
                    "insight_id": {"type": "string", "description": "The insight ID to promote"},
                },
                "required": ["insight_id"],
            },
        ),
        Tool(
            name="expert_brain__decay",
            description="Run knowledge decay: halve hit_count for 90-day stale insights, archive 180-day ones.",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Dispatch tool calls."""
    if name == "expert_brain__draft_insight":
        result = draft_insight(
            symptom=arguments.get("symptom", ""),
            root_cause=arguments.get("root_cause", ""),
            resolution=arguments.get("resolution", ""),
            severity=arguments.get("severity", "medium"),
            variants=arguments.get("variants"),
        )
        return [TextContent(type="text", text=str(result))]

    if name == "expert_brain__retrieve":
        result = retrieve(
            query=arguments.get("query", ""),
            top_k=arguments.get("top_k", 5),
        )
        return [TextContent(type="text", text=str(result))]

    if name == "expert_brain__promote":
        from wiki_bridge import promote as wiki_promote
        result = wiki_promote(insight_id=arguments.get("insight_id", ""))
        return [TextContent(type="text", text=str(result))]

    if name == "expert_brain__decay":
        from wiki_bridge import decay as wiki_decay
        result = wiki_decay()
        return [TextContent(type="text", text=str(result))]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )


if __name__ == "__main__":
    try:
        with open(_STARTUP_LOG, "a") as _f:
            _f.write(f"{datetime.now().isoformat()} entering main()\n")
        asyncio.run(main())
    except Exception as _e:
        with open(_STARTUP_LOG, "a") as _f:
            _f.write(f"{datetime.now().isoformat()} ERROR: {_e}\n")
        raise
