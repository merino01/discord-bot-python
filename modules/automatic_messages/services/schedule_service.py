from typing import List, Optional, Tuple
from modules.core import logger
from ..models import AutomaticMessage
from .message_service import MessageService


class ScheduleService(MessageService):
    def get_interval_messages(self) -> Tuple[Optional[List[AutomaticMessage]], Optional[str]]:
        """Obtiene todos los mensajes con programación por intervalo"""
        try:
            rows = self.db.select(
                """
                SELECT id, channel_id, category_id, text, name, interval, interval_unit,
                       hour, minute, schedule_type, weekdays, cron_expression
                FROM automatic_messages
                WHERE schedule_type = 'interval' AND channel_id IS NOT NULL
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
            logger.error("Error al obtener mensajes por intervalo: %s", error)
            return None, error

    def get_scheduled_messages(self) -> Tuple[Optional[List[AutomaticMessage]], Optional[str]]:
        """Obtiene todos los mensajes con programación por hora/cron"""
        try:
            rows = self.db.select(
                """
                SELECT id, channel_id, category_id, text, name, interval, interval_unit,
                       hour, minute, schedule_type, weekdays, cron_expression
                FROM automatic_messages
                WHERE schedule_type IN ('daily', 'weekly', 'custom') AND channel_id IS NOT NULL
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
            logger.error("Error al obtener mensajes programados: %s", error)
            return None, error

    def get_channel_create_messages(self) -> Tuple[Optional[List[AutomaticMessage]], Optional[str]]:
        """Obtiene mensajes que se envían al crear canales"""
        try:
            rows = self.db.select(
                """
                SELECT id, channel_id, category_id, text, name, interval, interval_unit,
                       hour, minute, schedule_type, weekdays, cron_expression
                FROM automatic_messages
                WHERE schedule_type = 'on_channel_create'
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
            logger.error("Error al obtener mensajes de creación de canal: %s", error)
            return None, error

    def get_daily_messages(self) -> Tuple[Optional[List[AutomaticMessage]], Optional[str]]:
        """Obtiene mensajes programados diariamente"""
        try:
            rows = self.db.select(
                """
                SELECT id, channel_id, category_id, text, name, interval, interval_unit,
                       hour, minute, schedule_type, weekdays, cron_expression
                FROM automatic_messages
                WHERE schedule_type = 'daily' AND channel_id IS NOT NULL
                ORDER BY hour, minute, name
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
            logger.error("Error al obtener mensajes diarios: %s", error)
            return None, error

    def get_weekly_messages(self) -> Tuple[Optional[List[AutomaticMessage]], Optional[str]]:
        """Obtiene mensajes programados semanalmente"""
        try:
            rows = self.db.select(
                """
                SELECT id, channel_id, category_id, text, name, interval, interval_unit,
                       hour, minute, schedule_type, weekdays, cron_expression
                FROM automatic_messages
                WHERE schedule_type = 'weekly' AND channel_id IS NOT NULL
                ORDER BY hour, minute, name
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
            logger.error("Error al obtener mensajes semanales: %s", error)
            return None, error
