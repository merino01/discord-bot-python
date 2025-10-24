from typing import Optional
from uuid import uuid4
from discord import app_commands, Interaction, TextChannel, Object, Embed, Color
from discord.ext import commands
from settings import guild_id
from modules.core import send_paginated_embeds
from .service import TriggersService
from .models import Trigger, TriggerTextPosition, TriggerPosition
from .utils import show_trigger_selection_for_delete, show_trigger_selection_for_edit, edit_trigger_by_id
from translator import __


class TriggersCommands(commands.GroupCog, name="triggers"):
    def __init__(self, bot):
        self.bot = bot
        self.service = TriggersService()

    ######################################
    ### Comando para añadir un trigger ###
    ######################################
    @app_commands.command(name="crear", description=constants.COMMAND_CREATE_DESC)
    @app_commands.describe(
        canal=constants.PARAM_CHANNEL_DESC,
        borrar_mensaje=constants.PARAM_DELETE_MESSAGE_DESC,
        respuesta=constants.PARAM_RESPONSE_DESC,
        clave=constants.PARAM_KEYWORD_DESC,
        posicion=constants.PARAM_POSITION_DESC,
        tiempo_respuesta=constants.PARAM_TIMEOUT_DESC,
    )
    @app_commands.choices(
        posicion=[
            app_commands.Choice(
                name=__("triggers.positions")[TriggerPosition.CONTAINS.value],
                value=TriggerPosition.CONTAINS.value,
            ),
            app_commands.Choice(
                name=__("triggers.positions")[TriggerPosition.STARTS_WITH.value],
                value=TriggerPosition.STARTS_WITH.value,
            ),
            app_commands.Choice(
                name=__("triggers.positions")[TriggerPosition.ENDS_WITH.value],
                value=TriggerPosition.ENDS_WITH.value,
            ),
            app_commands.Choice(
                name=__("triggers.positions")[TriggerPosition.EXACT_MATCH.value],
                value=TriggerPosition.EXACT_MATCH.value,
            ),
            app_commands.Choice(
                name=__("triggers.positions")[TriggerPosition.TEXT_BETWEEN.value],
                value=TriggerPosition.TEXT_BETWEEN.value,
            ),
            app_commands.Choice(
                name=__("triggers.positions")[TriggerPosition.REGEX.value],
                value=TriggerPosition.REGEX.value,
            ),
        ]
    )
    @app_commands.checks.has_permissions(manage_channels=True, manage_messages=True)
    async def add_trigger(
        self,
        interaction: Interaction,
        canal: TextChannel,
        borrar_mensaje: bool,
        respuesta: Optional[str],
        clave: str,
        posicion: TriggerTextPosition,
        tiempo_respuesta: Optional[int],
    ):
        new_trigger = Trigger(
            id=str(uuid4()),
            channel_id=canal.id,
            delete_message=borrar_mensaje,
            response=respuesta,
            key=clave,
            position=posicion,
            response_timeout=tiempo_respuesta,
        )
        _, error = self.service.add(new_trigger)
        if error:
            await interaction.response.send_message(content=error, ephemeral=True)
            return
        await interaction.response.send_message(__("triggers.successMessages.triggerCreated"), ephemeral=True)

    ##################################################
    ### Comando para ver una lista de los triggers ###
    ##################################################
    @app_commands.command(name="listar", description=constants.COMMAND_LIST_DESC)
    @app_commands.describe(
        id_trigger=constants.PARAM_TRIGGER_ID_DESC,
        canal=constants.PARAM_LIST_CHANNEL_DESC,
        persistente=constants.PARAM_PERSISTENT_DESC,
    )
    @app_commands.checks.has_permissions(manage_channels=True, manage_messages=True)
    async def list_triggers(
        self,
        interaction: Interaction,
        id_trigger: Optional[str] = None,
        canal: Optional[TextChannel] = None,
        persistente: bool = False,
    ):
        triggers = []
        if id_trigger:
            trigger, error = self.service.get_by_id(id_trigger)
            if error:
                await interaction.response.send_message(content=error, ephemeral=True)
                return
            if not trigger:
                await interaction.response.send_message(
                    content=__("triggers.errorMessages.triggerNotFound", id=id_trigger),
                    ephemeral=True,
                )
                return
            triggers.append(trigger)
        elif canal:
            triggers, error = self.service.get_all_by_channel_id(canal.id)
            if error:
                await interaction.response.send_message(content=error, ephemeral=True)
                return
        else:
            triggers, error = self.service.get_all()
            if error:
                await interaction.response.send_message(content=error, ephemeral=True)
                return

        if not triggers or len(triggers) == 0:
            await interaction.response.send_message(__("triggers.messages.noTriggersFound"), ephemeral=True)
            return

        embeds = []
        for trigger in triggers:
            embed = Embed(
                title=constants.TITLE_TRIGGER_ID.format(id=trigger.id),
                description=constants.EMBED_DESCRIPTION,
                color=Color.green(),
            )
            embed.add_field(name=constants.FIELD_CHANNEL, value=f"<#{trigger.channel_id}>", inline=True)
            embed.add_field(
                name=constants.FIELD_DELETE_MESSAGE,
                value=constants.VALUE_YES if trigger.delete_message else constants.VALUE_NO,
                inline=True,
            )
            embed.add_field(
                name=constants.FIELD_RESPONSE,
                value=trigger.response if trigger.response else constants.VALUE_NONE,
                inline=True,
            )
            embed.add_field(name=constants.FIELD_KEYWORD, value=trigger.key, inline=True)
            embed.add_field(
                name=constants.FIELD_POSITION,
                value=constants.TRIGGER_POSITIONS_TRANSLATIONS.get(trigger.position, constants.VALUE_INVALID),
                inline=True,
            )
            if trigger.response_timeout:
                embed.add_field(
                    name=constants.FIELD_TIMEOUT,
                    value=constants.VALUE_TIMEOUT_SECONDS.format(timeout=trigger.response_timeout),
                    inline=True,
                )
            embeds.append(embed)

        await send_paginated_embeds(
            interaction=interaction,
            embeds=embeds,
            ephemeral=not persistente,
            message=__("triggers.messages.showingTriggers", count=len(triggers)),
        )

    ########################################
    ### Comando para eliminar un trigger ###
    ########################################
    @app_commands.command(name="eliminar", description=constants.COMMAND_DELETE_DESC)
    @app_commands.describe(id_del_trigger=constants.PARAM_TRIGGER_DELETE_ID_DESC)
    @app_commands.checks.has_permissions(manage_channels=True, manage_messages=True)
    async def delete_trigger(self, interaction: Interaction, id_del_trigger: Optional[str] = None):
        """Delete trigger command"""
        if id_del_trigger:
            # Si se proporciona ID, eliminar directamente
            _, error = self.service.delete_by_id(id_del_trigger)
            if error:
                await interaction.response.send_message(content=error, ephemeral=True)
                return
            await interaction.response.send_message(content=__("triggers.successMessages.triggerDeleted"), ephemeral=True)
        else:
            # Si no se proporciona ID, mostrar vista de selección
            await show_trigger_selection_for_delete(interaction, self.service)

    #######################################
    ### Comando para editar un trigger ####
    #######################################
    @app_commands.command(name="editar", description=constants.COMMAND_EDIT_DESC)
    @app_commands.describe(
        id_trigger=constants.PARAM_TRIGGER_ID_DESC,
        canal=constants.PARAM_CHANNEL_DESC,
        borrar_mensaje=constants.PARAM_DELETE_MESSAGE_DESC,
        respuesta=constants.PARAM_RESPONSE_DESC,
        clave=constants.PARAM_KEYWORD_DESC,
        posicion=constants.PARAM_POSITION_DESC,
        tiempo_respuesta=constants.PARAM_TIMEOUT_DESC,
    )
    @app_commands.choices(
        posicion=[
            app_commands.Choice(
                name=__("triggers.positions")[TriggerPosition.CONTAINS.value],
                value=TriggerPosition.CONTAINS.value,
            ),
            app_commands.Choice(
                name=__("triggers.positions")[TriggerPosition.STARTS_WITH.value],
                value=TriggerPosition.STARTS_WITH.value,
            ),
            app_commands.Choice(
                name=__("triggers.positions")[TriggerPosition.ENDS_WITH.value],
                value=TriggerPosition.ENDS_WITH.value,
            ),
            app_commands.Choice(
                name=__("triggers.positions")[TriggerPosition.EXACT_MATCH.value],
                value=TriggerPosition.EXACT_MATCH.value,
            ),
            app_commands.Choice(
                name=__("triggers.positions")[TriggerPosition.TEXT_BETWEEN.value],
                value=TriggerPosition.TEXT_BETWEEN.value,
            ),
            app_commands.Choice(
                name=__("triggers.positions")[TriggerPosition.REGEX.value],
                value=TriggerPosition.REGEX.value,
            ),
        ]
    )
    @app_commands.checks.has_permissions(manage_channels=True, manage_messages=True)
    async def edit_trigger(
        self,
        interaction: Interaction,
        id_trigger: Optional[str] = None,
        canal: Optional[TextChannel] = None,
        borrar_mensaje: Optional[bool] = None,
        respuesta: Optional[str] = None,
        clave: Optional[str] = None,
        posicion: Optional[TriggerTextPosition] = None,
        tiempo_respuesta: Optional[int] = None,
    ):
        """Edit trigger command"""
        if id_trigger:
            # Si se proporciona ID, editar directamente
            await edit_trigger_by_id(
                interaction, self.service, id_trigger,
                canal=canal, borrar_mensaje=borrar_mensaje, respuesta=respuesta,
                clave=clave, posicion=posicion, tiempo_respuesta=tiempo_respuesta
            )
        else:
            # Si no se proporciona ID, mostrar vista de selección
            await show_trigger_selection_for_edit(
                interaction, self.service,
                canal=canal, borrar_mensaje=borrar_mensaje, respuesta=respuesta,
                clave=clave, posicion=posicion, tiempo_respuesta=tiempo_respuesta
            )


async def setup(bot):
    await bot.add_cog(TriggersCommands(bot), guild=Object(id=guild_id))
