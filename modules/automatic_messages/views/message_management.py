from typing import List
import discord
from discord import Interaction, SelectOption
from discord.ui import View, Select, Button
from translator import __
from ..models import AutomaticMessage
from ..services import AutomaticMessagesService
from ..utils import format_message_for_embed, send_error_message
from ..tasks import reload_all_schedules


class MessageSelectView(View):
    def __init__(self, messages: List[AutomaticMessage], action: str, bot):
        super().__init__(timeout=60)
        self.messages = messages
        self.action = action
        self.bot = bot
        self.service = AutomaticMessagesService()

        # Crear opciones para el select
        options = []
        for message in messages[:25]:  # Discord limita a 25 opciones
            label = message.display_name[:100]  # Limitar longitud
            description = self._get_message_description(message)
            options.append(SelectOption(label=label, description=description, value=message.id))

        if options:
            select = MessageSelect(options, action, self.bot)
            self.add_item(select)

    def _get_message_description(self, message: AutomaticMessage) -> str:
        """Genera una descripción corta para el mensaje"""
        if message.channel_id:
            channel = self.bot.get_channel(message.channel_id)
            target = (
                f"#{channel.name}" if channel else __("automaticMessages.summary.unknownChannel")
            )
        else:
            category = self.bot.get_channel(message.category_id)
            target = (
                f"{__('automaticMessages.summary.categoryPrefix')}{category.name}"
                if category
                else __("automaticMessages.summary.unknownCategory")
            )

        schedule_info = ""
        if message.schedule_type == "interval":
            schedule_info = __("automaticMessages.summary.interval")
        elif message.schedule_type == "daily":
            schedule_info = __("automaticMessages.summary.daily")
        elif message.schedule_type == "weekly":
            schedule_info = __("automaticMessages.summary.weekly")
        elif message.schedule_type == "on_channel_create":
            schedule_info = "Al crear canal"

        return f"{target} - {schedule_info}"[:100]


class MessageSelect(Select):
    def __init__(self, options: List[SelectOption], action: str, bot):
        placeholder = (
            __("automaticMessages.placeholders.selectToDelete")
            if action == "delete"
            else __("automaticMessages.placeholders.selectToView")
        )
        super().__init__(placeholder=placeholder, options=options)
        self.bot = bot
        self.action = action
        self.service = AutomaticMessagesService()

    async def callback(self, interaction: Interaction):
        message_id = self.values[0]
        message, error = self.service.get_by_id(message_id)

        if error or not message:
            await send_error_message(
                interaction,
                __("automaticMessages.errorMessages.messageNotFound").format(id=message_id),
            )
            return

        if self.action == "delete":
            # Mostrar confirmación de eliminación
            embed = format_message_for_embed(message, self.bot)
            embed.color = discord.Color.red()
            embed.description = __("automaticMessages.confirmDelete")

            confirm_view = ConfirmDeleteView(message)
            await interaction.response.edit_message(embed=embed, view=confirm_view)

        elif self.action == "view":
            # Mostrar detalles del mensaje
            embed = format_message_for_embed(message, self.bot)
            await interaction.response.edit_message(embed=embed, view=None)


class ConfirmDeleteView(View):
    def __init__(self, message: AutomaticMessage):
        super().__init__(timeout=30)
        self.message = message
        self.service = AutomaticMessagesService()

    @discord.ui.button(
        label=__("automaticMessages.buttons.confirmDelete"),
        style=discord.ButtonStyle.danger,
        emoji="✅",
    )
    async def confirm_delete(self, interaction: Interaction, button: Button):
        success, error = self.service.delete(self.message.id)

        if error or not success:
            await send_error_message(
                interaction, __("automaticMessages.errorMessages.errorDeletingMessage")
            )
            return

        # IMPORTANTE: Recargar el scheduler después de eliminar el mensaje
        reload_all_schedules()

        embed = discord.Embed(
            title=__("automaticMessages.successMessages.messageDeleted"),
            description=__("automaticMessages.messages.messageDeletedText").format(
                name=self.message.display_name
            ),
            color=discord.Color.green(),
        )

        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(
        label=__("automaticMessages.buttons.cancelDelete"),
        style=discord.ButtonStyle.secondary,
        emoji="❌",
    )
    async def cancel_delete(self, interaction: Interaction, button: Button):
        embed = discord.Embed(
            title=__("automaticMessages.messages.operationCancelledTitle"),
            description=__("automaticMessages.messages.noMessageDeleted"),
            color=discord.Color.orange(),
        )

        await interaction.response.edit_message(embed=embed, view=None)
