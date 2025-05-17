"""
Guild events for the bot.
"""

from discord.ext import commands
from modules.logs_config import LogHandler


class GuildEvents(commands.Cog):
    """
    Guild events for the bot.
    """

    def __init__(self, bot):
        self.bot = bot
        self.log_handler = LogHandler(bot)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        Called when a member joins the guild.
        """
        await self.log_handler.log_member_join(member)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """
        Called when a member leaves the guild.
        """
        await self.log_handler.log_member_remove(member)


async def setup(bot):
    """setup"""
    await bot.add_cog(GuildEvents(bot))
