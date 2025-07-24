from typing import List, Optional
from database.database import Database
from modules.core import logger
from .models import AutomaticMessage

class AutomaticMessagesService:
    def __init__(self):
        self.db = Database()

    def get_all(self) -> tuple[Optional[List[AutomaticMessage]], Optional[str]]:
        try:
            rows = self.db.select("SELECT * FROM automatic_messages")
            automatic_messages = [AutomaticMessage(**row) for row in rows]
            return automatic_messages, None
        except Exception as e:
            error = str(e)
            logger.error("Error al obtener los mensajes automáticos: %s", error)
            return None, error

    def get_by_id(
        self, automatic_message_id: str,
    ) -> tuple[Optional[AutomaticMessage], Optional[str]]:
        try:
            row = self.db.single("SELECT * FROM automatic_messages WHERE id = ?", (automatic_message_id,))
            if not row:
                return None, None
            automatic_message = AutomaticMessage(**row)
            return automatic_message, None
        except Exception as e:
            error = str(e)
            logger.error("Error al obtener el mensaje automático: %s", error)
            return None, error

    def get_by_channel_id(
        self, channel_id: int,
    ) -> tuple[Optional[List[AutomaticMessage]], Optional[str]]:
        try:
            rows = self.db.select("SELECT * FROM automatic_messages WHERE channel_id = ?", (channel_id,))
            automatic_messages = [AutomaticMessage(**row) for row in rows]
            return automatic_messages, None
        except Exception as e:
            error = str(e)
            logger.error("Error al obtener los mensajes automáticos: %s", error)
            return None, error

    def add(self, automatic_message: AutomaticMessage) -> tuple[Optional[AutomaticMessage], Optional[str]]:
        try:
            sql = """INSERT INTO automatic_messages 
                     (id, channel_id, text, interval, interval_unit, hour, minute) 
                     VALUES (?, ?, ?, ?, ?, ?, ?)"""
            params = (
                automatic_message.id,
                automatic_message.channel_id,
                automatic_message.text,
                automatic_message.interval,
                automatic_message.interval_unit,
                automatic_message.hour,
                automatic_message.minute
            )
            self.db.execute(sql, params)
            return automatic_message, None
        except Exception as e:
            error = str(e)
            logger.error("Error al crear el mensaje automático: %s", error)
            return None, error

    def delete_by_id(self, automatic_message_id: str) -> tuple[Optional[int], Optional[str]]:
        try:
            self.db.execute("DELETE FROM automatic_messages WHERE id = ?", (automatic_message_id,))
            return 1, None
        except Exception as e:
            error = str(e)
            logger.error("Error al eliminar el mensaje automático: %s", error)
            return None, error
