"""Authentication middleware for MCP BigQuery Server.

This module provides authentication utilities supporting both:
- Bearer token authentication (legacy)
- JWT token authentication (recommended)

Use create_jwt_verifier() to set up JWT authentication with FastMCP.
"""

import logging
from pathlib import Path

from fastmcp.server.auth.providers.jwt import JWTVerifier
from mcp_bigquery.config import get_settings

logger = logging.getLogger(__name__)


def create_jwt_verifier(public_key_path: Path | str | None = None) -> JWTVerifier:
    """
    Create a JWT verifier using settings and public key file.

    This function loads JWT settings (issuer, audience) from the application configuration
    and reads the RSA public key from a PEM file to create a JWTVerifier instance.

    The JWTVerifier can be used with FastMCP's authentication system to validate
    JWT tokens in incoming requests.

    Args:
        public_key_path: Path to the public key file. If None, defaults to "credentials/public_key.pem"

    Returns:
        JWTVerifier instance configured for the application

    Raises:
        FileNotFoundError: If the public key file doesn't exist
        ValueError: If the public key file is empty or invalid

    Example:
        ```python
        from mcp_bigquery.auth import create_jwt_verifier

        # Create verifier with default public key path
        verifier = create_jwt_verifier()

        # Create verifier with custom public key path
        verifier = create_jwt_verifier("path/to/public_key.pem")

        # Use with FastMCP server
        mcp = FastMCP("My Server", auth=verifier)
        ```
    """
    settings = get_settings()

    # Default to credentials/public_key.pem if no path provided
    if public_key_path is None:
        public_key_path = settings.jwt_public_key_path
    elif isinstance(public_key_path, str):
        public_key_path = Path(public_key_path)

    # Read the public key from file
    if not public_key_path.exists():
        raise FileNotFoundError(f"Public key file not found: {public_key_path}")

    try:
        public_key_content = public_key_path.read_text().strip()
        if not public_key_content:
            raise ValueError(f"Public key file is empty: {public_key_path}")
    except Exception as e:
        raise ValueError(f"Failed to read public key file {public_key_path}: {e}")

    # Create the JWT verifier
    verifier = JWTVerifier(
        public_key=public_key_content,
        issuer=settings.jwt_issuer,
        audience=settings.jwt_audience,
    )

    logger.info(
        f"JWT verifier created with issuer='{settings.jwt_issuer}' and audience='{settings.jwt_audience}'"
    )
    return verifier
