from uuid import uuid4
import discord
from discord import Interaction, SelectOption
from discord.ui import View, Modal, TextInput
from translator import __
from ..models import AutomaticMessage
from ..services import AutomaticMessagesService
from ..utils import send_error_message, validate_message_content
from .. import constants
from ..tasks import reload_all_schedules


class ProgramMessageModal(Modal):
    """Modal para programar mensajes con programación por intervalo"""

    def __init__(self, title: str = __("automaticMessages.modals.scheduleMessage.title")):
        super().__init__(title=title)

        self.name_input = TextInput(
            label=__("automaticMessages.modals.scheduleMessage.nameLabel"),
            placeholder=__("automaticMessages.modals.scheduleMessage.namePlaceholder"),
            max_length=constants.MAX_NAME_LENGTH,
            required=False,
        )

        self.text_input = TextInput(
            label=__("automaticMessages.modals.scheduleMessage.textLabel"),
            placeholder=__("automaticMessages.modals.scheduleMessage.textPlaceholder"),
            style=discord.TextStyle.paragraph,
            max_length=constants.MAX_MESSAGE_LENGTH,
            required=True,
        )

        self.add_item(self.name_input)
        self.add_item(self.text_input)

    async def on_submit(self, interaction: Interaction):
        # Esta implementación se completará en slash_commands.py
        await interaction.response.send_message(
            __("automaticMessages.modals.scheduleMessage.completedText"), ephemeral=True
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
            placeholder=__("automaticMessages.scheduleConfig.selectTypePlaceholder"),
            options=[
                SelectOption(
                    label=__("automaticMessages.scheduleConfig.intervalLabel"),
                    description=__("automaticMessages.scheduleConfig.intervalDesc"),
                    value="interval",
                    emoji="⏰",
                ),
                SelectOption(
                    label=__("automaticMessages.scheduleConfig.dailyLabel"),
                    description=__("automaticMessages.scheduleConfig.dailyDesc"),
                    value="daily",
                    emoji="📅",
                ),
                SelectOption(
                    label=__("automaticMessages.scheduleConfig.weeklyLabel"),
                    description=__("automaticMessages.scheduleConfig.weeklyDesc"),
                    value="weekly",
                    emoji="📆",
                ),
                SelectOption(
                    label=__("automaticMessages.scheduleConfig.channelCreateLabel"),
                    description=__("automaticMessages.scheduleConfig.channelCreateDesc"),
                    value="on_channel_create",
                    emoji="🆕",
                ),
            ],
        )
        select.callback = self._handle_type_selection
        self.add_item(select)

    def _add_config_buttons(self, schedule_type: str):
        """Añade botones de configuración según el tipo"""
        if schedule_type == "interval":
            button = discord.ui.Button(
                label=__("automaticMessages.modals.intervalConfig.title"),
                style=discord.ButtonStyle.primary,
                emoji="⏰",
            )
            button.callback = self._configure_interval
            self.add_item(button)

        elif schedule_type in ["daily", "weekly"]:
            button = discord.ui.Button(
                label=__("automaticMessages.timeConfig.configureHourButton"),
                style=discord.ButtonStyle.primary,
                emoji="🕐",
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
                title=__("automaticMessages.modals.intervalConfig.title"),
                description=__("automaticMessages.intervalConfig.description"),
                color=discord.Color.blue(),
            )
            await interaction.response.edit_message(embed=embed, view=view)

        elif schedule_type == "daily":
            from .time_config import TimeConfigView

            view = TimeConfigView(self.message_data, schedule_type)
            embed = discord.Embed(
                title=__("automaticMessages.timeConfig.dailyTitle"),
                description=__("automaticMessages.timeConfig.dailyDescription"),
                color=discord.Color.blue(),
            )
            await interaction.response.edit_message(embed=embed, view=view)

        elif schedule_type == "weekly":
            from .time_config import TimeConfigView

            view = TimeConfigView(self.message_data, schedule_type)
            embed = discord.Embed(
                title=__("automaticMessages.timeConfig.weeklyTitle"),
                description=__("automaticMessages.timeConfig.weeklyDescription"),
                color=discord.Color.blue(),
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
            title=__("automaticMessages.modals.intervalConfig.title"),
            description=__("automaticMessages.intervalConfig.description"),
            color=discord.Color.blue(),
        )
        await interaction.response.edit_message(embed=embed, view=view)

    async def _configure_time(self, interaction: Interaction):
        """Configurar hora"""
        from .time_config import TimeConfigView

        schedule_type = self.message_data['schedule_type']
        view = TimeConfigView(self.message_data, schedule_type)

        title = (
            __("automaticMessages.timeConfig.dailyTitle")
            if schedule_type == "daily"
            else __("automaticMessages.timeConfig.weeklyTitle")
        )
        description = (
            __("automaticMessages.timeConfig.dailyDescription")
            if schedule_type == "daily"
            else __("automaticMessages.timeConfig.weeklyDescription")
        )

        embed = discord.Embed(title=title, description=description, color=discord.Color.blue())
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
                cron_expression=None,
            )

            # Guardar en la base de datos
            service = AutomaticMessagesService()
            success, error = service.add(new_message)

            if error or not success:
                await send_error_message(
                    interaction, __("automaticMessages.errors.creatingMessage")
                )
                return

            # IMPORTANTE: Recargar el scheduler después de crear el mensaje
            reload_all_schedules()

            # Mostrar confirmación
            embed = discord.Embed(
                title=f"{__('automaticMessages.emoji.success')} {__('automaticMessages.success.messageCreated')}",
                description=f"**{new_message.display_name}**\n\n"
                f"{__('automaticMessages.scheduleConfig.autoSendChannelCreate')}",
                color=discord.Color.green(),
            )

            await interaction.response.edit_message(embed=embed, view=None)

        except Exception as e:
            await send_error_message(interaction, f"Error creando el mensaje: {str(e)}")
