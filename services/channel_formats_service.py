"""channel_formats_service.py"""

from typing import List
from database import db
from database.models import ChannelFormat
from utils.logger import logger

class ChannelFormatsService:
    """Service class for managing channel formats."""

    @staticmethod
    def get_all() -> List[ChannelFormat]:
        """
        Fetch all channel formats from the database.
        :return: List of channel formats.
        """
        return db.query(
            model=ChannelFormat,
            query="SELECT * FROM channel_formats"
        )

    @staticmethod
    def get_by_id(format_id: str) -> ChannelFormat | None:
        """
        Fetch a channel format by its ID.
        :param id: The ID of the channel format.
        :return: The channel format if found, otherwise None.
        """
        channel_formats = db.query(
            model=ChannelFormat,
            query="SELECT * FROM channel_formats WHERE id = ?",
            params=(format_id,)
        )
        return channel_formats[0] if len(channel_formats) > 0 else None

    @staticmethod
    def get_one_by_channel_id(channel_id: int) -> ChannelFormat | None:
        """
        Fetch channel formats by channel ID.
        :param channel_id: The ID of the channel.
        :return: List of channel formats for the specified channel.
        """
        channel_formats = db.query(
            model=ChannelFormat,
            query="SELECT * FROM channel_formats WHERE channel_id = ?",
            params=(channel_id,)
        )
        return channel_formats[0] if len(channel_formats) > 0 else None

    @staticmethod
    def get_all_by_channel_id(channel_id: int) -> List[ChannelFormat]:
        """
        Fetch channel formats by channel ID.
        :param channel_id: The ID of the channel.
        :return: List of channel formats for the specified channel.
        """
        channel_formats = db.query(
            model=ChannelFormat,
            query="SELECT * FROM channel_formats WHERE channel_id = ?",
            params=(channel_id,)
        )
        return channel_formats


    @staticmethod
    def add(channel_format: ChannelFormat) -> None:
        """
        Add a new channel format to the database.
        :param channel_format: The channel format to add.
        """
        ok = db.insert(
            table="channel_formats",
            data={
                "id": str(channel_format.id),
                "channel_id": channel_format.channel_id,
                "regex": channel_format.regex
            }
        )
        if ok:
            logger.info(f"Formato añadido para el canal {channel_format.channel_id}")


    @staticmethod
    def delete(channel_format: ChannelFormat) -> bool:
        """
        Delete a channel format from the database.
        :param channel_format: The channel format to delete.
        """
        ok = db.delete(
            table="channel_formats",
            key="id",
            value=str(channel_format.id)
        )
        if ok:
            logger.info(
                "Formato eliminado para el canal %s",
                channel_format.channel_id
            )
        else:
            logger.error(
                "Error al eliminar el formato para el canal %s",
                channel_format.channel_id
            )
        return ok
