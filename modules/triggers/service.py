from typing import List, Optional
from database import Database
from modules.core import logger
from .models import Trigger


class TriggersService:
    def __init__(self):
        self.db = Database()

    def get_all(self) -> tuple[Optional[List[Trigger]], Optional[str]]:
        try:
            rows = self.db.select("SELECT * FROM triggers")
            triggers = [Trigger(**row) for row in rows]
            return triggers, None
        except Exception as e:
            error = str(e)
            logger.error("Error al obtener los triggers: %s", error)
            return None, error

    def get_by_id(self, trigger_id: str) -> tuple[Optional[Trigger], Optional[str]]:
        try:
            row = self.db.single("SELECT * FROM triggers WHERE id = ?", (trigger_id,))
            if not row:
                return None, None
            trigger = Trigger(**row)
            return trigger, None
        except Exception as e:
            error = str(e)
            logger.error("Error al obtener el trigger: %s", error)
            return None, error

    def get_one_by_channel_id(
        self,
        channel_id: int,
    ) -> tuple[Optional[Trigger], Optional[str]]:
        try:
            row = self.db.single("SELECT * FROM triggers WHERE channel_id = ?", (channel_id,))
            if not row:
                return None, None
            trigger = Trigger(**row)
            return trigger, None
        except Exception as e:
            error = str(e)
            logger.error("Error al obtener el trigger: %s", error)
            return None, error

    def get_all_by_channel_id(
        self,
        channel_id: int,
    ) -> tuple[Optional[List[Trigger]], Optional[str]]:
        try:
            rows = self.db.select("SELECT * FROM triggers WHERE channel_id = ?", (channel_id,))
            triggers = [Trigger(**row) for row in rows]
            return triggers, None
        except Exception as e:
            error = str(e)
            logger.error("Error al obtener los triggers: %s", error)
            return None, error

    def add(self, trigger: Trigger) -> tuple[Optional[Trigger], Optional[str]]:
        try:
            sql = """INSERT INTO triggers 
                     (id, channel_id, delete_message, response, key, position, response_timeout) 
                     VALUES (?, ?, ?, ?, ?, ?, ?)"""
            params = (
                trigger.id,
                trigger.channel_id,
                trigger.delete_message,
                trigger.response,
                trigger.key,
                trigger.position,
                trigger.response_timeout,
            )
            self.db.execute(sql, params)
            return trigger, None
        except Exception as e:
            error = str(e)
            logger.error("Error al crear el trigger: %s", error)
            return None, error

    def delete_by_id(self, trigger_id: str) -> tuple[Optional[str], Optional[str]]:
        # Check if trigger exists
        trigger, error = self.get_by_id(trigger_id)
        if error:
            logger.error("Error al obtener el trigger: %s", error)
            return None, error
        if not trigger:
            logger.error("Trigger no encontrado")
            return None, "Trigger no encontrado"

        try:
            self.db.execute("DELETE FROM triggers WHERE id = ?", (trigger_id,))
            return trigger_id, None
        except Exception as e:
            error = str(e)
            logger.error("Error al eliminar el trigger: %s", error)
            return None, error

    def update(self, trigger: Trigger) -> tuple[Optional[Trigger], Optional[str]]:
        try:
            sql = """INSERT OR REPLACE INTO triggers 
                     (id, channel_id, delete_message, response, key, position, response_timeout) 
                     VALUES (?, ?, ?, ?, ?, ?, ?)"""
            params = (
                trigger.id,
                trigger.channel_id,
                trigger.delete_message,
                trigger.response,
                trigger.key,
                trigger.position,
                trigger.response_timeout,
            )
            self.db.execute(sql, params)
            return trigger, None
        except Exception as e:
            error = str(e)
            logger.error("Error al actualizar el trigger: %s", error)
            return None, error
