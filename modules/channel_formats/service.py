"""channel_formats_service.py"""
from typing import List, Optional
from database import db
from modules.core import logger
from .models import ChannelFormat

class ChannelFormatsService:
    """Service class for managing channel formats."""

    @staticmethod
    def get_all() -> tuple[Optional[List[ChannelFormat]], Optional[str]]:
        """
        Fetch all channel formats from the database.
        :return: List of channel formats.
        """
        channel_formats, error = db.select(
            model=ChannelFormat,
            table="channel_formats",
            columns=["*"]
        )
        if error:
            logger.error("Error al obtener los formatos de canal: %s", error)
            return None, error

        return channel_formats, None


    @staticmethod
    def get_by_id(format_id: str) -> tuple[Optional[ChannelFormat], Optional[str]]:
        """
        Fetch a channel format by its ID.
        :param id: The ID of the channel format.
        :return: The channel format if found, otherwise None.
        """
        channel_format, error = db.select_one(
            model=ChannelFormat,
            table="channel_formats",
            columns=["*"],
            contitions={"id": format_id}
        )
        if error:
            logger.error("Error al obtener el formato de canal: %s", error)
            return None, error
        return channel_format, None


    @staticmethod
    def get_one_by_channel_id(channel_id: int) -> tuple[Optional[ChannelFormat], Optional[str]]:
        """
        Fetch channel formats by channel ID.
        :param channel_id: The ID of the channel.
        :return: List of channel formats for the specified channel.
        """
        channel_format, error = db.select_one(
            model=ChannelFormat,
            table="channel_formats",
            columns=["*"],
            contitions={"channel_id": channel_id}
        )
        if error:
            logger.error("Error al obtener el formato de canal: %s", error)
            return None, error
        return channel_format, None


    @staticmethod
    def get_all_by_channel_id(channel_id: int) -> tuple[Optional[List[ChannelFormat]], Optional[str]]:
        """
        Fetch channel formats by channel ID.
        :param channel_id: The ID of the channel.
        :return: List of channel formats for the specified channel.
        """
        channel_formats, error = db.select(
            model=ChannelFormat,
            table="channel_formats",
            columns=["*"],
            conditions={"channel_id": channel_id}
        )
        if error:
            logger.error("Error al obtener los formatos de canal: %s", error)
            return None, error
        return channel_formats, None


    @staticmethod
    def add(channel_format: ChannelFormat) -> tuple[Optional[ChannelFormat], Optional[str]]:
        """
        Add a new channel format to the database.
        :param channel_format: The channel format to add.
        """
        _, error = db.insert(
            table="channel_formats",
            data={
                "id": str(channel_format.id),
                "channel_id": channel_format.channel_id,
                "regex": channel_format.regex
            }
        )
        if error:
            logger.error("Error al crear el formato de canal: %s", error)
            return None, error
        return channel_format, None


    @staticmethod
    def delete(channel_format: ChannelFormat) -> tuple[Optional[str], Optional[str]]:
        """
        Delete a channel format from the database.
        :param channel_format: The channel format to delete.
        """
        _, error = db.delete(
            table="channel_formats",
            key="id",
            value=str(channel_format.id)
        )
        if error:
            logger.error("Error al eliminar el formato de canal: %s", error)
            return None, error
        return channel_format.id, None
