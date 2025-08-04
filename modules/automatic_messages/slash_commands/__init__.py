from typing import Optional, Union
from discord import app_commands, Interaction, TextChannel, CategoryChannel, Object, ext
from settings import guild_id
from translator import __
from .program_message import program_message
from .list_messages import list_messages
from .delete_message import delete_message


class AutomaticMessagesCommands(
    ext.commands.GroupCog, name=__("commands.names.automaticMessages.commandName")
):
    def __init__(self, bot):
        self.bot = bot

    ########################################
    ### Comando para programar mensajes ###
    ########################################
    @app_commands.command(
        name=__("commands.names.automaticMessages.program"),
        description=__("commands.descriptions.automaticMessages.program"),
    )
    @app_commands.describe(
        tipo_programacion=__("automaticMessages.commandOptions.program.scheduleType"),
        destino=__("automaticMessages.commandOptions.program.destination"),
        nombre=__("automaticMessages.commandOptions.program.name"),
    )
    @app_commands.choices(
        tipo_programacion=[
            app_commands.Choice(
                name=__("automaticMessages.scheduleTypeChoices.interval"), value="interval"
            ),
            app_commands.Choice(
                name=__("automaticMessages.scheduleTypeChoices.daily"), value="daily"
            ),
            app_commands.Choice(
                name=__("automaticMessages.scheduleTypeChoices.weekly"), value="weekly"
            ),
            app_commands.Choice(
                name=__("automaticMessages.scheduleTypeChoices.on_channel_create"),
                value="on_channel_create",
            ),
        ]
    )
    async def _program_message(
        self,
        interaction: Interaction,
        tipo_programacion: str,
        destino: Union[TextChannel, CategoryChannel],
        nombre: Optional[str] = None,
    ):
        await program_message(interaction, tipo_programacion, destino, nombre)

    #####################################
    ### Comando para listar mensajes ###
    #####################################
    @app_commands.command(
        name=__("commands.names.automaticMessages.list"),
        description=__("commands.descriptions.automaticMessages.list"),
    )
    @app_commands.describe(
        canal=__("automaticMessages.commandOptions.channel"),
        categoria=__("automaticMessages.commandOptions.category"),
    )
    async def _list_messages(
        self,
        interaction: Interaction,
        canal: Optional[TextChannel] = None,
        categoria: Optional[CategoryChannel] = None,
    ):
        await list_messages(self.bot, interaction, canal, categoria)

    ######################################
    ### Comando para eliminar mensajes ###
    ######################################
    @app_commands.command(
        name=__("commands.names.automaticMessages.delete"),
        description=__("commands.descriptions.automaticMessages.delete"),
    )
    @app_commands.describe(
        canal=__("automaticMessages.commandOptions.channel"),
        categoria=__("automaticMessages.commandOptions.category"),
    )
    async def _delete_message(
        self,
        interaction: Interaction,
        canal: Optional[TextChannel] = None,
        categoria: Optional[CategoryChannel] = None,
    ):
        await delete_message(self.bot, interaction, canal, categoria)


async def setup(bot):
    await bot.add_cog(AutomaticMessagesCommands(bot), guild=Object(guild_id))
