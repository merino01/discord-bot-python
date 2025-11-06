"""
FastAPI application for Discord bot REST API.
"""

from fastapi import FastAPI
from api.routes_clans import router as clans_router
from api.routes_health import router as health_router

app = FastAPI(
    title="Discord Bot API",
    description="REST API for Discord bot management and data access",
    version="1.0.0",
)

# Register routers
app.include_router(health_router)
app.include_router(clans_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Discord Bot API", "docs": "/docs", "version": "1.0.0"}
