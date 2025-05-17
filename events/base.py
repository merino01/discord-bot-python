"""
Base events for the bot.
"""

from discord.ext import commands
from modules.core import logger
from settings import guild_id
from modules.automatic_messages.tasks import setup_automatic_messages
from modules.core import send_message_to_admin


class BaseEvents(commands.Cog):
    """
    Base events for the bot.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Called when the bot is ready.
        """
        logger.info(
            "Iniciado sesión como %s en el servidor %s", self.bot.user.name, guild_id
        )
        await send_message_to_admin(self.bot, "🟥🟧🟨🟩   **Ready**   🟩🟨🟧🟥")
        setup_automatic_messages(self.bot)

    @commands.Cog.listener()
    async def on_disconnect(self):
        """
        Called when the bot is disconnected.
        """
        logger.warning("Bot desconectado")


async def setup(bot):
    """setup"""
    await bot.add_cog(BaseEvents(bot))
