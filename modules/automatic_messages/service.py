from typing import List, Optional, Tuple
from database import Database
from modules.core import logger
from .models import AutomaticMessage
import json


class AutomaticMessagesService:
    def __init__(self):
        self.db = Database()
    
    def _normalize_message_data(self, row_data: dict) -> dict:
        """Normaliza los datos de un mensaje para evitar errores de validación"""
        message_data = dict(row_data)
        
        # Asegurar que schedule_type tenga un valor
        if message_data.get('schedule_type') is None:
            message_data['schedule_type'] = 'interval'
        
        # Para mensajes antiguos sin configuración completa
        if message_data['schedule_type'] == 'interval':
            if message_data.get('interval') is None:
                message_data['interval'] = 60
            if message_data.get('interval_unit') is None:
                message_data['interval_unit'] = 'minutes'
        
        return message_data

    def get_all(self) -> Tuple[Optional[List[AutomaticMessage]], Optional[str]]:
        """Obtiene todos los mensajes automáticos"""
        try:
            rows = self.db.select("""
                SELECT id, channel_id, category_id, text, name, interval, interval_unit, 
                       hour, minute, schedule_type, weekdays, cron_expression
                FROM automatic_messages
                ORDER BY name, id
            """)
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

    def get_by_id(self, message_id: str) -> Tuple[Optional[AutomaticMessage], Optional[str]]:
        """Obtiene un mensaje automático por ID"""
        try:
            row = self.db.single("""
                SELECT id, channel_id, category_id, text, name, interval, interval_unit,
                       hour, minute, schedule_type, weekdays, cron_expression
                FROM automatic_messages 
                WHERE id = ?
            """, (message_id,))
            if not row:
                return None, None
            
            message_data = self._normalize_message_data(row)
            message = AutomaticMessage(**message_data)
            return message, None
        except Exception as e:
            error = str(e)
            logger.error("Error al obtener el mensaje automático: %s", error)
            return None, error

    def get_by_channel_id(self, channel_id: int) -> Tuple[Optional[List[AutomaticMessage]], Optional[str]]:
        """Obtiene todos los mensajes automáticos de un canal específico"""
        try:
            rows = self.db.select("""
                SELECT id, channel_id, category_id, text, name, interval, interval_unit,
                       hour, minute, schedule_type, weekdays, cron_expression
                FROM automatic_messages 
                WHERE channel_id = ?
                ORDER BY name, id
            """, (channel_id,))
            
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

    def get_by_category_id(self, category_id: int) -> Tuple[Optional[List[AutomaticMessage]], Optional[str]]:
        """Obtiene todos los mensajes automáticos de una categoría específica"""
        try:
            rows = self.db.select("""
                SELECT id, channel_id, category_id, text, name, interval, interval_unit,
                       hour, minute, schedule_type, weekdays, cron_expression
                FROM automatic_messages 
                WHERE category_id = ?
                ORDER BY name, id
            """, (category_id,))
            
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

    def get_interval_messages(self) -> Tuple[Optional[List[AutomaticMessage]], Optional[str]]:
        """Obtiene todos los mensajes con programación por intervalo"""
        try:
            rows = self.db.select("""
                SELECT id, channel_id, category_id, text, name, interval, interval_unit,
                       hour, minute, schedule_type, weekdays, cron_expression
                FROM automatic_messages 
                WHERE schedule_type = 'interval' AND channel_id IS NOT NULL
                ORDER BY name, id
            """)
            
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
            rows = self.db.select("""
                SELECT id, channel_id, category_id, text, name, interval, interval_unit,
                       hour, minute, schedule_type, weekdays, cron_expression
                FROM automatic_messages 
                WHERE schedule_type IN ('daily', 'weekly', 'custom') AND channel_id IS NOT NULL
                ORDER BY name, id
            """)
            
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

    def add(self, message: AutomaticMessage) -> Tuple[bool, Optional[str]]:
        """Añade un nuevo mensaje automático"""
        try:
            self.db.execute("""
                INSERT INTO automatic_messages 
                (id, channel_id, category_id, text, name, interval, interval_unit, 
                 hour, minute, schedule_type, weekdays, cron_expression)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                message.id,
                message.channel_id,
                message.category_id,
                message.text,
                message.name,
                message.interval,
                message.interval_unit,
                message.hour,
                message.minute,
                message.schedule_type,
                message.weekdays,
                message.cron_expression
            ))
            return True, None
        except Exception as e:
            error = str(e)
            logger.error("Error al crear mensaje automático: %s", error)
            return False, error

    def update(self, message: AutomaticMessage) -> Tuple[bool, Optional[str]]:
        """Actualiza un mensaje automático existente"""
        try:
            self.db.execute("""
                UPDATE automatic_messages 
                SET channel_id = ?, category_id = ?, text = ?, name = ?, 
                    interval = ?, interval_unit = ?, hour = ?, minute = ?,
                    schedule_type = ?, weekdays = ?, cron_expression = ?
                WHERE id = ?
            """, (
                message.channel_id,
                message.category_id,
                message.text,
                message.name,
                message.interval,
                message.interval_unit,
                message.hour,
                message.minute,
                message.schedule_type,
                message.weekdays,
                message.cron_expression,
                message.id
            ))
            return True, None
        except Exception as e:
            error = str(e)
            logger.error("Error al actualizar mensaje automático: %s", error)
            return False, error

    def delete(self, message_id: str) -> Tuple[bool, Optional[str]]:
        """Elimina un mensaje automático"""
        try:
            self.db.execute("DELETE FROM automatic_messages WHERE id = ?", (message_id,))
            return True, None
        except Exception as e:
            error = str(e)
            logger.error("Error al eliminar mensaje automático: %s", error)
            return False, error

    def exists(self, message_id: str) -> bool:
        """Verifica si existe un mensaje automático con el ID dado"""
        try:
            row = self.db.single("SELECT 1 FROM automatic_messages WHERE id = ?", (message_id,))
            return row is not None
        except Exception as e:
            logger.error("Error al verificar existencia del mensaje: %s", str(e))
            return False
