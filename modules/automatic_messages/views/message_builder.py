import json
import asyncio
from typing import Optional
from uuid import uuid4
from discord import Interaction, CategoryChannel, ButtonStyle, TextStyle, Embed, Color
from discord.ui import View, Modal, TextInput, Button, button
from .. import utils, services, tasks, models, views
from translator import __


class MessageBuilderView(View):
    def __init__(self, schedule_type: str, destination, name: Optional[str] = None):
        super().__init__(timeout=600)  # 10 minutos
        self.schedule_type = schedule_type
        self.destination = destination
        self.name = name

        # Datos del mensaje en construcción
        self.message_data = {
            'text': '',
            'embed_config': None,
            'attachment_image_url': None,
            'name': name,
            'schedule_type': schedule_type,
        }

        # Determinar si es canal o categoría
        if isinstance(destination, CategoryChannel):
            self.message_data['category_id'] = destination.id
            self.message_data['channel_id'] = None
        else:
            self.message_data['channel_id'] = destination.id
            self.message_data['category_id'] = None

    @button(
        label=__("automaticMessages.configureMessageEmbed.addText"),
        style=ButtonStyle.secondary,
        emoji="📝",
        row=0,
    )
    async def add_text_button(self, interaction: Interaction, button: Button):
        """Botón para añadir o editar texto del mensaje"""
        modal = MessageTextModal(self.message_data.get('text', ''))
        modal.callback_view = self
        await interaction.response.send_modal(modal)

    @button(
        label=__("automaticMessages.configureMessageEmbed.addEmbed"),
        style=ButtonStyle.secondary,
        emoji="🎨",
        row=0,
    )
    async def add_embed_button(self, interaction: Interaction, button: Button):
        """Botón para añadir o editar embed"""
        modal = EmbedBuilderModal(self.message_data.get('embed_config', {}))
        modal.callback_view = self
        await interaction.response.send_modal(modal)

    @button(
        label=__("automaticMessages.configureMessageEmbed.addImage"),
        style=ButtonStyle.secondary,
        emoji="🖼️",
        row=0,
    )
    async def add_image_button(self, interaction: Interaction, button: Button):
        """Botón para añadir imagen como attachment independiente"""
        modal = ImageBuilderModal(self.message_data.get('attachment_image_url', ''))
        modal.callback_view = self
        await interaction.response.send_modal(modal)

    @button(
        label=__("automaticMessages.configureMessageEmbed.complete"),
        style=ButtonStyle.success,
        emoji="✅",
        row=1,
    )
    async def complete_button(self, interaction: Interaction, button: Button):
        """Botón para completar y programar el mensaje"""
        # Validar que hay contenido
        if (
            not self.message_data.get('text')
            and not self.message_data.get('embed_config')
            and not self.message_data.get('attachment_image_url')
        ):
            await utils.send_error_message(
                interaction, __("automaticMessages.errorMessages.noContentConfigured")
            )
            return

        # Mostrar mensaje de configuración completada
        embed = Embed(
            title=__("automaticMessages.configureMessageEmbed.completedTitle"),
            description=__("automaticMessages.configureMessageEmbed.completedDescription"),
            color=Color.green(),
        )

        embed.add_field(name=__("summary"), value=self._get_content_summary(), inline=False)

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
            view = views.ScheduleConfigView(self.message_data)

            embed = Embed(
                title=__("automaticMessages.configureMessageEmbed.configureScheduleTitle"),
                description=self._get_content_summary()
                + "\n\n"
                + __("automaticMessages.configureMessageEmbed.instructions.whenToSend"),
                color=Color.blue(),
            )

            await interaction.edit_original_response(embed=embed, view=view)

    @button(label=__("cancel"), style=ButtonStyle.danger, emoji="❌", row=1)
    async def cancel_button(self, interaction: Interaction, button: Button):
        """Botón para cancelar la configuración"""
        embed = Embed(
            title=__("automaticMessages.configureMessageEmbed.cancelledTitle"),
            description=__("automaticMessages.configureMessageEmbed.cancelledDescription"),
            color=Color.red(),
        )
        await interaction.response.edit_message(embed=embed, view=None)

    # TODO => Traduccion de esta funcion
    def _get_content_summary(self) -> str:
        summary = "**" + __("summary") + "**\n"

        if self.message_data.get('text'):
            text_preview = self.message_data['text'][:100]
            if len(self.message_data['text']) > 100:
                text_preview += "..."
            summary += f"**" + __("text") + ":** {text_preview}\n"

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
        embed = Embed(
            title=__("automaticMessages.configureMessageEmbed.title"),
            description=__("automaticMessages.configureMessageEmbed.description"),
            color=Color.blue(),
        )

        # Información básica
        embed.add_field(
            name=__("basicConfiguration"),
            value=f"{__('destination')} {self.destination.mention}\n"
            f"{__('type')} {self._get_schedule_type_display()}\n"
            f"{__('name')} {self.name or '' + __('automaticMessages.configureMessageEmbed.noName')}",
            inline=False,
        )

        # Estado del contenido
        content_status = []
        if self.message_data.get('text'):
            content_status.append(__("textConfigurated"))
        else:
            content_status.append(__("textNotConfigurated"))

        if self.message_data.get('embed_config'):
            content_status.append(__("embedConfigurated"))
        else:
            content_status.append(__("embedNotConfigurated"))

        if self.message_data.get('attachment_image_url'):
            content_status.append(__("imageConfigurated"))
        else:
            content_status.append(__("imageNotConfigurated"))

        embed.add_field(
            name=__("automaticMessages.configureMessageEmbed.contentStatus"),
            value="\n".join(content_status),
            inline=False,
        )

        # Vista previa del contenido si existe
        if any(
            [
                self.message_data.get('text'),
                self.message_data.get('embed_config'),
                self.message_data.get('attachment_image_url'),
            ]
        ):
            embed.add_field(name=__("preview"), value=self._get_content_summary(), inline=False)

        await interaction.response.edit_message(embed=embed, view=self)

    def _get_schedule_type_display(self) -> str:
        """Convierte el tipo de programación a un formato amigable"""
        displays = {
            "interval": __("automaticMessages.scheduleTypeChoices.interval"),
            "daily": __("automaticMessages.scheduleTypeChoices.daily"),
            "weekly": __("automaticMessages.scheduleTypeChoices.weekly"),
            "on_channel_create": __("automaticMessages.scheduleTypeChoices.on_channel_create"),
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
            new_message = models.AutomaticMessage(
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
            service = services.AutomaticMessagesService()
            success, error = service.add(new_message)

            if error or not success:
                await interaction.followup.send(
                    embed=Embed(
                        title=__("error"),
                        description=__("automaticMessages.errorMessages.errorCreatingMessage"),
                        color=Color.red(),
                    ),
                    ephemeral=True,
                )
                return

            # Recargar el scheduler
            tasks.reload_all_schedules()

            # Mostrar confirmación
            embed = Embed(
                title=__("automaticMessages.successMessages.messageCreated"),
                description=f"**{new_message.display_name}**\n\n"
                f"{__("automaticMessages.autoSendChannelCreate")}\n\n"
                f"{self._get_content_summary()}",
                color=Color.green(),
            )

            await interaction.edit_original_response(embed=embed, view=None)

        except Exception as e:
            await interaction.followup.send(
                embed=Embed(
                    title=__("error"),
                    description=__("automaticMessages.errorMessages.errorCreatingMessage"),
                    color=Color.red(),
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
            new_message = models.AutomaticMessage(
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
            service = services.AutomaticMessagesService()
            success, error = service.add(new_message)

            if error or not success:
                await utils.send_error_message(
                    interaction, __("automaticMessages.errorMessages.errorCreatingMessage")
                )
                return

            # Recargar el scheduler
            tasks.reload_all_schedules()

            # Mostrar confirmación
            embed = Embed(
                title=__("automaticMessages.successMessages.messageCreated"),
                description=f"**{new_message.display_name}**\n\n"
                f"{__("automaticMessages.autoSendChannelCreate")}\n\n"
                f"{self._get_content_summary()}",
                color=Color.green(),
            )

            await interaction.response.edit_message(embed=embed, view=None)

        except Exception as e:
            await utils.send_error_message(
                interaction, __("automaticMessages.errorMessages.errorCreatingMessage")
            )


class MessageTextModal(Modal):
    """Modal para añadir/editar texto del mensaje"""

    def __init__(self, current_text: str = ""):
        super().__init__(title=__("automaticMessages.configureMessageEmbed.textModal.title"))
        self.callback_view = None

        self.text_input = TextInput(
            label=__("automaticMessages.configureMessageEmbed.textModal.label"),
            placeholder=__("automaticMessages.configureMessageEmbed.textModal.placeholder"),
            style=TextStyle.paragraph,
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
                    __("automaticMessages.configureMessageEmbed.textModal.configured"),
                    ephemeral=True,
                )
        except Exception as e:
            await utils.send_error_message(
                interaction, __("automaticMessages.configureMessageEmbed.textModal.error")
            )


class EmbedBuilderModal(Modal):
    """Modal para añadir/editar embed del mensaje"""

    def __init__(self, current_embed: dict = None):
        super().__init__(title=__("automaticMessages.configureMessageEmbed.embedModal.title"))
        self.callback_view = None
        current_embed = current_embed or {}

        self.title_input = TextInput(
            label=__("automaticMessages.configureMessageEmbed.embedModal.titleInput.label"),
            placeholder=__(
                "automaticMessages.configureMessageEmbed.embedModal.titleInput.placeholder"
            ),
            required=False,
            max_length=256,
            default=current_embed.get('title', ''),
        )

        self.description_input = TextInput(
            label=__("automaticMessages.configureMessageEmbed.embedModal.descriptionInput.label"),
            placeholder=__(
                "automaticMessages.configureMessageEmbed.embedModal.descriptionInput.placeholder"
            ),
            style=TextStyle.paragraph,
            required=False,
            max_length=4000,
            default=current_embed.get('description', ''),
        )

        self.color_input = TextInput(
            label=__("automaticMessages.configureMessageEmbed.embedModal.colorInput.label"),
            placeholder=__(
                "automaticMessages.configureMessageEmbed.embedModal.colorInput.placeholder"
            ),
            required=False,
            max_length=20,
            default=current_embed.get('color', ''),
        )

        self.embed_image_input = TextInput(
            label=__("automaticMessages.configureMessageEmbed.embedModal.imageInput.label"),
            placeholder=__(
                "automaticMessages.configureMessageEmbed.embedModal.imageInput.placeholder"
            ),
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
                await utils.send_error_message(
                    interaction,
                    __("automaticMessages.configureMessageEmbed.embedModal.contentError"),
                )
                return

            # Actualizar el embed en la vista principal
            if self.callback_view:
                self.callback_view.message_data['embed_config'] = embed_config
                await self.callback_view.update_embed(interaction)
            else:
                await interaction.response.send_message(
                    __("automaticMessages.configureMessageEmbed.embedModal.success"), ephemeral=True
                )
        except Exception as e:
            await utils.send_error_message(
                interaction, __("automaticMessages.configureMessageEmbed.embedModal.error")
            )


class ImageBuilderModal(Modal):
    """Modal para añadir imagen como attachment independiente"""

    def __init__(self, current_image: str = ""):
        super().__init__(title=__("automaticMessages.configureMessageEmbed.imageModal.title"))
        self.callback_view = None

        self.image_url_input = TextInput(
            label=__("automaticMessages.configureMessageEmbed.imageModal.label"),
            placeholder=__("automaticMessages.configureMessageEmbed.imageModal.placeholder"),
            style=TextStyle.paragraph,
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
                    __("automaticMessages.configureMessageEmbed.imageModal.success"), ephemeral=True
                )
        except Exception as e:
            await utils.send_error_message(
                interaction, __("automaticMessages.configureMessageEmbed.imageModal.error")
            )
