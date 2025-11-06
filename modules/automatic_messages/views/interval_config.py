from uuid import uuid4
import discord
import json
from discord import Interaction, SelectOption
from discord.ui import View, Modal, TextInput, Select
from ..models import AutomaticMessage
from ..services import AutomaticMessagesService
from ..utils import send_error_message, validate_message_content
from .. import constants
from ..tasks import reload_all_schedules


class IntervalConfigModal(Modal):
    """Modal para configurar intervalos"""

    def __init__(self, message_data: dict):
        super().__init__(title=constants.TITLE_INTERVAL_CONFIG)
        self.message_data = message_data

        self.interval_input = TextInput(
            label=constants.LABEL_INTERVAL_NUMBER_SIMPLE,
            placeholder=constants.PLACEHOLDER_INTERVAL_EXAMPLE,
            max_length=10,
            required=True,
        )

        self.add_item(self.interval_input)

    async def on_submit(self, interaction: Interaction):
        try:
            interval = int(self.interval_input.value)
            if interval <= 0:
                raise ValueError("El intervalo debe ser positivo")

            self.message_data['interval'] = interval

            # Mostrar opciones de unidad
            view = IntervalUnitView(self.message_data)
            await interaction.response.send_message(
                "Selecciona la unidad de tiempo:", view=view, ephemeral=True
            )
        except ValueError:
            await send_error_message(interaction, constants.ERROR_INVALID_INTERVAL)


class IntervalUnitView(View):
    """Vista para seleccionar la unidad del intervalo"""

    def __init__(self, message_data: dict):
        super().__init__(timeout=60)
        self.message_data = message_data

    @discord.ui.select(
        placeholder=constants.PLACEHOLDER_TIME_UNIT,
        options=[
            SelectOption(label=constants.LABEL_SECONDS, value="seconds", emoji="⏱️"),
            SelectOption(label=constants.LABEL_MINUTES, value="minutes", emoji="⏰"),
            SelectOption(label=constants.LABEL_HOURS, value="hours", emoji="🕐"),
        ],
    )
    async def select_unit(self, interaction: Interaction, select: Select):
        self.message_data['interval_unit'] = select.values[0]
        await self._create_message(interaction)

    async def _create_message(self, interaction: Interaction):
        """Crear el mensaje con configuración de intervalo"""
        await interaction.response.edit_message(
            content=constants.MESSAGE_AUTO_CONFIGURED, view=None
        )


class IntervalConfigView(View):
    """Vista simple para configurar intervalos"""

    def __init__(self, message_data: dict):
        super().__init__(timeout=300)
        self.message_data = message_data

    @discord.ui.select(
        placeholder=constants.SELECT_INTERVAL_PLACEHOLDER,
        custom_id="quick_interval_select",
        options=[
            SelectOption(label=constants.OPTION_30_SECONDS, value="30-seconds", emoji="⚡"),
            SelectOption(label=constants.OPTION_1_MINUTE, value="1-minutes", emoji="⏱️"),
            SelectOption(label=constants.OPTION_5_MINUTES, value="5-minutes", emoji="🕐"),
            SelectOption(label=constants.OPTION_15_MINUTES, value="15-minutes", emoji="🕐"),
            SelectOption(label=constants.OPTION_30_MINUTES, value="30-minutes", emoji="🕑"),
            SelectOption(label=constants.OPTION_1_HOUR, value="1-hours", emoji="🕒"),
            SelectOption(label=constants.OPTION_2_HOURS, value="2-hours", emoji="🕓"),
            SelectOption(label=constants.OPTION_6_HOURS, value="6-hours", emoji="🕕"),
        ],
    )
    async def quick_interval_select(self, interaction: Interaction, select: Select):
        value_parts = select.values[0].split('-')
        interval = int(value_parts[0])
        unit = value_parts[1]

        await self._create_interval_message(interaction, interval, unit)

    @discord.ui.button(
        label=constants.BUTTON_CUSTOM_INTERVAL,
        style=discord.ButtonStyle.secondary,
        emoji="⚙️",
        custom_id="custom_interval_button",
        row=1,
    )
    async def custom_interval_button(self, interaction: Interaction, button: discord.ui.Button):
        modal = CustomIntervalModal(self.message_data)
        await interaction.response.send_modal(modal)

    async def _create_interval_message(self, interaction: Interaction, interval: int, unit: str):
        """Crea el mensaje automático con intervalo"""
        try:
            # Validar que el mensaje tenga contenido útil
            is_valid, error_msg = validate_message_content(self.message_data)
            if not is_valid:
                await send_error_message(interaction, error_msg)
                return

            # Preparar el texto con configuración avanzada si existe
            final_text = self.message_data['text']
            if self.message_data.get('embed_config') or self.message_data.get(
                'attachment_image_url'
            ):
                advanced_config = {}
                if self.message_data.get('embed_config'):
                    advanced_config['embed'] = self.message_data['embed_config']
                if self.message_data.get('attachment_image_url'):
                    advanced_config['attachment_image_url'] = self.message_data[
                        'attachment_image_url'
                    ]

                final_text = f"{final_text}\n__ADVANCED_CONFIG__:{json.dumps(advanced_config)}"

            new_message = AutomaticMessage(
                id=str(uuid4()),
                channel_id=self.message_data.get('channel_id'),
                category_id=self.message_data.get('category_id'),
                text=final_text,
                name=self.message_data.get('name'),
                interval=interval,
                interval_unit=unit,
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
                await send_error_message(interaction, constants.ERROR_CREATING_MESSAGE)
                return

            # IMPORTANTE: Recargar el scheduler después de crear el mensaje
            reload_all_schedules()

            # Mostrar confirmación
            unit_text = constants.INTERVAL_UNIT_TRANSLATIONS.get(unit, unit)
            embed = discord.Embed(
                title=f"{constants.EMOJI_SUCCESS} {constants.SUCCESS_MESSAGE_CREATED}",
                description=f"**{new_message.display_name}**\n\n"
                f"⏰ Se enviará cada {interval} {unit_text}",
                color=discord.Color.green(),
            )

            await interaction.response.edit_message(embed=embed, view=None)

        except Exception as e:
            await send_error_message(interaction, f"Error creando el mensaje: {str(e)}")


class CustomIntervalModal(Modal):
    """Modal para configurar un intervalo personalizado"""

    def __init__(self, message_data: dict):
        super().__init__(title=constants.TITLE_CUSTOM_INTERVAL)
        self.message_data = message_data

        self.interval_input = TextInput(
            label=constants.LABEL_INTERVAL_NUMBER,
            placeholder=constants.PLACEHOLDER_CUSTOM_INTERVAL,
            max_length=10,
            required=True,
        )

        self.unit_select = TextInput(
            label=constants.LABEL_UNIT_INTERVAL,
            placeholder=constants.PLACEHOLDER_UNIT_SELECT,
            max_length=10,
            required=True,
        )

        self.add_item(self.interval_input)
        self.add_item(self.unit_select)

    async def on_submit(self, interaction: Interaction):
        try:
            interval = int(self.interval_input.value)
            unit = self.unit_select.value.lower()

            if interval <= 0:
                raise ValueError(constants.ERROR_POSITIVE_INTERVAL)

            if unit not in ["seconds", "minutes", "hours"]:
                raise ValueError(constants.ERROR_VALID_UNIT)

            # Crear el mensaje
            view = IntervalConfigView(self.message_data)
            await view._create_interval_message(interaction, interval, unit)

        except ValueError as e:
            await send_error_message(interaction, f"{constants.TITLE_ERROR} {str(e)}")
