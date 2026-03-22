#!/usr/bin/env python3
"""MCP GPT Researcher Server - Auto-discovers GPT Researcher port"""

import asyncio
import json
import logging
import os
import sys
from typing import Optional

import httpx
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SERVER_PORT = 8080

DEFAULT_PORTS = [8000, 8001, 8080]
FALLBACK_PORTS = [10305, 3000, 5000]
GPTR_ENDPOINTS = ["/docs", "/openapi.json", "/api/reports", "/"]


def discover_port(
    ports: list[int], endpoints: list[str], timeout: float = 2.0
) -> Optional[str]:
    """Scan ports for a responsive endpoint."""
    for port in ports:
        try:
            client = httpx.Client(timeout=timeout)
            for endpoint in endpoints:
                try:
                    resp = client.get(f"http://localhost:{port}{endpoint}")
                    if resp.status_code < 500:
                        logger.info(f"Discovered service on port {port}")
                        return f"http://localhost:{port}"
                except Exception:
                    continue
        except Exception:
            continue
    return None


def prompt_user(service_name: str, default_port: int) -> str:
    """Prompt user for port if not discovered."""
    try:
        user_input = input(
            f"\n⚠️  Could not find {service_name}.\n"
            f"   Default port: {default_port}\n"
            f"   Enter port number (or press Enter for default): "
        ).strip()
        if user_input:
            return f"http://localhost:{user_input}"
    except (EOFError, KeyboardInterrupt):
        pass
    return f"http://localhost:{default_port}"


def get_base_url() -> str:
    """Get base URL: env var -> discover -> prompt user -> fallback."""
    env_url = os.getenv("GPT_RESEARCHER_BASE_URL")
    if env_url:
        return env_url

    discovered = discover_port(DEFAULT_PORTS, GPTR_ENDPOINTS)
    if discovered:
        return discovered

    logger.warning("GPT Researcher not found in default ports, trying fallback...")
    discovered = discover_port(FALLBACK_PORTS, GPTR_ENDPOINTS, timeout=1.0)
    if discovered:
        return discovered

    return prompt_user("GPT Researcher", 8000)


GPTR_BASE_URL = get_base_url()
logger.info(f"Targeting GPT Researcher at: {GPTR_BASE_URL}")

mcp = FastMCP(
    "gpt-researcher-mcp", port=SERVER_PORT, sse_path="/sse", message_path="/messages/"
)


@mcp.tool()
async def gptr_deep_research(query: str, report_type: str = "research_report") -> str:
    """Conduct deep research using GPT Researcher (3-5 min)"""
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{GPTR_BASE_URL}/api/reports",
                json={"query": query, "report_type": report_type},
            )
            response.raise_for_status()
            result = response.json()

            if result.get("success") and result.get("id"):
                research_id = result["id"]
                while True:
                    await asyncio.sleep(5)
                    status_resp = await client.get(
                        f"{GPTR_BASE_URL}/api/reports/{research_id}"
                    )
                    status = status_resp.json()
                    if status.get("report", {}).get("answer"):
                        return json.dumps(status["report"], indent=2)
                    if status.get("report", {}).get("status") == "failed":
                        return json.dumps({"error": "Research failed"})

            return json.dumps(result, indent=2)
    except httpx.HTTPError as e:
        logger.error(f"GPT Researcher API error: {e}")
        return json.dumps(
            {
                "error": str(e),
                "hint": "Check that GPT Researcher is running. Set GPT_RESEARCHER_BASE_URL in .env",
            }
        )


@mcp.tool()
async def gptr_quick_search(query: str) -> str:
    """Fast search using GPT Researcher"""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{GPTR_BASE_URL}/api/reports",
                json={"query": query, "report_type": "outline_report"},
            )
            response.raise_for_status()
            result = response.json()

            if result.get("success") and result.get("id"):
                research_id = result["id"]
                for _ in range(6):
                    await asyncio.sleep(3)
                    status_resp = await client.get(
                        f"{GPTR_BASE_URL}/api/reports/{research_id}"
                    )
                    status = status_resp.json()
                    if status.get("report", {}).get("answer"):
                        return json.dumps(
                            {
                                "results": status["report"]["answer"],
                                "sources": status["report"].get("sources", []),
                            },
                            indent=2,
                        )

            return json.dumps(
                {"status": "processing", "id": result.get("id")}, indent=2
            )
    except httpx.HTTPError as e:
        logger.error(f"GPT Researcher API error: {e}")
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting GPT Researcher MCP on port {SERVER_PORT}")
    uvicorn.run(
        mcp.streamable_http_app(), host="0.0.0.0", port=SERVER_PORT, log_level="info"
    )
