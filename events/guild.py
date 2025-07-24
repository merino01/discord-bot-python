from discord.ext import commands
from modules.logs_config import LogHandler


class GuildEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_handler = LogHandler(bot)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.log_handler.log_member_join(member)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.log_handler.log_member_remove(member)


async def setup(bot):
    await bot.add_cog(GuildEvents(bot))
