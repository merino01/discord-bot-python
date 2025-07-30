from typing import Optional, Union
from uuid import uuid4
import discord
from discord import app_commands, Interaction, TextChannel, CategoryChannel, Embed, Color
from discord.ext import commands
from settings import guild_id
from .service import AutomaticMessagesService
from .models import AutomaticMessage, ScheduleTypeEnum, IntervalUnitEnum
from .utils import (
    format_message_for_embed, 
    validate_cron_expression, 
    validate_weekdays_json,
    validate_time,
    send_error_message,
    send_success_message
)
from .views import MessageSelectView, ProgramMessageModal, ScheduleConfigView, IntervalConfigView, TimeConfigView, ProgramMessageTextModal, MessageBuilderView
from . import constants
from .tasks import reload_all_schedules


class AutomaticMessagesCommands(commands.GroupCog, name="mensajes_automaticos"):
    def __init__(self, bot):
        self.bot = bot
        self.service = AutomaticMessagesService()

    ########################################
    ### Comando para programar mensajes ###
    ########################################
    @app_commands.command(name="programar", description=constants.COMMAND_PROGRAM_DESC)
    @app_commands.describe(
        tipo_programacion=constants.PARAM_SCHEDULE_TYPE_DESC,
        destino=constants.DESC_DESTINATION_PARAM,
        nombre=constants.PARAM_NAME_DESC
    )
    @app_commands.choices(
        tipo_programacion=[
            app_commands.Choice(name=constants.CHOICE_INTERVAL, value="interval"),
            app_commands.Choice(name=constants.CHOICE_DAILY, value="daily"),
            app_commands.Choice(name=constants.CHOICE_WEEKLY, value="weekly"),
            app_commands.Choice(name=constants.CHOICE_ON_CHANNEL_CREATE, value="on_channel_create"),
        ]
    )
    @app_commands.checks.has_permissions(manage_channels=True, manage_messages=True)
    async def program_message(
        self,
        interaction: Interaction,
        tipo_programacion: str,
        destino: Union[TextChannel, CategoryChannel],
        nombre: Optional[str] = None,
    ):
        """Programa un nuevo mensaje automático"""
        
        # Validar nombre si se proporciona
        if nombre and len(nombre) > constants.MAX_NAME_LENGTH:
            await send_error_message(
                interaction,
                constants.ERROR_NAME_TOO_LONG.format(max_length=constants.MAX_NAME_LENGTH)
            )
            return
        
        # Validar destino
        if not isinstance(destino, (TextChannel, CategoryChannel)):
            await send_error_message(
                interaction,
                constants.ERROR_INVALID_DESTINATION
            )
            return
        
        # Validar que para "on_channel_create" se use una categoría
        if tipo_programacion == "on_channel_create" and not isinstance(destino, CategoryChannel):
            await send_error_message(
                interaction,
                constants.ERROR_CATEGORY_REQUIRED
            )
            return
        
        # Mostrar la nueva interfaz de configuración con embed y botones
        view = MessageBuilderView(tipo_programacion, destino, nombre)
        
        embed = discord.Embed(
            title=constants.TITLE_CONFIGURE_MESSAGE,
            description=constants.DESC_CONFIGURE_MESSAGE,
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name=constants.FIELD_CURRENT_CONFIG,
            value=constants.TEXT_DESTINATION.format(destination=destino.mention) + "\n" +
                  constants.TEXT_TYPE.format(type=self._get_schedule_type_display(tipo_programacion)) + "\n" +
                  constants.TEXT_NAME.format(name=nombre or constants.TEXT_NO_NAME) + "\n\n" +
                  constants.TEXT_STATUS.format(status=constants.TEXT_NO_CONTENT),
            inline=False
        )
        
        embed.add_field(
            name=constants.FIELD_INSTRUCTIONS,
            value=constants.INSTRUCTION_ADD_TEXT + "\n" +
                  constants.INSTRUCTION_ADD_EMBED + "\n" +
                  constants.INSTRUCTION_ADD_IMAGE + "\n" +
                  constants.INSTRUCTION_COMPLETE,
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    def _get_schedule_type_display(self, schedule_type: str) -> str:
        """Convierte el tipo de programación a un formato amigable"""
        displays = {
            "interval": constants.DISPLAY_INTERVAL,
            "daily": constants.DISPLAY_DAILY, 
            "weekly": constants.DISPLAY_WEEKLY,
            "on_channel_create": constants.DISPLAY_ON_CHANNEL_CREATE
        }
        return displays.get(schedule_type, schedule_type)
    def _validate_schedule_parameters(
        self, 
        schedule_type: str, 
        interval: Optional[int], 
        interval_unit: Optional[str],
        hour: Optional[int], 
        minute: Optional[int], 
        weekdays: Optional[str],  # Mantenemos por compatibilidad pero no se usa para semanal
        cron_expr: Optional[str]
    ) -> Optional[str]:
        """Valida los parámetros según el tipo de programación"""
        
        if schedule_type == "interval":
            if interval is None or interval_unit is None:
                return constants.ERROR_MISSING_REQUIRED_FIELDS
            if interval <= 0:
                return constants.ERROR_INVALID_INTERVAL
            if interval_unit not in ["seconds", "minutes", "hours"]:
                return constants.ERROR_INVALID_INTERVAL_UNIT
        
        elif schedule_type in ["daily", "weekly"]:
            if hour is None or minute is None:
                return constants.ERROR_MISSING_REQUIRED_FIELDS
            if not validate_time(hour, minute):
                return constants.ERROR_INVALID_TIME
            
            if schedule_type == "weekly":
                # Para semanal, los días se configuran en la interfaz interactiva
                # Solo validamos que no se hayan pasado weekdays por parámetro
                pass
        
        elif schedule_type == "custom":
            if not cron_expr:
                return constants.ERROR_CRON_REQUIRED
            if not validate_cron_expression(cron_expr):
                return constants.ERROR_INVALID_CRON
        
        # on_channel_create no requiere validaciones adicionales
        
        return None

    #####################################
    ### Comando para listar mensajes ###
    #####################################
    @app_commands.command(name="listar", description=constants.COMMAND_LIST_DESC)
    @app_commands.describe(
        canal="Filtrar por canal específico",
        categoria="Filtrar por categoría específica"
    )
    @app_commands.checks.has_permissions(manage_channels=True, manage_messages=True)
    async def list_messages(
        self,
        interaction: Interaction,
        canal: Optional[TextChannel] = None,
        categoria: Optional[CategoryChannel] = None,
    ):
        """Lista todos los mensajes automáticos configurados"""
        
        # Obtener mensajes según los filtros
        if canal:
            messages, error = self.service.get_by_channel_id(canal.id)
        elif categoria:
            messages, error = self.service.get_by_category_id(categoria.id)
        else:
            messages, error = self.service.get_all()
        
        if error:
            await send_error_message(interaction, constants.ERROR_GETTING_MESSAGES)
            return
        
        if not messages:
            embed = Embed(
                title=constants.NO_MESSAGES_FOUND,
                description="No se encontraron mensajes automáticos con los criterios especificados.",
                color=Color.orange()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Mostrar select para elegir mensaje a ver en detalle
        embed = Embed(
            title=constants.SHOWING_MESSAGES.format(count=len(messages)),
            description="Selecciona un mensaje para ver sus detalles:",
            color=Color.blue()
        )
        
        view = MessageSelectView(messages, "view", self.bot)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    ######################################
    ### Comando para eliminar mensajes ###
    ######################################
    @app_commands.command(name="eliminar", description=constants.COMMAND_DELETE_DESC)
    @app_commands.describe(
        canal="Filtrar por canal específico",
        categoria="Filtrar por categoría específica"
    )
    @app_commands.checks.has_permissions(manage_channels=True, manage_messages=True)
    async def delete_message(
        self,
        interaction: Interaction,
        canal: Optional[TextChannel] = None,
        categoria: Optional[CategoryChannel] = None,
    ):
        """Elimina un mensaje automático"""
        
        # Obtener mensajes según los filtros
        if canal:
            messages, error = self.service.get_by_channel_id(canal.id)
        elif categoria:
            messages, error = self.service.get_by_category_id(categoria.id)
        else:
            messages, error = self.service.get_all()
        
        if error:
            await send_error_message(interaction, constants.ERROR_GETTING_MESSAGES)
            return
        
        if not messages:
            embed = Embed(
                title=constants.NO_MESSAGES_FOUND,
                description=constants.TEXT_NO_MESSAGES_TO_DELETE,
                color=Color.orange()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Mostrar select para elegir mensaje a eliminar
        embed = Embed(
            title=constants.SELECT_MESSAGE_TO_DELETE,
            description=constants.TEXT_MESSAGES_FOUND_DELETE.format(count=len(messages)),
            color=Color.red()
        )
        
        view = MessageSelectView(messages, "delete", self.bot)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def on_app_command_error(self, interaction: Interaction, error: app_commands.AppCommandError):
        """Maneja errores de los comandos de aplicación"""
        if isinstance(error, app_commands.MissingPermissions):
            await send_error_message(interaction, constants.ERROR_PERMISSION_DENIED)
        else:
            await send_error_message(
                interaction, 
                constants.TEXT_UNEXPECTED_ERROR
            )


async def setup(bot):
    """Setup function para cargar el cog"""
    await bot.add_cog(AutomaticMessagesCommands(bot), guild=discord.Object(guild_id))
