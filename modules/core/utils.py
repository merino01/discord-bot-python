"""global utility functions"""

from typing import List, Optional
from discord import TextChannel, Interaction, Message, Embed, Forbidden, HTTPException
from discord.ext.commands import Bot
from settings import admin_id, send_to_admin
from modules.core import logger


async def send_message_to_channel(
    channel: TextChannel, content: Optional[str] = None, embed: Optional[Embed] = None
) -> Optional[Message]:
    try:
        if not channel.permissions_for(channel.guild.me).send_messages:
            logger.warning("No tengo permisos para enviar mensajes en %s", channel.name)
            return None
        kwargs = {}
        if content:
            kwargs["content"] = content
        if embed:
            kwargs["embed"] = embed
        return await channel.send(**kwargs)
    except Forbidden:
        logger.error("No tengo permisos para enviar mensajes en %s", channel.name)
        return None
    except HTTPException as e:
        logger.error("Error al enviar mensaje a %s. Error: %s", channel.name, e)
        return None


async def send_message_to_admin(
    bot: Bot, content: str, embed: Optional[Embed] = None
) -> Optional[Message]:
    if not send_to_admin:
        return

    try:
        admin = await bot.fetch_user(admin_id)
        if not admin:
            logger.error("No se pudo encontrar al admin con ID %s", admin_id)
            return None

        message = {"content": content, "embed": embed if embed else None}
        await admin.send(**message)
        logger.info("Mensaje enviado al admin: %s", message)
    except Forbidden:
        logger.error("No tengo permisos para enviar mensajes al admin")
        return None
    except HTTPException as e:
        logger.error("Error al enviar el mensaje al admin: %s", e)
        return None


async def send_error_to_admin(bot: Bot, e):
    error_message = f"Error: {str(e)}"
    await send_message_to_admin(bot, error_message)


async def send_paginated_embeds(
    interaction: Interaction,
    embeds: List[Embed],
    ephemeral: bool = False,
    message: Optional[str] = None,
) -> bool:
    try:
        await interaction.response.defer(ephemeral=ephemeral)

        if not embeds or len(embeds) == 0:
            await interaction.followup.send(
                content="No hay información para mostrar.", ephemeral=ephemeral
            )
            return False

        # Enviar primera página
        first_message = None
        if message:
            first_message = {
                "content": message,
                "embeds": embeds[:10],
                "ephemeral": ephemeral,
            }
        else:
            first_message = {"embeds": embeds[:10], "ephemeral": ephemeral}
        await interaction.followup.send(**first_message)

        # Si hay más páginas, usar followup
        for i in range(10, len(embeds), 10):
            await interaction.followup.send(embeds=embeds[i : i + 10], ephemeral=ephemeral)
        return True

    except HTTPException as e:
        logger.error("Error al enviar el mensaje: %s", e)
        await interaction.followup.send(content="No se pudo enviar el mensaje.", ephemeral=True)
        return False
