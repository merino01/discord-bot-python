"""Logs configs Service Module"""

from typing import List, Optional
from database import db
from modules.core import logger
from .models import LogConfigType, LogConfig

class LogsConfigService:
    """Service class for managing logs configs."""

    @staticmethod
    def get_all() -> tuple[Optional[List[LogConfig]], Optional[str]]:
        """
        Fetch all logs from the database.
        :return: List of logs configs.
        """
        log_configs, error = db.select(
            model=LogConfig,
            table="logs",
            columns=["*"]
        )
        if error:
            logger.error("Error al obtener las configuraciones de logs: %s", error)
            return None, error
        return log_configs, None


    @staticmethod
    def get_by_type(log_type: LogConfigType) -> tuple[Optional[LogConfig], Optional[str]]:
        """
        Fetch logs by type from the database.
        :return: Logs configs by type.
        """
        log_config, error = db.select_one(
            model=LogConfig,
            table="logs",
            columns=["*"],
            contitions={"type": log_type}
        )
        if error:
            logger.error(
                "Error al obtener la configuracion de logs de tipo %s: %s",
                log_type,
                error
            )
            return None, error
        return log_config, None


    @staticmethod
    def update(log_config: LogConfig) -> tuple[Optional[LogConfig], Optional[str]]:
        """
        Add a new log config to the database.
        :param log_config: Log config object to add.
        """
        _, error = db.upsert(
            table="logs",
            data={
                "type": log_config.type,
                "channel_id": log_config.channel_id,
                "enabled": log_config.enabled
            },
            primary_key="type"
        )
        if error:
            logger.error(
                "Error al actualizar la configuracion de logs de tipo %s: %s",
                log_config.type,
                error
            )
            return None, error
        return log_config, None
