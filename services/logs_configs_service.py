"""Logs configs Service Module"""

from typing import List
from database import db
from database.models import LogConfigType, LogConfig
from utils.logger import logger

class LogsConfigService:
    """Service class for managing logs configs."""

    @staticmethod
    def get_all() -> List[LogConfig]:
        """
        Fetch all logs from the database.
        :return: List of logs configs.
        """
        return db.query(
            model=LogConfig,
            query="SELECT * FROM logs"
        )

    @staticmethod
    def get_by_type(log_type: LogConfigType) -> LogConfig | None:
        """
        Fetch logs by type from the database.
        :return: Logs configs by type.
        """
        return db.fetch_one(
            model=LogConfig,
            query="SELECT * FROM logs WHERE type = ?",
            params=(log_type,)
        )

    @staticmethod
    def update(log_config: LogConfig) -> bool:
        """
        Add a new log config to the database.
        :param log_config: Log config object to add.
        """
        ok = db.upsert(
            table="logs",
            data={
                "type": log_config.type,
                "channel_id": log_config.channel_id,
                "enabled": log_config.enabled
            },
            primary_key="type"
        )
        if not ok:
            logger.error("Error actualizando el log config de tipo %s", log_config.type)
        else:
            logger.info("Log config de tipo %s actualizado", log_config.type)
        return ok
