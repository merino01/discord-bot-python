"""automatic_messages_service.py"""

from typing import List, Optional
from database import db
from utils.logger import logger
from database.models import AutomaticMessage

class AutomaticMessagesService:
    """Service class for managing channel formats."""

    @staticmethod
    def get_all() -> List[AutomaticMessage]:
        """
        Fetch all channel formats from the database.
        :return: List of channel formats.
        """
        return db.query(
            model=AutomaticMessage,
            query="SELECT * FROM automatic_messages"
        )

    @staticmethod
    def get_by_id(automatic_message_id: str) -> Optional[AutomaticMessage]:
        """
        Fetch a channel format by its ID.
        :param automatic_message_id: ID of the channel format to fetch.
        :return: Channel format with the specified ID.
        """
        automatic_messages = db.query(
            model=AutomaticMessage,
            query="SELECT * FROM automatic_messages WHERE id = ?",
            params=(automatic_message_id,)
        )
        return automatic_messages[0] if len(automatic_messages) > 0 else None

    @staticmethod
    def get_by_channel_id(channel_id: int) -> List[AutomaticMessage]:
        """
        Fetch channel formats by channel ID.
        :param channel_id: Channel ID to filter by.
        :return: List of channel formats for the specified channel ID.
        """
        return db.query(
            model=AutomaticMessage,
            query="SELECT * FROM automatic_messages WHERE channel_id = ?",
            params=(channel_id,)
        )

    @staticmethod
    def add(automatic_message: AutomaticMessage) -> None:
        """
        Add a new channel format to the database.
        :param automatic_message: Channel format to add.
        """
        data = automatic_message.__dict__.copy()
        data["id"] = str(data["id"])
        # Eliminar campos None para que SQLite use los defaults
        data = {k: v for k, v in data.items() if v is not None}
        db.insert(
            table="automatic_messages",
            data=data
        )

    @staticmethod
    def delete_by_id(automatic_message_id: str) -> bool:
        """
        Delete a channel format from the database.
        :param automatic_message_id: ID of the channel format to delete.
        """
        ok = db.delete(
            table="automatic_messages",
            key="id",
            value=automatic_message_id
        )
        if ok:
            logger.info(f"Mensaje automático {automatic_message_id} eliminado")
        else:
            logger.error(
                "Error al eliminar el mensaje automático %s",
                automatic_message_id
            )
        return ok
