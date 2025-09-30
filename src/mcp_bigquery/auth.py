"""Authentication middleware for MCP BigQuery Server."""

import logging
from functools import wraps
from typing import Any, Callable, Optional

from mcp_bigquery.config import get_settings

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Raised when authentication fails."""

    pass


def extract_bearer_token(auth_header: Optional[str]) -> Optional[str]:
    """
    Extract bearer token from Authorization header.

    Args:
        auth_header: The Authorization header value (e.g., "Bearer <token>")

    Returns:
        The extracted token, or None if extraction fails
    """
    if not auth_header:
        return None

    parts = auth_header.split()
    if len(parts) != 2:
        return None

    scheme, token = parts
    if scheme.lower() != "bearer":
        return None

    return token


def validate_bearer_token(token: Optional[str]) -> bool:
    """
    Validate a bearer token against the configured token.

    Args:
        token: The token to validate

    Returns:
        True if the token is valid, False otherwise
    """
    if not token:
        logger.warning("Authentication attempt with missing token")
        return False

    settings = get_settings()
    is_valid = token == settings.bearer_token

    if is_valid:
        logger.info("Authentication successful")
    else:
        logger.warning("Authentication failed: Invalid bearer token")

    return is_valid


def authenticate_request(auth_header: Optional[str]) -> bool:
    """
    Authenticate a request using the Authorization header.

    Args:
        auth_header: The Authorization header value

    Returns:
        True if authentication succeeds

    Raises:
        AuthenticationError: If authentication fails
    """
    token = extract_bearer_token(auth_header)

    if not validate_bearer_token(token):
        raise AuthenticationError("Invalid or missing bearer token")

    return True


def require_auth(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to require authentication for MCP tool functions.

    This decorator expects the function to have access to request context
    that includes authorization headers.

    Args:
        func: The function to decorate

    Returns:
        Decorated function that requires authentication
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Try to extract auth from context
        # Note: In FastMCP, authentication is typically handled at the transport level
        # This is a placeholder for when we integrate with actual MCP context
        auth_header = kwargs.get("_auth_header")

        if auth_header:
            try:
                authenticate_request(auth_header)
            except AuthenticationError as e:
                logger.error(f"Authentication error in {func.__name__}: {e}")
                raise

        return func(*args, **kwargs)

    return wrapper


def get_auth_error_response(message: str = "Authentication required") -> dict[str, Any]:
    """
    Create a standardized error response for authentication failures.

    Args:
        message: The error message

    Returns:
        Error response dictionary in MCP format
    """
    return {
        "error": {
            "code": "UNAUTHORIZED",
            "message": message,
        }
    }
