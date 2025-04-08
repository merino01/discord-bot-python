"""global utility functions"""

from typing import Optional
from discord import TextChannel, Message, Embed, Forbidden, HTTPException
from discord.ext.commands import Bot
from settings import admin_id, send_to_admin
from modules.core import logger

async def send_message_to_channel(
    channel: TextChannel,
    content: Optional[str] = None,
    embed: Optional[Embed] = None
) -> Optional[Message]:
    """
    Envía un mensaje a un canal de forma segura.
    
    Args:
        channel: Canal donde enviar el mensaje
        content: Contenido del mensaje (opcional)
        embed: Embed del mensaje (opcional)
    """
    try:
        if not channel.permissions_for(channel.guild.me).send_messages:
            logger.warning(
                "No tengo permisos para enviar mensajes en %s",
                channel.name
            )
            return None
        kwargs = {}
        if content:
            kwargs['content'] = content
        if embed:
            kwargs['embed'] = embed
        return await channel.send(**kwargs)
    except Forbidden:
        logger.error(
            "No tengo permisos para enviar mensajes en %s",
            channel.name
        )
        return None
    except HTTPException as e:
        logger.error(
            "Error al enviar mensaje a %s. Error: %s",
            channel.name, e
        )
        return None

async def send_message_to_admin(
    bot: Bot,
    content: str,
    embed: Optional[Embed] = None
) -> Optional[Message]:
    """
    Envía un mensaje al administrador del bot.
    
    Args:
        bot: Instancia del bot
        content: Contenido del mensaje
        embed: Embed del mensaje (opcional)
    """
    if not send_to_admin:
        return

    try:
        admin = await bot.fetch_user(admin_id)
        if not admin:
            logger.error("No se pudo encontrar al admin con ID %s", admin_id)
            return None

        message = {
            'content': content,
            'embed': embed if embed else None
        }
        await admin.send(**message)
        logger.info("Mensaje enviado al admin: %s", message)
    except Forbidden:
        logger.error("No tengo permisos para enviar mensajes al admin")
        return None
    except HTTPException as e:
        logger.error("Error al enviar el mensaje al admin: %s", e)
        return None

async def send_error_to_admin(bot: Bot, e):
    """
    Envía un mensaje de error al administrador del bot.
    
    Args:
        bot: Instancia del bot
        e: Excepción capturada
    """
    error_message = f"Error: {str(e)}"
    await send_message_to_admin(bot, error_message)
