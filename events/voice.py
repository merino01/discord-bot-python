"""
Voice events for the bot.
"""

from discord.ext import commands
from modules.logs_config import LogHandler

class VoiceEvents(commands.Cog):
    """
    Base events for the bot.
    """
    def __init__(self, bot):
        self.bot = bot
        self.log_handler = LogHandler(bot)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """
        Event when a user joins or leaves a voice channel.
        """
        await self.log_handler.log_voice_state_update(member, before, after)


async def setup(bot):
    """setup"""
    await bot.add_cog(VoiceEvents(bot))
