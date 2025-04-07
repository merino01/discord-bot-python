"""
triggers commands
"""
from typing import Optional
from uuid import uuid4
from discord import app_commands, Interaction, TextChannel, Object, Embed, Color
from discord.ext import commands
from settings import guild_id
from services import TriggersService
from database.models import Trigger, TriggerTextPosition
from utils.check_trigger import TriggerPosition

class TriggersCommands(commands.GroupCog, name="triggers"):
    """
    Commands for configuring the triggers
    """
    def __init__(self, bot):
        self.bot = bot

    ######################################
    ### Comando para añadir un trigger ###
    ######################################
    @app_commands.command(
        name="crear",
        description="Añade un trigger"
    )
    @app_commands.describe(
        canal="Canal donde se verificará el trigger",
        borrar_mensaje="Configurar si se debe borrar el mensaje que activa el trigger",
        respuesta="Respuesta del bot al trigger",
        clave="Palabra clave que activa el trigger",
        posicion="Posición de la palabra clave en el mensaje",
        tiempo_respuesta="Tiempo de espera para la respuesta del bot"
    )
    @app_commands.choices(posicion=[
        app_commands.Choice(name="Contiene", value=TriggerPosition.CONTAINS.value),
        app_commands.Choice(name="Empieza por", value=TriggerPosition.STARTS_WITH.value),
        app_commands.Choice(name="Termina por", value=TriggerPosition.ENDS_WITH.value),
        app_commands.Choice(name="Igual a", value=TriggerPosition.EXACT_MATCH.value),
        app_commands.Choice(name="Texto entre", value=TriggerPosition.TEXT_BETWEEN.value),
        app_commands.Choice(name="Expresión regular", value=TriggerPosition.REGEX.value)
    ])
    @app_commands.checks.has_permissions(
        manage_channels=True,
        manage_messages=True
    )
    async def add_trigger(
        self,
        interaction: Interaction,
        canal: TextChannel,
        borrar_mensaje: bool,
        respuesta: str,
        clave: str,
        posicion: TriggerTextPosition,
        tiempo_respuesta: Optional[int]
    ):
        """Add trigger command"""
        new_trigger = Trigger(
            id=uuid4(),
            channel_id=canal.id,
            delete_message=borrar_mensaje,
            response=respuesta,
            key=clave,
            position=posicion,
            response_timeout=tiempo_respuesta
        )
        TriggersService.add(new_trigger)
        await interaction.response.send_message("Trigger añadido", ephemeral=True)

    ##################################################
    ### Comando para ver una lista de los triggers ###
    ##################################################
    @app_commands.command(
        name="listar",
        description="Lista de triggers"
    )
    @app_commands.describe(
        id_trigger="ID del trigger",
        canal="Lista de triggers por canal",
        persistente="Hacer la lista persistente"
    )
    @app_commands.checks.has_permissions(
        manage_channels=True,
        manage_messages=True
    )
    async def list_triggers(
        self,
        interaction: Interaction,
        id_trigger: Optional[str] = None,
        canal: Optional[TextChannel] = None,
        persistente: bool = False
    ):
        """List triggers command"""
        triggers = []
        if id_trigger:
            trigger = TriggersService.get_by_id(id_trigger)
            if not trigger:
                await interaction.response.send_message(
                    f"No se ha encontrado el trigger con ID {id_trigger}.",
                    ephemeral=True
                )
                return
            triggers.append(trigger)
        elif canal:
            triggers = TriggersService.get_all_by_channel_id(canal.id)
            if not triggers:
                await interaction.response.send_message(
                    f"No hay triggers configurados para el canal {canal.mention}.",
                    ephemeral=True
                )
                return
        else:
            triggers = TriggersService.get_all()
            if not triggers:
                await interaction.response.send_message(
                    "No hay triggers configurados.",
                    ephemeral=True
                )
                return

        # Enviamos el primer mensaje para confirmar que recibimos el comando
        await interaction.response.send_message(
            f"Mostrando {len(triggers)} triggers:",
            ephemeral=not persistente
        )

        for trigger in triggers:
            embed = Embed(
                title=f"Trigger {trigger.id}",
                color=Color.green()
            )
            embed.add_field(
                name="Canal",
                value=f"<#{trigger.channel_id}>",
                inline=True
            )
            embed.add_field(
                name="Borrar mensaje",
                value="Sí" if trigger.delete_message else "No",
                inline=True
            )
            embed.add_field(
                name="Respuesta",
                value=trigger.response,
                inline=True
            )
            embed.add_field(
                name="Palabra clave",
                value=trigger.key,
                inline=True
            )
            embed.add_field(
                name="Posición",
                value=trigger.position,
                inline=True
            )
            if trigger.response_timeout:
                embed.add_field(
                    name="Tiempo de espera",
                    value=f"{trigger.response_timeout} segundos",
                    inline=True
                )

            # Usamos followup para enviar los embeds
            await interaction.followup.send(embed=embed, ephemeral=not persistente)


    ########################################
    ### Comando para eliminar un trigger ###
    ########################################
    @app_commands.command(
        name="eliminar",
        description="Eliminar un trigger"
    )
    @app_commands.describe(
        id_del_trigger="ID del trigger"
    )
    @app_commands.checks.has_permissions(
        manage_channels=True,
        manage_messages=True
    )
    async def delete_trigger(
        self,
        interaction: Interaction,
        id_del_trigger: str
    ):
        """Delete trigger command"""
        deleted = TriggersService.delete_by_id(id_del_trigger)
        if deleted:
            await interaction.response.send_message(
                f"Trigger {id_del_trigger} eliminado",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"Ha habido un error al eliminar el trigger {id_del_trigger}",
                ephemeral=True
            )

async def setup(bot):
    """setup"""
    await bot.add_cog(
        TriggersCommands(bot),
        guild=Object(id=guild_id)
    )
