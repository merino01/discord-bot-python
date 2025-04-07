"""
utils/channels.py
Utility functions to manage channels.
"""

from typing import Optional, Any
from discord import TextChannel, Forbidden, HTTPException
from discord.ext.commands import Bot
from utils.logger import logger
from settings import guild_id
from services import LogsConfigService


async def get_text_channel(client: Bot, channel_id: int) -> TextChannel | None:
    """
        Get a text channel by its ID.
    """
    if channel_id is None:
        return None
    channel = await client.fetch_channel(channel_id)
    if channel is None:
        return None
    if not isinstance(channel, TextChannel):
        return None
    if channel.guild.id != guild_id:
        return None

    return channel

async def get_chatlog_channel(client: Bot) -> TextChannel | None:
    """
        Get the chat log channel.
	"""
    chatlog_config = LogsConfigService.get_by_type("chat")
    if chatlog_config is None or chatlog_config.enabled is False:
        return None
    if chatlog_config is None or chatlog_config.enabled is False:
        return None

    return await get_text_channel(client, chatlog_config.channel_id)

async def get_voicelog_channel(client: Bot) -> TextChannel | None:
    """
        Get the voice log channel.
    """
    voicelog_config = LogsConfigService.get_by_type("voice")
    if voicelog_config is None or voicelog_config.enabled is False:
        return None

    return await get_text_channel(client, voicelog_config.channel_id)

async def get_join_leave_log_channel(client: Bot) -> TextChannel | None:
    """
        Get the join/leave log channel.
    """
    join_leave_log_config = LogsConfigService.get_by_type("join_leave")
    if join_leave_log_config is None or join_leave_log_config.enabled is False:
        return None

    return await get_text_channel(client, join_leave_log_config.channel_id)

async def get_memberslog_channel(client: Bot) -> TextChannel | None:
    """
        Get the members log channel.
    """
    memberslog_config = LogsConfigService.get_by_type("members")
    if memberslog_config is None or memberslog_config.enabled is False:
        return None

    return await get_text_channel(client, memberslog_config.channel_id)

async def send_message_to_channel(
    channel: TextChannel,
    content: Optional[str] = None,
    **kwargs: Any
) -> None:
    """
    Envía un mensaje a un canal con los mismos parámetros que channel.send()
    
    Args:
        channel: Canal donde enviar el mensaje
        content: Contenido del mensaje
        **kwargs: Argumentos adicionales para channel.send()
    """
    if channel is None or not isinstance(channel, TextChannel):
        return

    try:
        await channel.send(content=content, **kwargs)
    except Forbidden:
        logger.warning(
            "Error al enviar el mensaje al canal %s. No tengo permisos.",
            channel.name
        )
    except HTTPException as e:
        logger.error(
            "Error al enviar el mensaje al canal %s. Error: %s",
            channel.name,
            e
        )
