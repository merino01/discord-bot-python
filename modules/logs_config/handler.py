"""handler for logs"""

from discord import Message, Member, TextChannel, Embed, Forbidden, HTTPException
from discord.ext.commands import Bot
from modules.core import logger
from .utils import get_log_channel
from .embeds import (
    get_message_edit_embed,
    get_message_delete_embed,
    get_voice_state_join_embed,
    get_voice_state_leave_embed,
    get_voice_state_move_embed,
    get_member_join_embed,
    get_member_remove_embed,
    get_member_update_username_embed,
    get_member_update_nick_embed,
    get_member_update_roles_embed,
    get_member_update_avatar_embed,
    get_member_update_banner_embed,
)


class LogHandler:
    """Manejador centralizado de logs"""

    def __init__(self, bot: Bot):
        self.bot = bot

    async def _send_log(self, channel: TextChannel, embed: Embed) -> None:
        """Envía el log al canal"""
        try:
            await channel.send(embed=embed)
        except Forbidden:
            logger.warning(
                "Error al enviar el log al canal %s. No tengo permisos.", channel.name
            )
        except HTTPException as e:
            logger.error(
                "Error al enviar el log al canal %s. Error: %s", channel.name, e
            )

    async def log_message_edit(self, before: Message, after: Message) -> None:
        """Maneja logs de mensajes editados"""
        if before.author.bot:
            return
        if before.content == after.content:
            return

        channel = await get_log_channel(self.bot, "chat")
        if not channel:
            return

        embed = get_message_edit_embed(before, after)
        if embed:
            await self._send_log(channel, embed)

    async def log_message_delete(self, message: Message) -> None:
        """Maneja logs de mensajes borrados"""
        if message.author.bot:
            return

        channel = await get_log_channel(self.bot, "chat")
        if not channel:
            return

        embed = get_message_delete_embed(message)
        if embed:
            await self._send_log(channel, embed)

    async def log_member_join(self, member: Member) -> None:
        """Maneja logs de miembros que entran"""
        channel = await get_log_channel(self.bot, "join_leave")
        if not channel:
            return

        embed = get_member_join_embed(member)
        if embed:
            await self._send_log(channel, embed)

    async def log_member_remove(self, member: Member) -> None:
        """Maneja logs de miembros que salen"""
        channel = await get_log_channel(self.bot, "join_leave")
        if not channel:
            return

        embed = get_member_remove_embed(member)
        if embed:
            await self._send_log(channel, embed)

    async def log_member_update(self, before: Member, after: Member) -> None:
        """Maneja logs de miembros que actualizan su perfil"""
        # - Apodo actualizado
        embed = None
        if before.nick != after.nick:
            embed = get_member_update_nick_embed(before, after)
        # - Roles actualizados
        if before.roles != after.roles:
            embed = get_member_update_roles_embed(before, after)
        # - Avatar actualizado
        if before.avatar != after.avatar:
            embed = get_member_update_avatar_embed(before, after)
        # - Nombre actualizado
        if before.name != after.name:
            embed = get_member_update_username_embed(before, after)
        # - Banner actualizado
        if before.banner != after.banner:
            embed = get_member_update_banner_embed(before, after)

        channel = await get_log_channel(self.bot, "members")
        if not channel:
            return

        if embed:
            await self._send_log(channel, embed)

    async def log_voice_state_update(
        self, member: Member, before: Member, after: Member
    ) -> None:
        """Maneja logs de miembros que entran a un canal de voz"""
        channel = await get_log_channel(self.bot, "voice")
        if not channel:
            return

        action = self.get_voice_state_action(before, after)
        embed = None

        match action:
            case "joined":
                embed = get_voice_state_join_embed(member, after)
            case "left":
                embed = get_voice_state_leave_embed(member, before)
            case "moved":
                embed = get_voice_state_move_embed(member, before, after)
            case _:
                return

        if embed:
            await self._send_log(channel, embed)

    def get_voice_state_action(self, before, after):
        """
        Obtiene la acción realizada en el estado de voz.
        """
        if before.channel is None and after.channel is not None:
            return "joined"
        if before.channel is not None and after.channel is None:
            return "left"
        if before.channel != after.channel:
            return "moved"
        return "unknown"
