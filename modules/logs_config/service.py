from typing import List, Optional
from database import Database
from modules.core import logger
from .models import LogConfigType, LogConfig


class LogsConfigService:
    def __init__(self):
        self.db = Database()

    def get_all(self) -> tuple[Optional[List[LogConfig]], Optional[str]]:
        try:
            rows = self.db.select("SELECT * FROM logs")
            log_configs = [LogConfig(**row) for row in rows]
            return log_configs, None
        except Exception as e:
            error = str(e)
            logger.error("Error al obtener las configuraciones de logs: %s", error)
            return None, error

    def get_by_type(
        self,
        log_type: LogConfigType,
    ) -> tuple[Optional[LogConfig], Optional[str]]:
        try:
            row = self.db.single("SELECT * FROM logs WHERE type = ?", (log_type,))
            if not row:
                return None, None
            log_config = LogConfig(**row)
            return log_config, None
        except Exception as e:
            error = str(e)
            logger.error(
                "Error al obtener la configuracion de logs de tipo %s: %s",
                log_type,
                error,
            )
            return None, error

    def update(self, log_config: LogConfig) -> tuple[Optional[LogConfig], Optional[str]]:
        try:
            sql = """INSERT OR REPLACE INTO logs (type, channel_id, enabled) 
                     VALUES (?, ?, ?)"""
            params = (
                log_config.type,
                log_config.channel_id,
                log_config.enabled,
            )
            self.db.execute(sql, params)
            return log_config, None
        except Exception as e:
            error = str(e)
            logger.error(
                "Error al actualizar la configuracion de logs de tipo %s: %s",
                log_config.type,
                error,
            )
            return None, error
