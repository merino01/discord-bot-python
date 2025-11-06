"""
Authentication middleware for API.
"""

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from settings import api_key

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(key: str = Security(api_key_header)) -> str:
    """
    Verify that the API key is valid.

    Args:
        key: API key from request header

    Returns:
        The validated API key

    Raises:
        HTTPException: If API key is invalid or missing
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key not configured on server",
        )

    if not key or key != api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API key"
        )

    return key
