"""automatic_messages_service.py"""

from typing import List, Optional
from database import db
from modules.core import logger
from .models import AutomaticMessage

class AutomaticMessagesService:
    """Service class for managing channel formats."""

    @staticmethod
    def get_all() -> tuple[Optional[List[AutomaticMessage]], Optional[str]]:
        """
        Fetch all channel formats from the database.
        :return: List of channel formats.
        """
        automatic_messages, error = db.select(
            model=AutomaticMessage,
            table="automatic_messages",
            columns=["*"]
        )
        if error:
            logger.error("Error al obtener los mensajes automáticos: %s", error)
            return None, error
        return automatic_messages, None


    @staticmethod
    def get_by_id(automatic_message_id: str) -> tuple[Optional[AutomaticMessage], Optional[str]]:
        """
        Fetch a channel format by its ID.
        :param automatic_message_id: ID of the channel format to fetch.
        :return: Channel format with the specified ID.
        """
        automatic_message, error = db.select_one(
            model=AutomaticMessage,
            table="automatic_messages",
            columns=["*"],
            conditions={"id": automatic_message_id}
        )
        if error:
            logger.error("Error al obtener el mensaje automático: %s", error)
            return None, error
        return automatic_message, None


    @staticmethod
    def get_by_channel_id(
        channel_id: int
    ) -> tuple[Optional[List[AutomaticMessage]], Optional[str]]:
        """
        Fetch channel formats by channel ID.
        :param channel_id: Channel ID to filter by.
        :return: List of channel formats for the specified channel ID.
        """
        automatic_message, error = db.select(
            model=AutomaticMessage,
            table="automatic_messages",
            columns=["*"],
            conditions={"channel_id": channel_id}
        )
        if error:
            logger.error("Error al obtener los mensajes automáticos: %s", error)
            return None, error
        return automatic_message, None


    @staticmethod
    def add(
        automatic_message: AutomaticMessage
    ) -> tuple[Optional[AutomaticMessage], Optional[str]]:
        """
        Add a new channel format to the database.
        :param automatic_message: Channel format to add.
        """
        _, error = db.insert(
            table="automatic_messages",
            data=automatic_message.__dict__
        )
        if error:
            logger.error("Error al crear el mensaje automático: %s", error)
            return None, error
        return automatic_message, None


    @staticmethod
    def delete_by_id(automatic_message_id: str) -> tuple[Optional[int], Optional[str]]:
        """
        Delete a channel format from the database.
        :param automatic_message_id: ID of the channel format to delete.
        """
        _id, error = db.delete(
            table="automatic_messages",
            key="id",
            value=automatic_message_id
        )
        if error:
            logger.error("Error al eliminar el mensaje automático: %s", error)
            return None, error
        return _id, None
