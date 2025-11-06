from typing import Optional
from uuid import uuid4
from discord import app_commands, Interaction, TextChannel, Object, Embed, Color
from discord.ext import commands
from settings import guild_id
from modules.core import send_paginated_embeds
from .service import TriggersService
from .models import Trigger, TriggerTextPosition, TriggerPosition
from .utils import show_trigger_selection_for_delete, show_trigger_selection_for_edit, edit_trigger_by_id
from i18n import __


class TriggersCommands(commands.GroupCog, name="triggers"):
    def __init__(self, bot):
        self.bot = bot
        self.service = TriggersService()

def get_position_translation(position: str, fallback: str = "") -> str:
    """Get translation for trigger position."""
    position_translations = {
        "contains": __("triggers.positions.contains"),
        "starts_with": __("triggers.positions.startsWidth"),
        "ends_with": __("triggers.positions.endsWidth"),
        "equal": __("triggers.positions.equal"),
        "text_between": __("triggers.positions.textBetween"),
        "regex": __("triggers.positions.regex"),
    }
    return position_translations.get(position, fallback)



    ######################################
    ### Comando para añadir un trigger ###
    ######################################
    @app_commands.command(name="crear", description=__("triggers.commands.create"))
    @app_commands.describe(
        canal=__("triggers.params.channel"),
        borrar_mensaje=__("triggers.params.deleteMessage"),
        respuesta=__("triggers.params.response"),
        clave=__("triggers.params.keyword"),
        posicion=__("triggers.params.position"),
        tiempo_respuesta=__("triggers.params.timeout"),
    )
    @app_commands.choices(
        posicion=[
            app_commands.Choice(
                name=__("triggers.positions.contains"),
                value=TriggerPosition.CONTAINS.value,
            ),
            app_commands.Choice(
                name=__("triggers.positions.startsWidth"),
                value=TriggerPosition.STARTS_WITH.value,
            ),
            app_commands.Choice(
                name=__("triggers.positions.endsWidth"),
                value=TriggerPosition.ENDS_WITH.value,
            ),
            app_commands.Choice(
                name=__("triggers.positions.equal"),
                value=TriggerPosition.EXACT_MATCH.value,
            ),
            app_commands.Choice(
                name=__("triggers.positions.textBetween"),
                value=TriggerPosition.TEXT_BETWEEN.value,
            ),
            app_commands.Choice(
                name=__("triggers.positions.regex"),
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
        await interaction.response.send_message(__("triggers.success.triggerCreated"), ephemeral=True)

    ##################################################
    ### Comando para ver una lista de los triggers ###
    ##################################################
    @app_commands.command(name="listar", description=__("triggers.commands.list"))
    @app_commands.describe(
        id_trigger=__("triggers.params.triggerId"),
        canal=__("triggers.params.listChannel"),
        persistente=__("triggers.params.persistent"),
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
                    content=__("triggers.errors.triggerNotFound", id=id_trigger),
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
                title=__("triggers.embeds.triggerIdTitle", id=trigger.id),
                description=__("clanSettings.embeds.description"),
                color=Color.green(),
            )
            embed.add_field(name=__("triggers.fields.channel"), value=f"<#{trigger.channel_id}>", inline=True)
            embed.add_field(
                name=__("triggers.fields.deleteMessage"),
                value=__("clanSettings.values.yes") if trigger.delete_message else __("clanSettings.values.no"),
                inline=True,
            )
            embed.add_field(
                name=__("triggers.fields.response"),
                value=trigger.response if trigger.response else __("triggers.values.none"),
                inline=True,
            )
            embed.add_field(name=__("triggers.fields.keyword"), value=trigger.key, inline=True)
            embed.add_field(
                name=__("triggers.fields.position"),
                value=get_position_translation(trigger.position, __("triggers.values.invalid")),
                inline=True,
            )
            if trigger.response_timeout:
                embed.add_field(
                    name=__("triggers.fields.timeout"),
                    value=__("triggers.values.timeoutSeconds", timeout=trigger.response_timeout),
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
    @app_commands.command(name="eliminar", description=__("triggers.commands.delete"))
    @app_commands.describe(id_del_trigger=__("triggers.params.triggerDeleteId"))
    @app_commands.checks.has_permissions(manage_channels=True, manage_messages=True)
    async def delete_trigger(self, interaction: Interaction, id_del_trigger: Optional[str] = None):
        """Delete trigger command"""
        if id_del_trigger:
            # Si se proporciona ID, eliminar directamente
            _, error = self.service.delete_by_id(id_del_trigger)
            if error:
                await interaction.response.send_message(content=error, ephemeral=True)
                return
            await interaction.response.send_message(content=__("triggers.success.triggerDeleted"), ephemeral=True)
        else:
            # Si no se proporciona ID, mostrar vista de selección
            await show_trigger_selection_for_delete(interaction, self.service)

    #######################################
    ### Comando para editar un trigger ####
    #######################################
    @app_commands.command(name="editar", description=__("triggers.commands.edit"))
    @app_commands.describe(
        id_trigger=__("triggers.params.triggerId"),
        canal=__("triggers.params.channel"),
        borrar_mensaje=__("triggers.params.deleteMessage"),
        respuesta=__("triggers.params.response"),
        clave=__("triggers.params.keyword"),
        posicion=__("triggers.params.position"),
        tiempo_respuesta=__("triggers.params.timeout"),
    )
    @app_commands.choices(
        posicion=[
            app_commands.Choice(
                name=__("triggers.positions.contains"),
                value=TriggerPosition.CONTAINS.value,
            ),
            app_commands.Choice(
                name=__("triggers.positions.startsWidth"),
                value=TriggerPosition.STARTS_WITH.value,
            ),
            app_commands.Choice(
                name=__("triggers.positions.endsWidth"),
                value=TriggerPosition.ENDS_WITH.value,
            ),
            app_commands.Choice(
                name=__("triggers.positions.equal"),
                value=TriggerPosition.EXACT_MATCH.value,
            ),
            app_commands.Choice(
                name=__("triggers.positions.textBetween"),
                value=TriggerPosition.TEXT_BETWEEN.value,
            ),
            app_commands.Choice(
                name=__("triggers.positions.regex"),
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
