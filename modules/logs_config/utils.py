"""Utility functions for log configs."""

from typing import Optional
from discord import TextChannel
from discord.ext.commands import Bot
from settings import guild_id
from modules.core import logger
from .service import LogsConfigService
from .models import LogConfigType


async def _get_text_channel(bot: Bot, channel_id: int) -> Optional[TextChannel]:
    """Get a text channel by its ID."""
    if not channel_id:
        return None

    channel = await bot.fetch_channel(channel_id)
    if not channel or not isinstance(channel, TextChannel):
        logger.error(
            "El canal %s no es un canal de texto o no existe.",
            channel_id
        )
        return None

    if channel.guild.id != guild_id:
        return None

    return channel

async def get_log_channel(bot: Bot, log_type: LogConfigType) -> Optional[TextChannel]:
    """
    Get the log channel for a specific log type.
    
    Args:
        bot: The bot instance.
        log_type: The type of log to get the channel for.
    
    Returns:
        The log channel, or None if not found or not enabled.
    """
    log_config, error = LogsConfigService.get_by_type(log_type)
    if error:
        logger.error(
            "Error al obtener la configuracion de logs de tipo members: %s",
            error
        )
        return None
    if not log_config or not log_config.enabled:
        return None

    return await _get_text_channel(bot, log_config.channel_id)
