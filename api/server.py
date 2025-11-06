"""
API server runner for Discord bot.
Manages the FastAPI server lifecycle.
"""

import asyncio
import uvicorn
from modules.core import logger
from settings import api_port, api_enabled, api_key


class APIServer:
    """Manages the API server lifecycle"""

    def __init__(self):
        self.config = uvicorn.Config("api.app:app", host="0.0.0.0", port=api_port, log_level="info")
        self.server = uvicorn.Server(self.config)
        self._task = None

    async def start(self):
        """Start the API server in the background"""
        if not api_enabled:
            logger.info("API deshabilitada, no se iniciará el servidor")
            return

        if not api_key:
            logger.warning(
                "API habilitada pero no se ha configurado api_key. La API no será segura."
            )

        logger.info(f"Iniciando API en puerto {api_port}")
        self._task = asyncio.create_task(self.server.serve())
        logger.info(f"API iniciada en http://0.0.0.0:{api_port}")
        logger.info(f"Documentación disponible en http://0.0.0.0:{api_port}/docs")

    async def stop(self):
        """Stop the API server"""
        if self._task and not self._task.done():
            logger.info("Deteniendo API...")
            self.server.should_exit = True
            await self._task
            logger.info("API detenida")
