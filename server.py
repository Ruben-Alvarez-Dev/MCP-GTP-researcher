"""MCP Server for GPT Researcher.

This server provides MCP tools for interacting with GPT Researcher research API.
"""

import logging
import sys
from typing import Any, Dict, List, Optional

import requests
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from config import get_config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

config = get_config()
server = Server("mcp-gpt-researcher")


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="conduct_research",
            description="Conduct comprehensive research on a topic",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The research query or topic",
                    },
                    "source_type": {
                        "type": "string",
                        "description": "Type of sources to use (web, academic, all)",
                        "enum": ["web", "academic", "all"],
                    },
                    "max_sources": {
                        "type": "number",
                        "description": "Maximum number of sources to gather",
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="generate_report",
            description="Generate a comprehensive research report",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The report topic",
                    },
                    "report_format": {
                        "type": "string",
                        "description": "Format for the report",
                        "enum": ["markdown", "pdf", "html"],
                    },
                    "depth": {
                        "type": "string",
                        "description": "Report depth",
                        "enum": ["quick", "medium", "detailed"],
                    },
                },
                "required": ["topic"],
            },
        ),
        Tool(
            name="get_sources",
            description="Get sources used in research",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The original research query",
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="validate_sources",
            description="Validate research sources for reliability",
            inputSchema={
                "type": "object",
                "properties": {
                    "sources": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of source URLs to validate",
                    },
                },
                "required": ["sources"],
            },
        ),
        Tool(
            name="follow_up_research",
            description="Explore follow-up questions from initial research",
            inputSchema={
                "type": "object",
                "properties": {
                    "original_query": {
                        "type": "string",
                        "description": "The original research query",
                    },
                    "follow_up_questions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of follow-up questions",
                    },
                },
                "required": ["original_query", "follow_up_questions"],
            },
        ),
        Tool(
            name="health_check",
            description="Check if GPT Researcher API is healthy",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="quick_research",
            description="Conduct quick research with minimal sources",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The research query",
                    },
                },
                "required": ["query"],
            },
        ),
    ]


def make_api_request(
    endpoint: str,
    payload: Optional[Dict[str, Any]] = None,
    timeout: int = 60,
) -> Dict[str, Any]:
    """Make request to GPT Researcher API."""
    url = config.get_api_url(endpoint)
    try:
        response = requests.post(
            url,
            json=payload or {},
            timeout=timeout,
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        logger.error(f"Timeout requesting {url}")
        raise Exception("Request to GPT Researcher API timed out")
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error requesting {url}")
        raise Exception("Could not connect to GPT Researcher API")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        raise Exception(f"GPT Researcher API request failed: {str(e)}")


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls."""
    try:
        if name == "conduct_research":
            result = make_api_request(
                "api/research",
                {
                    "query": arguments["query"],
                    "source_type": arguments.get("source_type", "all"),
                    "max_sources": arguments.get("max_sources", 10),
                },
            )
            return [TextContent(type="text", text=str(result))]

        elif name == "generate_report":
            result = make_api_request(
                "api/report",
                {
                    "topic": arguments["topic"],
                    "report_format": arguments.get("report_format", "markdown"),
                    "depth": arguments.get("depth", "medium"),
                },
            )
            return [TextContent(type="text", text=str(result))]

        elif name == "get_sources":
            result = make_api_request(
                "api/sources",
                {"query": arguments["query"]},
            )
            return [TextContent(type="text", text=str(result))]

        elif name == "validate_sources":
            result = make_api_request(
                "api/validate",
                {"sources": arguments["sources"]},
            )
            return [TextContent(type="text", text=str(result))]

        elif name == "follow_up_research":
            result = make_api_request(
                "api/research/follow-up",
                {
                    "original_query": arguments["original_query"],
                    "follow_up_questions": arguments["follow_up_questions"],
                },
            )
            return [TextContent(type="text", text=str(result))]

        elif name == "health_check":
            result = make_api_request("health")
            return [TextContent(type="text", text=str(result))]

        elif name == "quick_research":
            result = make_api_request(
                "api/research/quick",
                {"query": arguments["query"]},
            )
            return [TextContent(type="text", text=str(result))]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Tool error: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main() -> None:
    """Main entry point."""
    logger.info("Starting MCP GPT Researcher server...")
    logger.info(f"GPT Researcher base URL: {config.gpt_researcher_base_url}")

    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
