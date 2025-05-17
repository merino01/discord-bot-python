"""
Member events for the bot.
"""

from discord import Member
from discord.ext import commands
from modules.logs_config import LogHandler


class MemberEvents(commands.Cog):
    """
    Member events for the bot.
    """

    def __init__(self, bot):
        self.bot = bot
        self.log_handler = LogHandler(bot)

    @commands.Cog.listener()
    async def on_member_update(self, before: Member, after: Member):
        """
        Called when a member updates their profile.
        """
        await self.log_handler.log_member_update(before, after)


async def setup(bot):
    """setup"""
    await bot.add_cog(MemberEvents(bot))
