from typing import Optional
from uuid import uuid4
import discord
import json
import asyncio
from discord import Interaction
from discord.ui import View, Modal, TextInput
from modules.automatic_messages.models import AutomaticMessage
from modules.automatic_messages.services import AutomaticMessagesService
from modules.automatic_messages.utils import send_error_message
from modules.automatic_messages import constants
from modules.automatic_messages.tasks import reload_all_schedules


class MessageBuilderView(View):
    """Vista principal para construir un mensaje automático con botones"""

    def __init__(self, schedule_type: str, destination, name: Optional[str] = None):
        super().__init__(timeout=600)  # 10 minutos
        self.schedule_type = schedule_type
        self.destination = destination
        self.name = name

        # Datos del mensaje en construcción
        self.message_data = {
            'text': '',
            'embed_config': None,
            'attachment_image_url': None,  # Imagen como attachment independiente
            'name': name,
            'schedule_type': schedule_type,
        }

        # Determinar si es canal o categoría
        if isinstance(destination, discord.CategoryChannel):
            self.message_data['category_id'] = destination.id
            self.message_data['channel_id'] = None
        else:
            self.message_data['channel_id'] = destination.id
            self.message_data['category_id'] = None

    @discord.ui.button(
        label=constants.LABEL_ADD_TEXT, style=discord.ButtonStyle.secondary, emoji="📝", row=0
    )
    async def add_text_button(self, interaction: Interaction, button: discord.ui.Button):
        """Botón para añadir o editar texto del mensaje"""
        modal = MessageTextModal(self.message_data.get('text', ''))
        modal.callback_view = self
        await interaction.response.send_modal(modal)

    @discord.ui.button(
        label=constants.LABEL_ADD_EMBED, style=discord.ButtonStyle.secondary, emoji="🎨", row=0
    )
    async def add_embed_button(self, interaction: Interaction, button: discord.ui.Button):
        """Botón para añadir o editar embed"""
        modal = EmbedBuilderModal(self.message_data.get('embed_config', {}))
        modal.callback_view = self
        await interaction.response.send_modal(modal)

    @discord.ui.button(
        label=constants.LABEL_IMAGE_ATTACHMENT,
        style=discord.ButtonStyle.secondary,
        emoji="🖼️",
        row=0,
    )
    async def add_image_button(self, interaction: Interaction, button: discord.ui.Button):
        """Botón para añadir imagen como attachment independiente"""
        modal = ImageBuilderModal(self.message_data.get('attachment_image_url', ''))
        modal.callback_view = self
        await interaction.response.send_modal(modal)

    @discord.ui.button(
        label=constants.LABEL_COMPLETE, style=discord.ButtonStyle.success, emoji="✅", row=1
    )
    async def complete_button(self, interaction: Interaction, button: discord.ui.Button):
        """Botón para completar y programar el mensaje"""
        # Validar que hay contenido
        if (
            not self.message_data.get('text')
            and not self.message_data.get('embed_config')
            and not self.message_data.get('attachment_image_url')
        ):
            await send_error_message(interaction, constants.ERROR_NO_CONTENT_BEFORE_COMPLETE)
            return

        # Mostrar mensaje de configuración completada
        embed = discord.Embed(
            title=constants.TITLE_CONFIG_COMPLETED,
            description=constants.DESC_CONFIG_COMPLETED,
            color=discord.Color.green(),
        )

        embed.add_field(
            name=constants.FIELD_NAME_SUMMARY, value=self._get_content_summary(), inline=False
        )

        # Pequeña pausa visual y luego continuar
        await interaction.response.edit_message(embed=embed, view=None)

        # Esperar un poco y luego mostrar la configuración de programación
        await asyncio.sleep(1.5)

        # Continuar con la configuración de programación
        if self.schedule_type == "on_channel_create":
            # Para mensajes de creación de canal, crear directamente
            # Usar followup porque ya respondimos antes
            await self._create_channel_message_directly_followup(interaction)
        else:
            # Para otros tipos, mostrar configuración de programación
            from .schedule_config import ScheduleConfigView

            view = ScheduleConfigView(self.message_data)

            embed = discord.Embed(
                title=constants.TITLE_CONFIG_PROGRAMMING,
                description=self._get_content_summary()
                + "\n\nAhora configura cuándo se debe enviar el mensaje:",
                color=discord.Color.blue(),
            )

            await interaction.edit_original_response(embed=embed, view=view)

    @discord.ui.button(
        label=constants.LABEL_CANCEL, style=discord.ButtonStyle.danger, emoji="❌", row=1
    )
    async def cancel_button(self, interaction: Interaction, button: discord.ui.Button):
        """Botón para cancelar la configuración"""
        embed = discord.Embed(
            title=constants.TITLE_CONFIG_CANCELLED,
            description=constants.DESC_CONFIG_CANCELLED,
            color=discord.Color.red(),
        )
        await interaction.response.edit_message(embed=embed, view=None)

    def _get_content_summary(self) -> str:
        """Genera un resumen del contenido configurado"""
        summary = "**📋 Resumen del mensaje:**\n"

        if self.message_data.get('text'):
            text_preview = self.message_data['text'][:100]
            if len(self.message_data['text']) > 100:
                text_preview += "..."
            summary += f"📝 **Texto:** {text_preview}\n"

        if self.message_data.get('embed_config'):
            embed_config = self.message_data['embed_config']
            embed_title = embed_config.get('title', 'Sin título')
            has_embed_image = " + imagen" if embed_config.get('image') else ""
            summary += f"🎨 **Embed:** {embed_title}{has_embed_image}\n"

        if self.message_data.get('attachment_image_url'):
            summary += "🖼️ **Imagen (Attachment):** Configurada\n"

        return summary

    async def update_embed(self, interaction: Interaction):
        """Actualiza el embed principal con el estado actual"""
        embed = discord.Embed(
            title=constants.TITLE_MESSAGE_BUILDER,
            description=constants.DESC_MESSAGE_BUILDER,
            color=discord.Color.blue(),
        )

        # Información básica
        embed.add_field(
            name=constants.FIELD_NAME_BASIC_CONFIG,
            value=f"**📍 Destino:** {self.destination.mention}\n"
            f"**⏰ Tipo:** {self._get_schedule_type_display()}\n"
            f"**📝 Nombre:** {self.name or 'Sin nombre'}",
            inline=False,
        )

        # Estado del contenido
        content_status = []
        if self.message_data.get('text'):
            content_status.append("✅ Texto configurado")
        else:
            content_status.append("❌ Sin texto")

        if self.message_data.get('embed_config'):
            content_status.append("✅ Embed configurado")
        else:
            content_status.append("❌ Sin embed")

        if self.message_data.get('attachment_image_url'):
            content_status.append("✅ Imagen configurada")
        else:
            content_status.append("❌ Sin imagen")

        embed.add_field(
            name=constants.FIELD_NAME_CONTENT_STATUS, value="\n".join(content_status), inline=False
        )

        # Vista previa del contenido si existe
        if any(
            [
                self.message_data.get('text'),
                self.message_data.get('embed_config'),
                self.message_data.get('attachment_image_url'),
            ]
        ):
            embed.add_field(
                name=constants.FIELD_NAME_PREVIEW, value=self._get_content_summary(), inline=False
            )

        await interaction.response.edit_message(embed=embed, view=self)

    def _get_schedule_type_display(self) -> str:
        """Convierte el tipo de programación a un formato amigable"""
        displays = {
            "interval": constants.SCHEDULE_INTERVAL_DISPLAY,
            "daily": constants.SCHEDULE_DAILY_DISPLAY,
            "weekly": constants.SCHEDULE_WEEKLY_DISPLAY,
            "on_channel_create": constants.SCHEDULE_CHANNEL_CREATE_DISPLAY,
        }
        return displays.get(self.schedule_type, self.schedule_type)

    async def _create_channel_message_directly_followup(self, interaction: Interaction):
        """Crea directamente un mensaje para creación de canal usando followup"""
        try:
            # Generar ID único
            message_id = str(uuid4())

            # Preparar el texto con configuración avanzada si existe
            final_text = self.message_data.get('text', '')
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

            # Crear el mensaje automático
            new_message = AutomaticMessage(
                id=message_id,
                channel_id=self.message_data.get('channel_id'),
                category_id=self.message_data.get('category_id'),
                text=final_text,
                name=self.message_data.get('name') or f"Mensaje {message_id[:8]}",
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
                await interaction.followup.send(
                    embed=discord.Embed(
                        title=constants.TITLE_ERROR_EMOJI,
                        description=constants.ERROR_CREATING_MESSAGE,
                        color=discord.Color.red(),
                    ),
                    ephemeral=True,
                )
                return

            # Recargar el scheduler
            reload_all_schedules()

            # Mostrar confirmación
            embed = discord.Embed(
                title=f"✅ {constants.SUCCESS_MESSAGE_CREATED}",
                description=f"**{new_message.display_name}**\n\n"
                f"{constants.TEXT_AUTO_SEND_CHANNEL_CREATE}\n\n"
                f"{self._get_content_summary()}",
                color=discord.Color.green(),
            )

            await interaction.edit_original_response(embed=embed, view=None)

        except Exception as e:
            await interaction.followup.send(
                embed=discord.Embed(
                    title=constants.TITLE_ERROR_EMOJI,
                    description=f"Error creando el mensaje: {str(e)}",
                    color=discord.Color.red(),
                ),
                ephemeral=True,
            )

    async def _create_channel_message_directly(self, interaction: Interaction):
        """Crea directamente un mensaje para creación de canal"""
        try:
            # Generar ID único
            message_id = str(uuid4())

            # Preparar el texto con configuración avanzada si existe
            final_text = self.message_data.get('text', '')
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

            # Crear el mensaje automático
            new_message = AutomaticMessage(
                id=message_id,
                channel_id=self.message_data.get('channel_id'),
                category_id=self.message_data.get('category_id'),
                text=final_text,
                name=self.message_data.get('name') or f"Mensaje {message_id[:8]}",
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
                await send_error_message(interaction, constants.ERROR_CREATING_MESSAGE)
                return

            # Recargar el scheduler
            reload_all_schedules()

            # Mostrar confirmación
            embed = discord.Embed(
                title=f"✅ {constants.SUCCESS_MESSAGE_CREATED}",
                description=f"**{new_message.display_name}**\n\n"
                f"{constants.TEXT_AUTO_SEND_CHANNEL_CREATE}\n\n"
                f"{self._get_content_summary()}",
                color=discord.Color.green(),
            )

            await interaction.response.edit_message(embed=embed, view=None)

        except Exception as e:
            await send_error_message(interaction, f"Error creando el mensaje: {str(e)}")


class MessageTextModal(Modal):
    """Modal para añadir/editar texto del mensaje"""

    def __init__(self, current_text: str = ""):
        super().__init__(title=constants.TITLE_TEXT_CONFIG)
        self.callback_view = None

        self.text_input = TextInput(
            label=constants.LABEL_MESSAGE_TEXT,
            placeholder=constants.PLACEHOLDER_MESSAGE_TEXT_FULL,
            style=discord.TextStyle.paragraph,
            required=False,
            max_length=2000,
            default=current_text,
        )

        self.add_item(self.text_input)

    async def on_submit(self, interaction: Interaction):
        try:
            # Actualizar el texto en la vista principal
            if self.callback_view:
                self.callback_view.message_data['text'] = self.text_input.value.strip()
                await self.callback_view.update_embed(interaction)
            else:
                await interaction.response.send_message(
                    constants.MESSAGE_TEXT_CONFIGURED, ephemeral=True
                )
        except Exception as e:
            await send_error_message(interaction, f"Error: {str(e)}")


class EmbedBuilderModal(Modal):
    """Modal para añadir/editar embed del mensaje"""

    def __init__(self, current_embed: dict = None):
        super().__init__(title=constants.TITLE_EMBED_CONFIG_MODAL)
        self.callback_view = None
        current_embed = current_embed or {}

        self.title_input = TextInput(
            label=constants.LABEL_EMBED_TITLE_OPTIONAL,
            placeholder=constants.PLACEHOLDER_WELCOME_EMBED,
            required=False,
            max_length=256,
            default=current_embed.get('title', ''),
        )

        self.description_input = TextInput(
            label=constants.LABEL_EMBED_DESCRIPTION,
            placeholder=constants.PLACEHOLDER_EMBED_DESCRIPTION_MODAL,
            style=discord.TextStyle.paragraph,
            required=False,
            max_length=4000,
            default=current_embed.get('description', ''),
        )

        self.color_input = TextInput(
            label=constants.LABEL_EMBED_COLOR,
            placeholder=constants.PLACEHOLDER_EMBED_COLOR_OPTIONS,
            required=False,
            max_length=20,
            default=current_embed.get('color', ''),
        )

        self.embed_image_input = TextInput(
            label=constants.LABEL_EMBED_IMAGE_URL,
            placeholder=constants.PLACEHOLDER_EMBED_IMAGE,
            required=False,
            max_length=500,
            default=current_embed.get('image', ''),
        )

        self.add_item(self.title_input)
        self.add_item(self.description_input)
        self.add_item(self.color_input)
        self.add_item(self.embed_image_input)

    async def on_submit(self, interaction: Interaction):
        try:
            # Crear configuración del embed
            embed_config = {
                'title': self.title_input.value.strip() if self.title_input.value else None,
                'description': (
                    self.description_input.value.strip() if self.description_input.value else None
                ),
                'color': self.color_input.value.strip() if self.color_input.value else 'blue',
                'image': (
                    self.embed_image_input.value.strip() if self.embed_image_input.value else None
                ),
            }

            # Validar que al menos hay título o descripción
            if not embed_config['title'] and not embed_config['description']:
                await send_error_message(interaction, constants.ERROR_EMBED_NO_CONTENT)
                return

            # Actualizar el embed en la vista principal
            if self.callback_view:
                self.callback_view.message_data['embed_config'] = embed_config
                await self.callback_view.update_embed(interaction)
            else:
                await interaction.response.send_message(
                    constants.MESSAGE_EMBED_CONFIGURED, ephemeral=True
                )
        except Exception as e:
            await send_error_message(interaction, f"Error: {str(e)}")


class ImageBuilderModal(Modal):
    """Modal para añadir imagen como attachment independiente"""

    def __init__(self, current_image: str = ""):
        super().__init__(title=constants.TITLE_IMAGE_CONFIG)
        self.callback_view = None

        self.image_url_input = TextInput(
            label=constants.LABEL_IMAGE_URL_ATTACHMENT,
            placeholder=constants.PLACEHOLDER_IMAGE_URL,
            style=discord.TextStyle.paragraph,
            required=False,
            max_length=500,
            default=current_image,
        )

        self.add_item(self.image_url_input)

    async def on_submit(self, interaction: Interaction):
        try:
            image_url = self.image_url_input.value.strip()

            # Actualizar la imagen en la vista principal
            if self.callback_view:
                self.callback_view.message_data['attachment_image_url'] = (
                    image_url if image_url else None
                )
                await self.callback_view.update_embed(interaction)
            else:
                await interaction.response.send_message(
                    constants.MESSAGE_IMAGE_CONFIGURED, ephemeral=True
                )
        except Exception as e:
            await send_error_message(interaction, f"Error: {str(e)}")
