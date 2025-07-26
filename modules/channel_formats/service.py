from typing import List, Optional
from database import Database
from modules.core import logger
from .models import ChannelFormat


class ChannelFormatsService:
    def __init__(self):
        self.db = Database()

    def get_all(self) -> tuple[Optional[List[ChannelFormat]], Optional[str]]:
        try:
            rows = self.db.select("SELECT * FROM channel_formats")
            channel_formats = [ChannelFormat(**row) for row in rows]
            return channel_formats, None
        except Exception as e:
            error = str(e)
            logger.error("Error al obtener los formatos de canal: %s", error)
            return None, error

    def get_by_id(self, format_id: str) -> tuple[Optional[ChannelFormat], Optional[str]]:
        try:
            row = self.db.single("SELECT * FROM channel_formats WHERE id = ?", (format_id,))
            if not row:
                return None, None
            channel_format = ChannelFormat(**row)
            return channel_format, None
        except Exception as e:
            error = str(e)
            logger.error("Error al obtener el formato de canal: %s", error)
            return None, error

    def get_one_by_channel_id(
        self, channel_id: int,
    ) -> tuple[Optional[ChannelFormat], Optional[str]]:
        try:
            row = self.db.single("SELECT * FROM channel_formats WHERE channel_id = ?", (channel_id,))
            if not row:
                return None, None
            channel_format = ChannelFormat(**row)
            return channel_format, None
        except Exception as e:
            error = str(e)
            logger.error("Error al obtener el formato de canal: %s", error)
            return None, error

    def get_all_by_channel_id(
        self, channel_id: int,
    ) -> tuple[Optional[List[ChannelFormat]], Optional[str]]:
        try:
            rows = self.db.select("SELECT * FROM channel_formats WHERE channel_id = ?", (channel_id,))
            channel_formats = [ChannelFormat(**row) for row in rows]
            return channel_formats, None
        except Exception as e:
            error = str(e)
            logger.error("Error al obtener los formatos de canal: %s", error)
            return None, error

    def add(
        self, channel_format: ChannelFormat,
    ) -> tuple[Optional[ChannelFormat], Optional[str]]:
        try:
            sql = """INSERT INTO channel_formats (id, channel_id, regex) VALUES (?, ?, ?)"""
            params = (
                str(channel_format.id),
                channel_format.channel_id,
                channel_format.regex,
            )
            self.db.execute(sql, params)
            return channel_format, None
        except Exception as e:
            error = str(e)
            logger.error("Error al crear el formato de canal: %s", error)
            return None, error

    def delete(self, channel_format: ChannelFormat) -> tuple[Optional[str], Optional[str]]:
        try:
            self.db.execute("DELETE FROM channel_formats WHERE id = ?", (str(channel_format.id),))
            return channel_format.id, None
        except Exception as e:
            error = str(e)
            logger.error("Error al eliminar el formato de canal: %s", error)
            return None, error

    def update(self, channel_format: ChannelFormat) -> Optional[str]:
        try:
            sql = """INSERT OR REPLACE INTO channel_formats (id, channel_id, regex) 
                     VALUES (?, ?, ?)"""
            params = (
                str(channel_format.id),
                channel_format.channel_id,
                channel_format.regex,
            )
            self.db.execute(sql, params)
            return None
        except Exception as e:
            error = str(e)
            logger.error("Error al actualizar el formato de canal: %s", error)
            return "Error al actualizar el formato de canal"
