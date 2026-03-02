"""Configuration module for MCP GPT Researcher server."""

import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration for MCP GPT Researcher server."""

    def __init__(self) -> None:
        """Initialize configuration from environment variables."""
        self.gpt_researcher_base_url: str = os.getenv(
            "GPT_RESEARCHER_BASE_URL", "http://localhost:10305"
        )
        port_str = os.getenv("SERVER_PORT")
        self.server_port: Optional[int] = int(port_str) if port_str else None
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")

    def get_api_url(self, endpoint: str) -> str:
        """Build full URL for GPT Researcher API endpoint."""
        base = self.gpt_researcher_base_url.rstrip("/")
        endpoint = endpoint.lstrip("/")
        return f"{base}/{endpoint}"

    def validate(self) -> bool:
        """Validate configuration."""
        if not self.gpt_researcher_base_url:
            return False
        return True


def get_config() -> Config:
    """Get configuration instance."""
    return Config()
