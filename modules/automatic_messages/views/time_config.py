from uuid import uuid4
import discord
import json
from discord import Interaction
from discord.ui import View, Modal, TextInput
from translator import __
from ..models import AutomaticMessage
from ..services import AutomaticMessagesService
from ..utils import send_error_message, validate_message_content
from ..tasks import reload_all_schedules


class TimeConfigView(View):
    """Vista para configurar hora (diario o semanal)"""

    def __init__(self, message_data: dict, schedule_type: str):
        super().__init__(timeout=300)
        self.message_data = message_data
        self.schedule_type = schedule_type

    @discord.ui.button(
        label=__("automaticMessages.timeConfig.configureTimeButton"),
        style=discord.ButtonStyle.primary,
        emoji="🕐",
        custom_id="configure_time_button",
    )
    async def time_button(self, interaction: Interaction, button: discord.ui.Button):
        modal = TimeConfigModal(self.message_data, self.schedule_type)
        await interaction.response.send_modal(modal)


class TimeConfigModal(Modal):
    """Modal para configurar la hora"""

    def __init__(self, message_data: dict, schedule_type: str):
        super().__init__(title=__("automaticMessages.modals.timeConfig.title"))
        self.message_data = message_data
        self.schedule_type = schedule_type

        self.hour_input = TextInput(
            label=__("automaticMessages.modals.timeConfig.hourLabel"),
            placeholder=(
                __("automaticMessages.modals.timeConfig.weeklyPlaceholder")
                if schedule_type == "weekly"
                else __("automaticMessages.modals.timeConfig.dailyPlaceholder")
            ),
            max_length=2,
            required=True,
        )

        self.minute_input = TextInput(
            label=__("automaticMessages.modals.timeConfig.minuteLabel"),
            placeholder=__("automaticMessages.modals.timeConfig.minutePlaceholder"),
            max_length=2,
            required=True,
        )

        self.add_item(self.hour_input)
        self.add_item(self.minute_input)

    async def on_submit(self, interaction: Interaction):
        try:
            hour = int(self.hour_input.value)
            minute = int(self.minute_input.value)

            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError(__("automaticMessages.errorMessages.hourMinuteInvalid"))

            self.message_data['hour'] = hour
            self.message_data['minute'] = minute

            if self.schedule_type == "daily":
                await self._create_daily_message(interaction)
            elif self.schedule_type == "weekly":
                # Mostrar selector de días
                from .weekly_config import WeekdaySelectionView

                view = WeekdaySelectionView(self.message_data)
                embed = discord.Embed(
                    title=__("automaticMessages.weeklyConfig.selectDaysTitle"),
                    description=__("automaticMessages.weeklyConfig.timeConfiguredDesc").format(
                        hour=hour, minute=minute
                    ),
                    color=discord.Color.blue(),
                )
                await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

        except ValueError:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=__("error"),
                    description=__("automaticMessages.errorMessages.hourMinuteInvalid"),
                    color=discord.Color.red(),
                ),
                ephemeral=True,
            )
        except Exception as e:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=__("error"),
                    description=__("automaticMessages.errorMessages.unexpectedError").format(
                        error=str(e)
                    ),
                    color=discord.Color.red(),
                ),
                ephemeral=True,
            )

    async def _create_daily_message(self, interaction: Interaction):
        """Crea un mensaje automático diario"""
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
                interval=None,
                interval_unit=None,
                hour=self.message_data['hour'],
                minute=self.message_data['minute'],
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
                f"📅 Se enviará todos los días a las {self.message_data['hour']:02d}:{self.message_data['minute']:02d}",
                color=discord.Color.green(),
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            await send_error_message(interaction, f"Error creando el mensaje: {str(e)}")


class DailyConfigModal(Modal):
    """Modal para configurar programación diaria"""

    def __init__(self, message_data: dict):
        super().__init__(title=__("automaticMessages.modals.dailyConfig.title"))
        self.message_data = message_data

        self.hour_input = TextInput(
            label=__("automaticMessages.labels.hour"),
            placeholder=__("automaticMessages.placeholders.hourExample"),
            max_length=2,
            required=True,
        )

        self.minute_input = TextInput(
            label=__("automaticMessages.labels.minute"),
            placeholder=__("automaticMessages.placeholders.minute"),
            max_length=2,
            required=True,
        )

        self.add_item(self.hour_input)
        self.add_item(self.minute_input)

    async def on_submit(self, interaction: Interaction):
        try:
            hour = int(self.hour_input.value)
            minute = int(self.minute_input.value)

            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError("Hora o minuto inválidos")

            self.message_data['hour'] = hour
            self.message_data['minute'] = minute

            await self._create_message(interaction)
        except ValueError:
            await send_error_message(
                interaction, __("automaticMessages.errorMessages.hourMinuteInvalid")
            )

    async def _create_message(self, interaction: Interaction):
        """Crear el mensaje con configuración diaria"""
        await interaction.response.send_message(
            __("automaticMessages.messages.autoConfigured"), ephemeral=True
        )
