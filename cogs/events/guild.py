"""
Base events for the bot.
"""

from discord.ext import commands
from utils.channels import get_join_leave_log_channel, send_message_to_channel
from utils.embeds import get_member_join_embed, get_member_remove_embed

class GuildEvents(commands.Cog):
    """
    Member events for the bot.
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        Called when a member joins the server.
        """
        channel_to_send = await get_join_leave_log_channel(self.bot)
        if channel_to_send is None:
            return
        embed = get_member_join_embed(member)
        await send_message_to_channel(channel=channel_to_send, embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """
        Called when a member leaves the server.
        """
        channel_to_send = await get_join_leave_log_channel(self.bot)
        if channel_to_send is None:
            return
        embed = get_member_remove_embed(member)
        await send_message_to_channel(channel=channel_to_send, embed=embed)


async def setup(bot):
    """setup"""
    await bot.add_cog(GuildEvents(bot))
