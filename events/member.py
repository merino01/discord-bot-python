from discord import Member
from discord.ext import commands
from modules.logs_config import LogHandler


class MemberEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_handler = LogHandler(bot)

    @commands.Cog.listener()
    async def on_member_update(self, before: Member, after: Member):
        await self.log_handler.log_member_update(before, after)


async def setup(bot):
    await bot.add_cog(MemberEvents(bot))
