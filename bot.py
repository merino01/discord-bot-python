"""bot.py"""

from discord import Intents, Object
from discord.ext import commands
from settings import bot_token, guild_id, prefix
from modules.core import logger


EXTENSIONS = {
    'events': [
        "events.base",
        "events.message",
        "events.member",
        "events.voice",
        "events.guild",
    ],
    'slash_commands': {
        "modules.automatic_messages.slash_commands",
        "modules.channel_formats.slash_commands",
        "modules.logs_config.slash_commands",
        "modules.triggers.slash_commands",
        "modules.clans.slash_commands",
        "modules.clan_settings.slash_commands"
    }
}


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
        # Events
        try:
            for event in EXTENSIONS['events']:
                await self.load_extension(event)
                logger.info("Eventos cargados: (modulo %s)", event)

            # Slash commands
            for command in EXTENSIONS['slash_commands']:
                await self.load_extension(command)
                logger.info("Comandos de barra cargados: modulo (%s)", command)
        except Exception as e:
            logger.error("Error al cargar las extensiones: %s", e)

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
