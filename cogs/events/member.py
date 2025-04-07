"""
Base events for the bot.
"""

from discord import Member
from discord.ext import commands
from utils.channels import send_message_to_channel
from utils.embeds import (
    get_member_update_avatar_embed,
    get_member_update_nick_embed,
    get_member_update_roles_embed,
    get_member_update_banner_embed,
    get_member_update_username_embed
)
from utils.channels import get_memberslog_channel

class MemberEvents(commands.Cog):
    """
    Member events for the bot.
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, before: Member, after: Member):
        """
        Called when a member updates their profile.
        """
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

        if embed is None:
            return

        channel_to_send = await get_memberslog_channel(self.bot)
        if channel_to_send is None:
            return
        await send_message_to_channel(channel=channel_to_send, embed=embed)


async def setup(bot):
    """setup"""
    await bot.add_cog(MemberEvents(bot))
