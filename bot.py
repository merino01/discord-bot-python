"""
    bot.py
"""

from discord import Intents, Object
from discord.ext import commands
from settings import bot_token, guild_id, prefix
from utils.logger import logger

class Bot(commands.Bot):
    """
    Custom Discord bot class that inherits from discord.Client.
    """

    def __init__(self):
        """
        Initialize the bot with the intents.
        """
        intents = Intents.default()
        intents.guilds = True
        intents.members = True
        intents.message_content = True
        intents.voice_states = True
        intents.guild_reactions = True

        super().__init__(
            command_prefix=prefix,
            intents=intents
        )

    async def setup_hook(self):
        """
        Executes before the bot starts.
        This is where we can set up listeners and other configurations.
        """
        # Load events
        await self.load_extension("cogs.events.base")
        await self.load_extension("cogs.events.message")
        await self.load_extension("cogs.events.member")
        await self.load_extension("cogs.events.voice")
        await self.load_extension("cogs.events.guild")
        logger.info("Eventos registrados")

        # Load commands
        await self.load_extension("cogs.commands.tasks")
        logger.info("Comandos registrados con el prefijo %s", prefix)

        # Load slash commands
        await self.load_extension("cogs.slash_commands.config_logs")
        await self.load_extension("cogs.slash_commands.triggers")
        await self.load_extension("cogs.slash_commands.channel_formats")
        await self.load_extension("cogs.slash_commands.automatic_messages")
        logger.info("Comandos de barra registrados")

        # Sincronize slash commands with discord
        await self.tree.sync(guild=Object(id=guild_id))
        logger.info("Comandos de barra sincronizados")

    def init(self):
        """
        Run the bot.
        """
        self.run(
            token=bot_token,
            log_handler=logger.handlers[0]
        )
