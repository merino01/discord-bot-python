"""
triggers commands
"""

from typing import Optional
from uuid import uuid4
from discord import app_commands, Interaction, TextChannel, Object, Embed, Color
from discord.ext import commands
from settings import guild_id
from modules.core import send_paginated_embeds
from .service import TriggersService
from .models import Trigger, TriggerTextPosition, TriggerPosition


TRIGGER_POSITIONS_TRANSLATIONS = {
    TriggerPosition.CONTAINS.value: "Contiene",
    TriggerPosition.STARTS_WITH.value: "Empieza por",
    TriggerPosition.ENDS_WITH.value: "Termina por",
    TriggerPosition.EXACT_MATCH.value: "Igual a",
    TriggerPosition.TEXT_BETWEEN.value: "Texto entre",
    TriggerPosition.REGEX.value: "Expresión regular",
}


class TriggersCommands(commands.GroupCog, name="triggers"):
    """
    Commands for configuring the triggers
    """

    def __init__(self, bot):
        self.bot = bot

    ######################################
    ### Comando para añadir un trigger ###
    ######################################
    @app_commands.command(name="crear", description="Añade un trigger")
    @app_commands.describe(
        canal="Canal donde se verificará el trigger",
        borrar_mensaje="Configurar si se debe borrar el mensaje que activa el trigger",
        respuesta="Respuesta del bot al trigger",
        clave="Palabra clave que activa el trigger",
        posicion="Posición de la palabra clave en el mensaje",
        tiempo_respuesta="Tiempo de espera para la respuesta del bot",
    )
    @app_commands.choices(
        posicion=[
            app_commands.Choice(
                name=TRIGGER_POSITIONS_TRANSLATIONS[TriggerPosition.CONTAINS.value],
                value=TriggerPosition.CONTAINS.value,
            ),
            app_commands.Choice(
                name=TRIGGER_POSITIONS_TRANSLATIONS[TriggerPosition.STARTS_WITH.value],
                value=TriggerPosition.STARTS_WITH.value,
            ),
            app_commands.Choice(
                name=TRIGGER_POSITIONS_TRANSLATIONS[TriggerPosition.ENDS_WITH.value],
                value=TriggerPosition.ENDS_WITH.value,
            ),
            app_commands.Choice(
                name=TRIGGER_POSITIONS_TRANSLATIONS[TriggerPosition.EXACT_MATCH.value],
                value=TriggerPosition.EXACT_MATCH.value,
            ),
            app_commands.Choice(
                name=TRIGGER_POSITIONS_TRANSLATIONS[TriggerPosition.TEXT_BETWEEN.value],
                value=TriggerPosition.TEXT_BETWEEN.value,
            ),
            app_commands.Choice(
                name=TRIGGER_POSITIONS_TRANSLATIONS[TriggerPosition.REGEX.value],
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
        """Add trigger command"""
        new_trigger = Trigger(
            id=str(uuid4()),
            channel_id=canal.id,
            delete_message=borrar_mensaje,
            response=respuesta,
            key=clave,
            position=posicion,
            response_timeout=tiempo_respuesta,
        )
        _, error = TriggersService.add(new_trigger)
        if error:
            await interaction.response.send_message(content=error, ephemeral=True)
            return
        await interaction.response.send_message("Trigger creado", ephemeral=True)

    ##################################################
    ### Comando para ver una lista de los triggers ###
    ##################################################
    @app_commands.command(name="listar", description="Lista de triggers")
    @app_commands.describe(
        id_trigger="ID del trigger",
        canal="Lista de triggers por canal",
        persistente="Hacer la lista persistente",
    )
    @app_commands.checks.has_permissions(manage_channels=True, manage_messages=True)
    async def list_triggers(
        self,
        interaction: Interaction,
        id_trigger: Optional[str] = None,
        canal: Optional[TextChannel] = None,
        persistente: bool = False,
    ):
        """List triggers command"""
        triggers = []
        if id_trigger:
            trigger, error = TriggersService.get_by_id(id_trigger)
            if error:
                await interaction.response.send_message(content=error, ephemeral=True)
                return
            if not trigger:
                await interaction.response.send_message(
                    content=f"No se ha encontrado el trigger con ID {id_trigger}.",
                    ephemeral=True,
                )
                return
            triggers.append(trigger)
        elif canal:
            triggers, error = TriggersService.get_all_by_channel_id(canal.id)
            if error:
                await interaction.response.send_message(content=error, ephemeral=True)
                return
        else:
            triggers, error = TriggersService.get_all()
            if error:
                await interaction.response.send_message(content=error, ephemeral=True)
                return

        if not triggers or len(triggers) == 0:
            await interaction.response.send_message(
                "No hay triggers configurados.", ephemeral=True
            )
            return

        embeds = []
        for trigger in triggers:
            embed = Embed(
                title=f"Trigger {trigger.id}",
                description="Detalles del trigger",
                color=Color.green(),
            )
            embed.add_field(name="Canal", value=f"<#{trigger.channel_id}>", inline=True)
            embed.add_field(
                name="Borrar mensaje",
                value="Sí" if trigger.delete_message else "No",
                inline=True,
            )
            embed.add_field(
                name="Respuesta",
                value=trigger.response if trigger.response else "-",
                inline=True,
            )
            embed.add_field(name="Palabra clave", value=trigger.key, inline=True)
            embed.add_field(
                name="Posición",
                value=TRIGGER_POSITIONS_TRANSLATIONS.get(trigger.position, "invalido"),
                inline=True,
            )
            if trigger.response_timeout:
                embed.add_field(
                    name="Tiempo de espera",
                    value=f"{trigger.response_timeout} segundos",
                    inline=True,
                )
            embeds.append(embed)

        await send_paginated_embeds(
            interaction=interaction,
            embeds=embeds,
            ephemeral=not persistente,
            message=f"Lista de triggers ({len(triggers)})",
        )

    ########################################
    ### Comando para eliminar un trigger ###
    ########################################
    @app_commands.command(name="eliminar", description="Eliminar un trigger")
    @app_commands.describe(id_del_trigger="ID del trigger")
    @app_commands.checks.has_permissions(manage_channels=True, manage_messages=True)
    async def delete_trigger(self, interaction: Interaction, id_del_trigger: str):
        """Delete trigger command"""
        _, error = TriggersService.delete_by_id(id_del_trigger)
        if error:
            await interaction.response.send_message(content=error, ephemeral=True)
            return
        await interaction.response.send_message(
            content="Trigger eliminado", ephemeral=True
        )

    #######################################
    ### Comando para editar un trigger ####
    #######################################
    @app_commands.command(name="editar", description="Editar un trigger")
    @app_commands.describe(
        id_trigger="ID del trigger",
        canal="Canal donde se verificará el trigger",
        borrar_mensaje="Configurar si se debe borrar el mensaje que activa el trigger",
        respuesta="Respuesta del bot al trigger",
        clave="Palabra clave que activa el trigger",
        posicion="Posición de la palabra clave en el mensaje",
        tiempo_respuesta="Tiempo de espera para la respuesta del bot",
    )
    @app_commands.choices(
        posicion=[
            app_commands.Choice(
                name=TRIGGER_POSITIONS_TRANSLATIONS[TriggerPosition.CONTAINS.value],
                value=TriggerPosition.CONTAINS.value,
            ),
            app_commands.Choice(
                name=TRIGGER_POSITIONS_TRANSLATIONS[TriggerPosition.STARTS_WITH.value],
                value=TriggerPosition.STARTS_WITH.value,
            ),
            app_commands.Choice(
                name=TRIGGER_POSITIONS_TRANSLATIONS[TriggerPosition.ENDS_WITH.value],
                value=TriggerPosition.ENDS_WITH.value,
            ),
            app_commands.Choice(
                name=TRIGGER_POSITIONS_TRANSLATIONS[TriggerPosition.EXACT_MATCH.value],
                value=TriggerPosition.EXACT_MATCH.value,
            ),
            app_commands.Choice(
                name=TRIGGER_POSITIONS_TRANSLATIONS[TriggerPosition.TEXT_BETWEEN.value],
                value=TriggerPosition.TEXT_BETWEEN.value,
            ),
            app_commands.Choice(
                name=TRIGGER_POSITIONS_TRANSLATIONS[TriggerPosition.REGEX.value],
                value=TriggerPosition.REGEX.value,
            ),
        ]
    )
    @app_commands.checks.has_permissions(manage_channels=True, manage_messages=True)
    async def edit_trigger(
        self,
        interaction: Interaction,
        id_trigger: str,
        canal: Optional[TextChannel] = None,
        borrar_mensaje: Optional[bool] = None,
        respuesta: Optional[str] = None,
        clave: Optional[str] = None,
        posicion: Optional[TriggerTextPosition] = None,
        tiempo_respuesta: Optional[int] = None,
    ):
        """Edit trigger command"""
        trigger, error = TriggersService.get_by_id(id_trigger)
        if error:
            await interaction.response.send_message(content=error, ephemeral=True)
            return
        if not trigger:
            await interaction.response.send_message(
                content=f"No se ha encontrado el trigger con ID {id_trigger}.",
                ephemeral=True,
            )
            return

        # Actualizamos los campos que se han pasado como parámetros
        if canal:
            trigger.channel_id = canal.id
        if borrar_mensaje is not None:
            trigger.delete_message = borrar_mensaje
        if respuesta:
            trigger.response = respuesta
        if clave:
            trigger.key = clave
        if posicion:
            trigger.position = posicion
        if tiempo_respuesta:
            trigger.response_timeout = tiempo_respuesta

        _, error = TriggersService.update(trigger)
        if error:
            await interaction.response.send_message(content=error, ephemeral=True)
            return

        await interaction.response.send_message(
            content="Trigger editado", ephemeral=True
        )


async def setup(bot):
    """setup"""
    await bot.add_cog(TriggersCommands(bot), guild=Object(id=guild_id))
