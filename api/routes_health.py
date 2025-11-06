"""
Health check and status routes.
"""

from fastapi import APIRouter, Depends
from api.auth import verify_api_key
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api", tags=["health"])


class HealthResponse(BaseModel):
    """Response model for health check"""

    status: str
    timestamp: datetime
    message: str


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint (no authentication required).

    Returns:
        Health status of the API
    """
    return HealthResponse(status="healthy", timestamp=datetime.now(), message="API is running")


@router.get("/status", response_model=HealthResponse)
async def get_status(_: str = Depends(verify_api_key)):
    """
    Get API status (requires authentication).

    Returns:
        Detailed status information
    """
    return HealthResponse(
        status="ok", timestamp=datetime.now(), message="API is operational and authenticated"
    )
