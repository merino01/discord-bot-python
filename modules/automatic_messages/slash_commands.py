"""
automatic messages commands
"""
from uuid import uuid4
from typing import Optional, Literal, Dict
from discord import (
    app_commands,
    Interaction,
    TextChannel,
    Object,
    Embed,
    Color
)
from discord.ext import commands
from settings import guild_id
from modules.core import send_paginated_embeds
from .service import AutomaticMessagesService
from .models import AutomaticMessage
from .tasks import stop_task_by_id, start_task

TimeUnit = Literal["seconds", "minutes", "hours"]

TIME_TRANSLATIONS: Dict[TimeUnit, str] = {
    "seconds": "segundos",
    "minutes": "minutos",
    "hours": "horas"
}


class AutomaticMessagesCommands(commands.GroupCog, name="mensajes_automaticos"):
    """
    Commands for configuring the logs
    """
    def __init__(self, bot):
        self.bot = bot


    #################################################
    ### Comando para añadir un mensaje automático ###
    #################################################
    @app_commands.command(name="crear", description="Crea un mensaje automático")
    @app_commands.describe(
        canal="Canal donde se enviará el mensaje automático",
        mensaje="Mensaje automático a enviar",
        intervalo="Intervalo de tiempo entre mensajes",
        tipo_intervalo="Tipo de intervalo (segundos, minutos, horas)",
        hora="Hora en la que se enviará el mensaje automático",
        minuto="Minuto en el que se enviará el mensaje automático"
    )
    @app_commands.choices(tipo_intervalo=[
        app_commands.Choice(name="segundos", value="seconds"),
        app_commands.Choice(name="minutos", value="minutes"),
        app_commands.Choice(name="horas", value="hours")
    ])
    @app_commands.checks.has_permissions(
        manage_channels=True,
        manage_messages=True
    )
    async def create_automatic_message(
        self,
        interaction: Interaction,
        canal: TextChannel,
        mensaje: str,
        intervalo: Optional[int] = None,
        tipo_intervalo: Optional[TimeUnit] = None,
        hora: Optional[int] = None,
        minuto: Optional[int] = None
    ):
        """Create an automatic message"""
        new_automatic_message = AutomaticMessage(
            id=str(uuid4()),
            channel_id=canal.id,
            text=mensaje,
            interval=intervalo,
            interval_unit=tipo_intervalo,
            hour=hora,
            minute=minuto
        )
        _, error = AutomaticMessagesService.add(new_automatic_message)
        if error:
            await interaction.response.send_message(
                "Error al crear el mensaje automático",
                ephemeral=True
            )
            return
        await interaction.response.send_message(
            f"Mensaje automático creado en el canal {canal.mention}",
            ephemeral=True
        )
        start_task(self.bot, new_automatic_message)


    ##########################################################
    ### Comando para listar todos los mensajes automáticos ###
    ##########################################################
    @app_commands.command(
        name="listar",
        description="Lista todos los mensajes automáticos"
    )
    @app_commands.describe(
        canal="Vero mensaje automático por canal",
        persistente="Hacer persistente"
    )
    @app_commands.checks.has_permissions(
        manage_channels=True,
        manage_messages=True
    )
    async def list_automatic_messages(
        self,
        interaction: Interaction,
        canal: Optional[TextChannel],
        persistente: Optional[bool] = False
    ):
        """List channel formats command"""
        automatic_messages = []
        if canal:
            automatic_messages, error = AutomaticMessagesService.get_by_channel_id(canal.id)
            if error:
                await interaction.response.send_message(
                    content=error,
                    ephemeral=True
                )
                return

        else:
            automatic_messages, error = AutomaticMessagesService.get_all()
            if error:
                await interaction.response.send_message(
                    content=error,
                    ephemeral=True
                )
                return

        if not automatic_messages:
            automatic_messages = []

        embeds = []
        for automatic_message in automatic_messages:
            embed = Embed(
                title=f"Mensaje automático {automatic_message.id}",
                color=Color.blue()
            )
            embed.add_field(
                name="Canal",
                value=f"<#{automatic_message.channel_id}>",
                inline=False
            )
            embed.add_field(
                name="Mensaje",
                value=automatic_message.text,
                inline=False
            )
            if hasattr(automatic_message, "interval") and automatic_message.interval_unit:
                _unit = automatic_message.interval_unit
                embed.add_field(
                    name="Intervalo",
                    value=f"Cada {automatic_message.interval} {TIME_TRANSLATIONS[_unit]}",
                    inline=False
                )
            elif hasattr(automatic_message, "hour") and hasattr(automatic_message, "minute"):
                embed.add_field(
                    name="Hora",
                    value=f"{automatic_message.hour}:{automatic_message.minute}",
                    inline=False
                )
            embeds.append(embed)

        await send_paginated_embeds(
            interaction=interaction,
            message=f"Mostrando {len(automatic_messages)} mensajes automáticos",
            embeds=embeds,
            ephemeral=not persistente
        )


    ###################################################
    ### Comando para eliminar un mensaje automático ###
    ###################################################
    @app_commands.command(name="eliminar", description="Elimina un mensaje automático")
    @app_commands.describe(
        id_mensaje="ID del mensaje automático a eliminar"
    )
    @app_commands.checks.has_permissions(
        manage_channels=True,
        manage_messages=True
    )
    async def delete_automatic_message(
        self,
        interaction: Interaction,
        id_mensaje: str
    ):
        """Delete automatic message command"""
        automatic_message, error = AutomaticMessagesService.get_by_id(id_mensaje)
        if error:
            await interaction.response.send_message(
                content=error,
                ephemeral=True
            )
            return

        if not automatic_message:
            await interaction.response.send_message(
                f"No se ha encontrado el mensaje automático con ID {id_mensaje}",
                ephemeral=True
            )
            return

        _, error = AutomaticMessagesService.delete_by_id(id_mensaje)
        if error:
            await interaction.response.send_message(
                f"No se ha podido eliminar el mensaje automático con ID {id_mensaje}",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"Mensaje automático con ID **{id_mensaje}** eliminado",
            ephemeral=True
        )
        # Detenemos la tarea si existe
        stop_task_by_id(id_mensaje)


async def setup(bot):
    """setup"""
    await bot.add_cog(
        AutomaticMessagesCommands(bot),
        guild=Object(id=guild_id)
    )
