"""Servicio para manejar los mensajes echo en la base de datos"""

import uuid
from datetime import datetime
from typing import List, Optional, Tuple
from database import Database
from modules.core import logger
from .models import EchoMessage


class EchoService:
    """Servicio para gestionar mensajes echo"""
    
    def __init__(self):
        self.db = Database()
        self._ensure_table_exists()
    
    def _ensure_table_exists(self):
        """Crea la tabla echo_messages si no existe"""
        try:
            sql = """
                CREATE TABLE IF NOT EXISTS echo_messages (
                    id TEXT PRIMARY KEY,
                    message_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    is_embed BOOLEAN NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            self.db.execute(sql)
            logger.info("Tabla echo_messages verificada/creada")
        except Exception as e:
            logger.error(f"Error al crear tabla echo_messages: {e}")
    
    def save_echo_message(
        self,
        message_id: int,
        channel_id: int,
        guild_id: int,
        user_id: int,
        content: str,
        is_embed: bool
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Guarda un mensaje echo en la base de datos
        Returns: (echo_id, error)
        """
        try:
            echo_id = str(uuid.uuid4())
            sql = """
                INSERT INTO echo_messages 
                (id, message_id, channel_id, guild_id, user_id, content, is_embed, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                echo_id,
                message_id,
                channel_id,
                guild_id,
                user_id,
                content,
                is_embed,
                datetime.now().isoformat()
            )
            self.db.execute(sql, params)
            logger.info(f"Mensaje echo guardado: {echo_id}")
            return echo_id, None
        except Exception as e:
            error_msg = f"Error al guardar mensaje echo: {e}"
            logger.error(error_msg)
            return None, error_msg
    
    def get_user_echo_messages(
        self,
        user_id: int,
        guild_id: int,
        limit: int = 10
    ) -> Tuple[Optional[List[EchoMessage]], Optional[str]]:
        """
        Obtiene los últimos mensajes echo de un usuario
        Returns: (messages, error)
        """
        try:
            sql = """
                SELECT id, message_id, channel_id, guild_id, user_id, 
                       content, is_embed, created_at
                FROM echo_messages 
                WHERE user_id = ? AND guild_id = ?
                ORDER BY created_at DESC 
                LIMIT ?
            """
            rows = self.db.select(sql, (user_id, guild_id, limit))
            
            if not rows:
                return [], None
            
            messages = []
            for row in rows:
                message = EchoMessage(
                    id=row['id'],
                    message_id=row['message_id'],
                    channel_id=row['channel_id'],
                    guild_id=row['guild_id'],
                    user_id=row['user_id'],
                    content=row['content'],
                    is_embed=bool(row['is_embed']),
                    created_at=datetime.fromisoformat(row['created_at']) if isinstance(row['created_at'], str) else row['created_at']
                )
                messages.append(message)
            
            return messages, None
        except Exception as e:
            error_msg = f"Error al obtener mensajes echo: {e}"
            logger.error(error_msg)
            return None, error_msg
    
    def get_guild_echo_messages(
        self,
        guild_id: int,
        limit: int = 10
    ) -> Tuple[Optional[List[EchoMessage]], Optional[str]]:
        """
        Obtiene los últimos mensajes echo de todo el servidor
        Returns: (messages, error)
        """
        try:
            sql = """
                SELECT id, message_id, channel_id, guild_id, user_id, 
                       content, is_embed, created_at
                FROM echo_messages 
                WHERE guild_id = ?
                ORDER BY created_at DESC 
                LIMIT ?
            """
            rows = self.db.select(sql, (guild_id, limit))
            
            if not rows:
                return [], None
            
            messages = []
            for row in rows:
                message = EchoMessage(
                    id=row['id'],
                    message_id=row['message_id'],
                    channel_id=row['channel_id'],
                    guild_id=row['guild_id'],
                    user_id=row['user_id'],
                    content=row['content'],
                    is_embed=bool(row['is_embed']),
                    created_at=datetime.fromisoformat(row['created_at']) if isinstance(row['created_at'], str) else row['created_at']
                )
                messages.append(message)
            
            return messages, None
        except Exception as e:
            error_msg = f"Error al obtener mensajes echo del servidor: {e}"
            logger.error(error_msg)
            return None, error_msg
    
    def get_echo_message_by_id(
        self,
        echo_id: str
    ) -> Tuple[Optional[EchoMessage], Optional[str]]:
        """
        Obtiene un mensaje echo por su ID
        Returns: (message, error)
        """
        try:
            sql = """
                SELECT id, message_id, channel_id, guild_id, user_id, 
                       content, is_embed, created_at
                FROM echo_messages 
                WHERE id = ?
            """
            row = self.db.single(sql, (echo_id,))
            
            if not row:
                return None, "Mensaje echo no encontrado"
            
            message = EchoMessage(
                id=row['id'],
                message_id=row['message_id'],
                channel_id=row['channel_id'],
                guild_id=row['guild_id'],
                user_id=row['user_id'],
                content=row['content'],
                is_embed=bool(row['is_embed']),
                created_at=datetime.fromisoformat(row['created_at']) if isinstance(row['created_at'], str) else row['created_at']
            )
            
            return message, None
        except Exception as e:
            error_msg = f"Error al obtener mensaje echo: {e}"
            logger.error(error_msg)
            return None, error_msg
    
    def delete_echo_message(
        self,
        echo_id: str
    ) -> Optional[str]:
        """
        Elimina un mensaje echo de la base de datos
        Returns: error (si existe)
        """
        try:
            self.db.execute("DELETE FROM echo_messages WHERE id = ?", (echo_id,))
            logger.info(f"Mensaje echo eliminado: {echo_id}")
            return None
        except Exception as e:
            error_msg = f"Error al eliminar mensaje echo: {e}"
            logger.error(error_msg)
            return error_msg
