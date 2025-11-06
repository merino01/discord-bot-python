from uuid import uuid4
import discord
from discord import Interaction, SelectOption
from discord.ui import View, Modal, TextInput
from ..models import AutomaticMessage
from ..services import AutomaticMessagesService
from ..utils import send_error_message, validate_message_content
from ..tasks import reload_all_schedules
from i18n import __


class ProgramMessageModal(Modal):
    """Modal para programar mensajes con programación por intervalo"""
    
    def __init__(self, title: str = constants.TITLE_SCHEDULE_MESSAGE):
        super().__init__(title=title)
        
        self.name_input = TextInput(
            label=constants.LABEL_MESSAGE_NAME,
            placeholder=constants.PLACEHOLDER_MESSAGE_NAME,
            max_length=constants.MAX_NAME_LENGTH,
            required=False
        )
        
        self.text_input = TextInput(
            label=constants.LABEL_MESSAGE_TEXT,
            placeholder=constants.PLACEHOLDER_MESSAGE_TEXT,
            style=discord.TextStyle.paragraph,
            max_length=constants.MAX_MESSAGE_LENGTH,
            required=True
        )
        
        self.add_item(self.name_input)
        self.add_item(self.text_input)
    
    async def on_submit(self, interaction: Interaction):
        # Esta implementación se completará en slash_commands.py
        await interaction.response.send_message(
            constants.TEXT_MODAL_COMPLETED,
            ephemeral=True
        )


class ScheduleConfigView(View):
    """Vista para configurar el tipo de programación"""
    
    def __init__(self, message_data: dict):
        super().__init__(timeout=300)  # 5 minutos
        self.message_data = message_data
        
        # Si ya tenemos el tipo de programación, mostrar botones de configuración
        if 'schedule_type' in message_data:
            self._add_config_buttons(message_data['schedule_type'])
        else:
            # Si no, mostrar el selector de tipo
            self._add_type_selector()
    
    def _add_type_selector(self):
        """Añade el selector de tipo de programación"""
        select = discord.ui.Select(
            placeholder=constants.SELECT_TYPE_PLACEHOLDER,
            options=[
                SelectOption(
                    label=constants.OPTION_INTERVAL_LABEL,
                    description=constants.OPTION_INTERVAL_DESC,
                    value="interval",
                    emoji="⏰"
                ),
                SelectOption(
                    label=constants.OPTION_DAILY_LABEL,
                    description=constants.OPTION_DAILY_DESC,
                    value="daily",
                    emoji="📅"
                ),
                SelectOption(
                    label=constants.OPTION_WEEKLY_LABEL,
                    description=constants.OPTION_WEEKLY_DESC,
                    value="weekly",
                    emoji="📆"
                ),
                SelectOption(
                    label=constants.OPTION_CHANNEL_CREATE_LABEL,
                    description=constants.OPTION_CHANNEL_CREATE_DESC,
                    value="on_channel_create",
                    emoji="🆕"
                )
            ]
        )
        select.callback = self._handle_type_selection
        self.add_item(select)
    
    def _add_config_buttons(self, schedule_type: str):
        """Añade botones de configuración según el tipo"""
        if schedule_type == "interval":
            button = discord.ui.Button(
                label=constants.TITLE_CONFIGURE_INTERVAL,
                style=discord.ButtonStyle.primary,
                emoji="⏰"
            )
            button.callback = self._configure_interval
            self.add_item(button)
        
        elif schedule_type in ["daily", "weekly"]:
            button = discord.ui.Button(
                label=constants.BUTTON_CONFIGURE_HOUR,
                style=discord.ButtonStyle.primary,
                emoji="🕐"
            )
            button.callback = self._configure_time
            self.add_item(button)
    
    async def _handle_type_selection(self, interaction: Interaction):
        """Maneja la selección del tipo de programación"""
        select = interaction.data['values'][0]
        schedule_type = select
        self.message_data['schedule_type'] = schedule_type
        
        # Según el tipo, mostrar diferentes configuraciones
        if schedule_type == "interval":
            from .interval_config import IntervalConfigView
            view = IntervalConfigView(self.message_data)
            embed = discord.Embed(
                title=constants.TITLE_CONFIGURE_INTERVAL,
                description=constants.DESC_CONFIGURE_INTERVAL,
                color=discord.Color.blue()
            )
            await interaction.response.edit_message(embed=embed, view=view)
            
        elif schedule_type == "daily":
            from .time_config import TimeConfigView
            view = TimeConfigView(self.message_data, schedule_type)
            embed = discord.Embed(
                title=constants.TITLE_DAILY_HOUR_CONFIG,
                description=constants.DESC_DAILY_CONFIG,
                color=discord.Color.blue()
            )
            await interaction.response.edit_message(embed=embed, view=view)
            
        elif schedule_type == "weekly":
            from .time_config import TimeConfigView
            view = TimeConfigView(self.message_data, schedule_type)
            embed = discord.Embed(
                title=constants.TITLE_WEEKLY_CONFIG,
                description=constants.DESC_WEEKLY_CONFIG,
                color=discord.Color.blue()
            )
            await interaction.response.edit_message(embed=embed, view=view)
            
        elif schedule_type == "on_channel_create":
            # Para este tipo, crear directamente el mensaje
            await self._create_channel_message(interaction)
    
    async def _configure_interval(self, interaction: Interaction):
        """Configurar intervalo"""
        from .interval_config import IntervalConfigView
        view = IntervalConfigView(self.message_data)
        embed = discord.Embed(
            title=constants.TITLE_CONFIGURE_INTERVAL,
            description=constants.DESC_CONFIGURE_INTERVAL,
            color=discord.Color.blue()
        )
        await interaction.response.edit_message(embed=embed, view=view)
    
    async def _configure_time(self, interaction: Interaction):
        """Configurar hora"""
        from .time_config import TimeConfigView
        schedule_type = self.message_data['schedule_type']
        view = TimeConfigView(self.message_data, schedule_type)
        
        title = constants.TITLE_DAILY_HOUR_CONFIG if schedule_type == "daily" else constants.TITLE_WEEKLY_CONFIG
        description = constants.DESC_DAILY_CONFIG if schedule_type == "daily" else constants.DESC_WEEKLY_CONFIG
        
        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.blue()
        )
        await interaction.response.edit_message(embed=embed, view=view)
    
    async def _create_channel_message(self, interaction: Interaction):
        """Crea directamente un mensaje para creación de canal"""
        try:
            # Validar que el mensaje tenga contenido útil
            is_valid, error_msg = validate_message_content(self.message_data)
            if not is_valid:
                await send_error_message(interaction, error_msg)
                return
            
            new_message = AutomaticMessage(
                id=str(uuid4()),
                channel_id=self.message_data.get('channel_id'),
                category_id=self.message_data.get('category_id'),
                text=self.message_data['text'],
                name=self.message_data.get('name'),
                interval=None,
                interval_unit=None,
                hour=None,
                minute=None,
                schedule_type=self.message_data['schedule_type'],
                weekdays=None,
                cron_expression=None
            )
            
            # Guardar en la base de datos
            service = AutomaticMessagesService()
            success, error = service.add(new_message)
            
            if error or not success:
                await send_error_message(interaction, constants.ERROR_CREATING_MESSAGE)
                return
            
            # IMPORTANTE: Recargar el scheduler después de crear el mensaje
            reload_all_schedules()
            
            # Mostrar confirmación
            embed = discord.Embed(
                title=f"{constants.EMOJI_SUCCESS} {constants.SUCCESS_MESSAGE_CREATED}",
                description=f"**{new_message.display_name}**\n\n"
                           f"{constants.TEXT_AUTO_SEND_CHANNEL_CREATE}",
                color=discord.Color.green()
            )
            
            await interaction.response.edit_message(embed=embed, view=None)
            
        except Exception as e:
            await send_error_message(interaction, f"Error creando el mensaje: {str(e)}")
