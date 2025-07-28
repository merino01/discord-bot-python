from uuid import uuid4
from typing import Optional, Literal
from discord import app_commands, Interaction, TextChannel, CategoryChannel, Object
from discord.ext import commands
from settings import guild_id
from modules.core import send_paginated_embeds
from .service import AutomaticMessagesService
from .models import AutomaticMessage
from .tasks import stop_task_by_id, start_task
from .utils import (
    show_message_selection_for_delete, 
    get_messages_for_listing, 
    create_message_embeds
)
from . import constants

TimeUnit = Literal["seconds", "minutes", "hours"]

class AutomaticMessagesCommands(commands.GroupCog, name="mensajes_automaticos"):
    def __init__(self, bot):
        self.bot = bot
        self.service = AutomaticMessagesService()

    #################################################
    ### Comando para añadir un mensaje automático ###
    #################################################
    @app_commands.command(name="crear", description=constants.COMMAND_CREATE_DESC)
    @app_commands.describe(
        mensaje=constants.PARAM_MESSAGE_DESC,
        nombre=constants.PARAM_NAME_DESC,
        canal=constants.PARAM_CHANNEL_DESC,
        categoria=constants.PARAM_CATEGORY_DESC,
        intervalo=constants.PARAM_INTERVAL_DESC,
        tipo_intervalo=constants.PARAM_INTERVAL_TYPE_DESC,
        hora=constants.PARAM_HOUR_DESC,
        minuto=constants.PARAM_MINUTE_DESC,
    )
    @app_commands.choices(
        tipo_intervalo=[
            app_commands.Choice(name=constants.CHOICE_SECONDS, value="seconds"),
            app_commands.Choice(name=constants.CHOICE_MINUTES, value="minutes"),
            app_commands.Choice(name=constants.CHOICE_HOURS, value="hours"),
        ]
    )
    @app_commands.checks.has_permissions(manage_channels=True, manage_messages=True)
    async def create_automatic_message(
        self,
        interaction: Interaction,
        nombre: str,
        mensaje: str,
        canal: Optional[TextChannel] = None,
        categoria: Optional[CategoryChannel] = None,
        intervalo: Optional[int] = None,
        tipo_intervalo: Optional[TimeUnit] = None,
        hora: Optional[int] = None,
        minuto: Optional[int] = None,
    ):
        # Validar que se especifique canal o categoría, pero no ambos
        if not canal and not categoria:
            await interaction.response.send_message(
                constants.ERROR_MUST_SPECIFY_CHANNEL_OR_CATEGORY, ephemeral=True
            )
            return
        
        if canal and categoria:
            await interaction.response.send_message(
                constants.ERROR_CANNOT_SPECIFY_BOTH, ephemeral=True
            )
            return

        # Para mensajes por categoría, no se requieren parámetros de tiempo
        if categoria:
            new_automatic_message = AutomaticMessage(
                id=str(uuid4()),
                category_id=categoria.id,
                text=mensaje,
                name=nombre,
            )
        else:
            # Para mensajes de canal, aplicar lógica original
            new_automatic_message = AutomaticMessage(
                id=str(uuid4()),
                channel_id=canal.id,
                text=mensaje,
                name=nombre,
                interval=intervalo,
                interval_unit=tipo_intervalo,
                hour=hora,
                minute=minuto,
            )

        _, error = self.service.add(new_automatic_message)
        if error:
            await interaction.response.send_message(
                constants.ERROR_CREATING_MESSAGE, ephemeral=True
            )
            return

        # Respuesta diferente según el tipo
        if categoria:
            await interaction.response.send_message(
                constants.SUCCESS_CATEGORY_MESSAGE_CREATED.format(category=categoria.name), ephemeral=True
            )
        else:
            await interaction.response.send_message(
                constants.SUCCESS_MESSAGE_CREATED.format(channel=canal.mention), ephemeral=True
            )
            # Solo iniciar task para mensajes de canal (no para categoría)
            start_task(self.bot, new_automatic_message)

    ##########################################################
    ### Comando para listar todos los mensajes automáticos ###
    ##########################################################
    @app_commands.command(name="listar", description=constants.COMMAND_LIST_DESC)
    @app_commands.describe(
        canal=constants.PARAM_LIST_CHANNEL_DESC, persistente=constants.PARAM_PERSISTENT_DESC
    )
    @app_commands.checks.has_permissions(manage_channels=True, manage_messages=True)
    async def list_automatic_messages(
        self,
        interaction: Interaction,
        canal: Optional[TextChannel],
        persistente: Optional[bool] = False,
    ):
        automatic_messages, error = get_messages_for_listing(self.service, canal)
        if error:
            await interaction.response.send_message(content=error, ephemeral=True)
            return

        embeds = create_message_embeds(automatic_messages or [])
        await send_paginated_embeds(
            interaction=interaction,
            message=constants.SHOWING_MESSAGES.format(count=len(automatic_messages or [])),
            embeds=embeds,
            ephemeral=not persistente,
        )

    ###################################################
    ### Comando para eliminar un mensaje automático ###
    ###################################################
    @app_commands.command(name="eliminar", description=constants.COMMAND_DELETE_DESC)
    @app_commands.describe(id_mensaje=constants.PARAM_MESSAGE_ID_DESC)
    @app_commands.checks.has_permissions(manage_channels=True, manage_messages=True)
    async def delete_automatic_message(self, interaction: Interaction, id_mensaje: Optional[str] = None):
        # Si no se proporciona ID, mostrar vista de selección
        if id_mensaje is None:
            await show_message_selection_for_delete(interaction)
            return
        
        # Lógica original para cuando se proporciona ID
        automatic_message, error = self.service.get_by_id(id_mensaje)
        if error:
            await interaction.response.send_message(content=error, ephemeral=True)
            return

        if not automatic_message:
            await interaction.response.send_message(
                constants.ERROR_MESSAGE_NOT_FOUND.format(id=id_mensaje),
                ephemeral=True,
            )
            return

        _, error = self.service.delete_by_id(id_mensaje)
        if error:
            await interaction.response.send_message(
                constants.ERROR_DELETING_MESSAGE.format(id=id_mensaje),
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            constants.SUCCESS_MESSAGE_DELETED.format(id=id_mensaje), ephemeral=True
        )
        # Detenemos la tarea si existe
        stop_task_by_id(id_mensaje)


async def setup(bot):
    await bot.add_cog(AutomaticMessagesCommands(bot), guild=Object(id=guild_id))
