from uuid import uuid4
import discord
import json
from discord import Interaction, SelectOption
from discord.ui import View, Select, Modal, TextInput
from translator import __
from ..models import AutomaticMessage
from ..services import AutomaticMessagesService
from ..utils import send_error_message, validate_message_content
from ..tasks import reload_all_schedules


class WeekdaySelectionView(View):
    """Vista para seleccionar días de la semana con multiselect"""

    def __init__(self, message_data: dict):
        super().__init__(timeout=300)  # 5 minutos
        self.message_data = message_data
        self.selected_weekdays = set()

        # Crear el multiselect con ID único
        weekday_select = WeekdayMultiSelect()
        self.add_item(weekday_select)

    @discord.ui.button(
        label=__("automaticMessages.weeklyConfig.confirmButton"),
        style=discord.ButtonStyle.success,
        emoji="✅",
        custom_id="confirm_weekdays_button",
    )
    async def confirm_button(self, interaction: Interaction, button: discord.ui.Button):
        if not self.selected_weekdays:
            await send_error_message(
                interaction, __("automaticMessages.errorMessages.selectOneDay")
            )
            return

        # Convertir el set a lista ordenada y a JSON
        weekdays_list = sorted(self.selected_weekdays)
        self.message_data['weekdays'] = json.dumps(weekdays_list)

        # Crear el mensaje automático
        await self._create_weekly_message(interaction)

    async def _create_weekly_message(self, interaction: Interaction):
        """Crea el mensaje automático semanal con los datos configurados"""
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

            # Crear el objeto del mensaje
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
                weekdays=self.message_data['weekdays'],
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

            # Mostrar confirmación final
            weekday_names = [
                __(
                    "weekdays."
                    + [
                        "monday",
                        "tuesday",
                        "wednesday",
                        "thursday",
                        "friday",
                        "saturday",
                        "sunday",
                    ][day]
                )
                for day in sorted(self.selected_weekdays)
            ]
            days_text = ", ".join(weekday_names)

            embed = discord.Embed(
                title=f"{__('automaticMessages.emoji.success')} {__('automaticMessages.success.messageCreated')}",
                description=f"**{new_message.display_name}**\n\n"
                f"📅 Días: {days_text}\n"
                f"🕐 Hora: {self.message_data['hour']:02d}:{self.message_data['minute']:02d}",
                color=discord.Color.green(),
            )

            await interaction.response.edit_message(embed=embed, view=None)

        except Exception as e:
            await send_error_message(interaction, f"Error creando el mensaje: {str(e)}")


class WeekdayMultiSelect(Select):
    """Multiselect para elegir días de la semana"""

    def __init__(self):
        options = [
            SelectOption(label=__("weekdays.monday"), value="0", emoji="📅"),
            SelectOption(label=__("weekdays.tuesday"), value="1", emoji="📅"),
            SelectOption(label=__("weekdays.wednesday"), value="2", emoji="📅"),
            SelectOption(label=__("weekdays.thursday"), value="3", emoji="📅"),
            SelectOption(label=__("weekdays.friday"), value="4", emoji="📅"),
            SelectOption(label=__("weekdays.saturday"), value="5", emoji="📅"),
            SelectOption(label=__("weekdays.sunday"), value="6", emoji="📅"),
        ]

        super().__init__(
            placeholder=__("automaticMessages.placeholders.weekdaySelection"),
            options=options,
            min_values=1,
            max_values=7,
            custom_id="weekday_multiselect",
        )

    async def callback(self, interaction: Interaction):
        # Actualizar la selección en la vista padre
        view = self.view
        if isinstance(view, WeekdaySelectionView):
            view.selected_weekdays = {int(value) for value in self.values}

            # Crear mensaje de confirmación
            selected_days = [
                __(
                    "weekdays."
                    + [
                        "monday",
                        "tuesday",
                        "wednesday",
                        "thursday",
                        "friday",
                        "saturday",
                        "sunday",
                    ][int(day)]
                )
                for day in self.values
            ]
            days_text = ", ".join(selected_days)

            embed = discord.Embed(
                title=__("automaticMessages.weeklyConfig.daysSelectedTitle"),
                description=__("automaticMessages.weeklyConfig.confirmDaysDesc").format(
                    days=days_text
                ),
                color=discord.Color.blue(),
            )

            await interaction.response.edit_message(embed=embed, view=view)


class WeeklyConfigModal(Modal):
    """Modal para configurar programación semanal"""

    def __init__(self, message_data: dict):
        super().__init__(title=__("automaticMessages.modals.weeklyConfig.title"))
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

            # Mostrar selector de días de la semana
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
                    title=__("automaticMessages.errorMessages.invalidTime"),
                    description=__("automaticMessages.validation.validHour"),
                    color=discord.Color.red(),
                ),
                ephemeral=True,
            )
        except Exception as e:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=__("automaticMessages.errorMessages.unexpectedError"),
                    description=f"Error inesperado: {str(e)}",
                    color=discord.Color.red(),
                ),
                ephemeral=True,
            )
