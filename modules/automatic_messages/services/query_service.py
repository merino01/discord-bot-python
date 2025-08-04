from typing import List, Optional, Tuple
from modules.core import logger
from ..models import AutomaticMessage
from .message_service import MessageService


class QueryService(MessageService):
    def get_all(self) -> Tuple[Optional[List[AutomaticMessage]], Optional[str]]:
        """Obtiene todos los mensajes automáticos"""
        try:
            rows = self.db.select(
                """
                SELECT id, channel_id, category_id, text, name, interval, interval_unit,
                       hour, minute, schedule_type, weekdays, cron_expression
                FROM automatic_messages
                ORDER BY name, id
            """
            )
            messages = []
            for row in rows:
                try:
                    message_data = self._normalize_message_data(row)
                    message = AutomaticMessage(**message_data)
                    messages.append(message)
                except Exception as e:
                    logger.warning(f"Error procesando mensaje {row.get('id', 'unknown')}: {e}")
                    continue

            return messages, None
        except Exception as e:
            error = str(e)
            logger.error("Error al obtener los mensajes automáticos: %s", error)
            return None, error

    def get_by_channel_id(
        self, channel_id: int
    ) -> Tuple[Optional[List[AutomaticMessage]], Optional[str]]:
        """Obtiene todos los mensajes automáticos de un canal específico"""
        try:
            rows = self.db.select(
                """
                SELECT id, channel_id, category_id, text, name, interval, interval_unit,
                       hour, minute, schedule_type, weekdays, cron_expression
                FROM automatic_messages
                WHERE channel_id = ?
                ORDER BY name, id
            """,
                (channel_id,),
            )

            messages = []
            for row in rows:
                try:
                    message_data = self._normalize_message_data(row)
                    message = AutomaticMessage(**message_data)
                    messages.append(message)
                except Exception as e:
                    logger.warning(f"Error procesando mensaje {row.get('id', 'unknown')}: {e}")
                    continue

            return messages, None
        except Exception as e:
            error = str(e)
            logger.error("Error al obtener mensajes por canal: %s", error)
            return None, error

    def get_by_category_id(
        self, category_id: int
    ) -> Tuple[Optional[List[AutomaticMessage]], Optional[str]]:
        """Obtiene todos los mensajes automáticos de una categoría específica"""
        try:
            rows = self.db.select(
                """
                SELECT id, channel_id, category_id, text, name, interval, interval_unit,
                       hour, minute, schedule_type, weekdays, cron_expression
                FROM automatic_messages
                WHERE category_id = ?
                ORDER BY name, id
            """,
                (category_id,),
            )

            messages = []
            for row in rows:
                try:
                    message_data = self._normalize_message_data(row)
                    message = AutomaticMessage(**message_data)
                    messages.append(message)
                except Exception as e:
                    logger.warning(f"Error procesando mensaje {row.get('id', 'unknown')}: {e}")
                    continue

            return messages, None
        except Exception as e:
            error = str(e)
            logger.error("Error al obtener mensajes por categoría: %s", error)
            return None, error

    def get_by_schedule_type(
        self, schedule_type: str
    ) -> Tuple[Optional[List[AutomaticMessage]], Optional[str]]:
        """Obtiene mensajes por tipo de programación"""
        try:
            rows = self.db.select(
                """
                SELECT id, channel_id, category_id, text, name, interval, interval_unit,
                       hour, minute, schedule_type, weekdays, cron_expression
                FROM automatic_messages
                WHERE schedule_type = ?
                ORDER BY name, id
            """,
                (schedule_type,),
            )

            messages = []
            for row in rows:
                try:
                    message_data = self._normalize_message_data(row)
                    message = AutomaticMessage(**message_data)
                    messages.append(message)
                except Exception as e:
                    logger.warning(f"Error procesando mensaje {row.get('id', 'unknown')}: {e}")
                    continue

            return messages, None
        except Exception as e:
            error = str(e)
            logger.error("Error al obtener mensajes por tipo de programación: %s", error)
            return None, error
