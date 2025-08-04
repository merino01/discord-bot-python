from uuid import uuid4
import discord
import json
from discord import Interaction, SelectOption
from discord.ui import View, Modal, TextInput, Select
from translator import __
from ..models import AutomaticMessage
from ..services import AutomaticMessagesService
from ..utils import send_error_message, validate_message_content
from ..tasks import reload_all_schedules


class IntervalConfigModal(Modal):
    """Modal para configurar intervalos"""

    def __init__(self, message_data: dict):
        super().__init__(title=__("automaticMessages.modals.intervalConfig.title"))
        self.message_data = message_data

        self.interval_input = TextInput(
            label=__("automaticMessages.modals.intervalConfig.intervalLabel"),
            placeholder=__("automaticMessages.modals.intervalConfig.intervalPlaceholder"),
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
                __("automaticMessages.intervalConfig.selectUnit"), view=view, ephemeral=True
            )
        except ValueError:
            await send_error_message(
                interaction, __("automaticMessages.errorMessages.invalidInterval")
            )


class IntervalUnitView(View):
    """Vista para seleccionar la unidad del intervalo"""

    def __init__(self, message_data: dict):
        super().__init__(timeout=60)
        self.message_data = message_data

    @discord.ui.select(
        placeholder=__("automaticMessages.intervalConfig.selectUnitPlaceholder"),
        options=[
            SelectOption(
                label=__("automaticMessages.intervalConfig.unitSeconds"), value="seconds", emoji="⏱️"
            ),
            SelectOption(
                label=__("automaticMessages.intervalConfig.unitMinutes"),
                value="minutes",
                emoji="⏰",
            ),
            SelectOption(
                label=__("automaticMessages.intervalConfig.unitHours"), value="hours", emoji="🕐"
            ),
        ],
    )
    async def select_unit(self, interaction: Interaction, select: Select):
        self.message_data['interval_unit'] = select.values[0]
        await self._create_message(interaction)

    async def _create_message(self, interaction: Interaction):
        """Crear el mensaje con configuración de intervalo"""
        await interaction.response.edit_message(
            content=__("automaticMessages.successMessages.messageConfigured"), view=None
        )


class IntervalConfigView(View):
    """Vista simple para configurar intervalos"""

    def __init__(self, message_data: dict):
        super().__init__(timeout=300)
        self.message_data = message_data

    @discord.ui.select(
        placeholder=__("automaticMessages.intervalConfig.selectQuickInterval"),
        custom_id="quick_interval_select",
        options=[
            SelectOption(
                label=__("automaticMessages.intervalConfig.option30Seconds"),
                value="30-seconds",
                emoji="⚡",
            ),
            SelectOption(
                label=__("automaticMessages.intervalConfig.option1Minute"),
                value="1-minutes",
                emoji="⏱️",
            ),
            SelectOption(
                label=__("automaticMessages.intervalConfig.option5Minutes"),
                value="5-minutes",
                emoji="🕐",
            ),
            SelectOption(
                label=__("automaticMessages.intervalConfig.option15Minutes"),
                value="15-minutes",
                emoji="🕐",
            ),
            SelectOption(
                label=__("automaticMessages.intervalConfig.option30Minutes"),
                value="30-minutes",
                emoji="🕑",
            ),
            SelectOption(
                label=__("automaticMessages.intervalConfig.option1Hour"),
                value="1-hours",
                emoji="🕒",
            ),
            SelectOption(
                label=__("automaticMessages.intervalConfig.option2Hours"),
                value="2-hours",
                emoji="🕓",
            ),
            SelectOption(
                label=__("automaticMessages.intervalConfig.option6Hours"),
                value="6-hours",
                emoji="🕕",
            ),
        ],
    )
    async def quick_interval_select(self, interaction: Interaction, select: Select):
        value_parts = select.values[0].split('-')
        interval = int(value_parts[0])
        unit = value_parts[1]

        await self._create_interval_message(interaction, interval, unit)

    @discord.ui.button(
        label=__("automaticMessages.buttons.customInterval"),
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
                await send_error_message(
                    interaction, __("automaticMessages.errors.creatingMessage")
                )
                return

            # IMPORTANTE: Recargar el scheduler después de crear el mensaje
            reload_all_schedules()

            # Mostrar confirmación
            unit_text = __("intervalUnits." + unit)
            embed = discord.Embed(
                title=f"{__('automaticMessages.emoji.success')} {__('automaticMessages.success.messageCreated')}",
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
        super().__init__(title=__("automaticMessages.modals.customInterval.title"))
        self.message_data = message_data

        self.interval_input = TextInput(
            label=__("automaticMessages.labels.intervalNumber"),
            placeholder=__("automaticMessages.placeholders.intervalNumber"),
            max_length=10,
            required=True,
        )

        self.unit_select = TextInput(
            label=__("automaticMessages.labels.intervalUnit"),
            placeholder=__("automaticMessages.placeholders.customUnit"),
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
                raise ValueError(__("automaticMessages.errorMessages.invalidInterval"))

            if unit not in ["seconds", "minutes", "hours"]:
                raise ValueError(__("automaticMessages.validation.intervalUnitError"))

            # Crear el mensaje
            view = IntervalConfigView(self.message_data)
            await view._create_interval_message(interaction, interval, unit)

        except ValueError as e:
            await send_error_message(interaction, f"{__('error')} {str(e)}")
