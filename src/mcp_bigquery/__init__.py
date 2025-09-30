"""MCP BigQuery Server - A secure MCP server for Google BigQuery."""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from mcp_bigquery.config import Settings
from mcp_bigquery.server import mcp

__all__ = ["Settings", "mcp", "__version__"]
