from discord import Intents, Object
from discord.ext import commands
from settings import bot_token, guild_id, prefix
from modules.core import logger


EXTENSIONS = {
    "events": [
        "events.base",
        "events.message",
        "events.member",
        "events.voice",
        "events.guild"
    ],
    "slash_commands": [
        "modules.automatic_messages.slash_commands",
        "modules.channel_formats.slash_commands",
        "modules.logs_config.slash_commands",
        "modules.triggers.slash_commands",
        "modules.clans.slash_commands",
        "modules.clan_settings.slash_commands"
    ],
}


class Bot(commands.Bot):
    def __init__(self):
        intents = Intents.default()
        intents.guilds = True
        intents.members = True
        intents.message_content = True
        intents.voice_states = True
        intents.guild_reactions = True

        super().__init__(command_prefix=prefix, intents=intents)

    async def setup_hook(self):
        # Events
        logger.info("Cargando eventos...")
        for event in EXTENSIONS.get("events", []):
            try:
                await self.load_extension(event)
                logger.info("Eventos cargados: (modulo %s)", event)
            except Exception as e:
                logger.error("Error al cargar la extension: %s", e)
                continue

        # Commands
        logger.info("Cargando comandos...")
        for command in EXTENSIONS.get("commands", []):
            try:
                await self.load_extension(command)
                logger.info("Comandos cargados: modulo (%s)", command)
            except Exception as e:
                logger.error("Error al cargar la extension: %s", e)
                continue

        # Slash commands
        logger.info("Cargando comandos de barra...")
        for command in EXTENSIONS.get("slash_commands", []):
            try:
                await self.load_extension(command)
                logger.info("Comandos de barra cargados: modulo (%s)", command)
            except Exception as e:
                logger.error("Error al cargar la extension: %s", e)
                continue

        # Sincronize slash commands with discord
        await self.tree.sync(guild=Object(id=guild_id))
        logger.info("Comandos de barra sincronizados")

    def init(self):
        self.run(token=bot_token, log_handler=logger.handlers[0])
