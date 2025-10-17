"""
Configuration settings for the MCP Streamlit Chatbot.
"""
import os
from typing import Dict, List, Optional
import importlib
import pydantic
from pydantic import Field

# Try to import BaseSettings in a way that supports both pydantic v2 and v1.
# - pydantic v2: BaseSettings is provided by the separate package `pydantic-settings`
# - pydantic v1: BaseSettings is available directly in pydantic
try:
    # Preferred for pydantic v2 (if pydantic-settings is installed)
    BaseSettings = importlib.import_module("pydantic_settings").BaseSettings
except Exception:
    # fallback: if running pydantic v1, import from pydantic
    try:
        if getattr(pydantic, "__version__", "").startswith("1."):
            from pydantic import BaseSettings  # type: ignore
        else:
            # pydantic v2 detected but pydantic-settings isn't installed
            raise ImportError(
                "pydantic v2 detected but package `pydantic-settings` is not installed. "
                "Install it by adding `pydantic-settings` to your requirements.txt (or pin pydantic<2)."
            )
    except Exception as e:
        # Re-raise with clear guidance
        raise ImportError(
            "Failed to import BaseSettings. If you're using Pydantic v2, please install "
            "`pydantic-settings` (pip install pydantic-settings) or pin pydantic to <2 in requirements.txt. "
            f"Original error: {e}"
        ) from e

from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-5", env="OPENAI_MODEL")
    openai_max_tokens: int = Field(default=1000, env="OPENAI_MAX_TOKENS")
    openai_temperature: float = Field(default=0.7, env="OPENAI_TEMPERATURE")

    # MCP Configuration
    mcp_timeout: int = Field(default=30, env="MCP_TIMEOUT")
    mcp_retry_attempts: int = Field(default=3, env="MCP_RETRY_ATTEMPTS")
    mcp_servers_config_path: str = Field(default="config/mcp_servers.json", env="MCP_SERVERS_CONFIG")

    # Streamlit Configuration
    app_title: str = Field(default="MCP Server Tester", env="APP_TITLE")
    app_icon: str = Field(default="🤖", env="APP_ICON")
    debug_mode: bool = Field(default=False, env="DEBUG_MODE")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
try:
    settings = Settings()
except Exception as e:
    print(f"Error loading settings: {e}")
    print("Please make sure your .env file is configured correctly")
    # Create settings with defaults if loading fails
    settings = Settings(openai_api_key="not-set")


# Default MCP server configurations
DEFAULT_MCP_SERVERS = [
    {
        "name": "filesystem",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
        "description": "File system operations server",
        "enabled": True
    },
    {
        "name": "brave-search",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-brave-search"],
        "description": "Web search using Brave Search API",
        "enabled": False,
        "env": {"BRAVE_API_KEY": ""}
    },
    {
        "name": "git",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-git", "--repository", "."],
        "description": "Git repository operations",
        "enabled": True
    }
]


def get_mcp_servers_config() -> List[Dict]:
    """Get MCP servers configuration from file or defaults."""
    import json

    try:
        with open(settings.mcp_servers_config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Create default config file
        os.makedirs(os.path.dirname(settings.mcp_servers_config_path), exist_ok=True)
        with open(settings.mcp_servers_config_path, 'w') as f:
            json.dump(DEFAULT_MCP_SERVERS, f, indent=2)
        return DEFAULT_MCP_SERVERS
    except Exception as e:
        print(f"Error loading MCP servers config: {e}")
        return DEFAULT_MCP_SERVERS


def save_mcp_servers_config(servers: List[Dict]) -> bool:
    """Save MCP servers configuration to file."""
    import json

    try:
        os.makedirs(os.path.dirname(settings.mcp_servers_config_path), exist_ok=True)
        with open(settings.mcp_servers_config_path, 'w') as f:
            json.dump(servers, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving MCP servers config: {e}")
        return False 
