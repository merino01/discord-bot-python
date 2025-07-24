from discord.ext import commands
from modules.logs_config import LogHandler


class VoiceEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_handler = LogHandler(bot)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        await self.log_handler.log_voice_state_update(member, before, after)


async def setup(bot):
    await bot.add_cog(VoiceEvents(bot))
