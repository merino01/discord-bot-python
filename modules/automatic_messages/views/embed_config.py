import discord
from discord import Interaction
from discord.ui import Modal, TextInput
from translator import __
from modules.automatic_messages.utils import send_error_message


class EmbedConfigModal(Modal):
    """Modal para configurar un embed simple"""

    def __init__(self, base_message_data: dict):
        super().__init__(title=__("automaticMessages.modals.embedConfig.title"))
        self.base_message_data = base_message_data

        self.title_input = TextInput(
            label=__("automaticMessages.modals.embedConfig.titleLabel"),
            placeholder=__("automaticMessages.modals.embedConfig.titlePlaceholder"),
            required=False,
            max_length=256,
        )

        self.description_input = TextInput(
            label=__("automaticMessages.modals.embedConfig.descriptionLabel"),
            placeholder=__("automaticMessages.modals.embedConfig.descriptionPlaceholder"),
            style=discord.TextStyle.paragraph,
            required=False,
            max_length=4000,
        )

        self.color_input = TextInput(
            label=__("automaticMessages.modals.embedConfig.colorLabel"),
            placeholder=__("automaticMessages.modals.embedConfig.colorPlaceholder"),
            required=False,
            max_length=20,
        )

        self.add_item(self.title_input)
        self.add_item(self.description_input)
        self.add_item(self.color_input)

    async def on_submit(self, interaction: Interaction):
        try:
            title_value = self.title_input.value.strip() if self.title_input.value else ""
            description_value = (
                self.description_input.value.strip() if self.description_input.value else ""
            )
            color_value = self.color_input.value.strip() if self.color_input.value else ""

            embed_config = {
                'title': title_value if title_value else None,
                'description': (
                    description_value if description_value else self.base_message_data['text']
                ),
                'color': color_value if color_value else 'blue',
            }

            message_data = self.base_message_data.copy()
            message_data['embed_config'] = embed_config

            from .message_config import MessageConfigOptionsView

            view = MessageConfigOptionsView(self.base_message_data)
            await view._continue_to_schedule_config(interaction, message_data)

        except Exception as e:
            await send_error_message(
                interaction,
                __("automaticMessages.errorMessages.configuringEmbed").format(error=str(e)),
            )


class ImageConfigModal(Modal):
    """Modal para configurar solo una imagen"""

    def __init__(self, base_message_data: dict):
        super().__init__(title=__("automaticMessages.modals.imageModal.title"))
        self.base_message_data = base_message_data

        self.image_url_input = TextInput(
            label=__("automaticMessages.modals.imageModal.label"),
            placeholder=__("automaticMessages.modals.imageModal.placeholder"),
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=500,
        )

        self.add_item(self.image_url_input)

    async def on_submit(self, interaction: Interaction):
        try:
            image_url = self.image_url_input.value.strip()

            if not image_url:
                await send_error_message(
                    interaction, __("automaticMessages.errorMessages.imageUrlRequired")
                )
                return

            message_data = self.base_message_data.copy()
            message_data['attachment_image_url'] = image_url

            from .message_config import MessageConfigOptionsView

            view = MessageConfigOptionsView(self.base_message_data)
            await view._continue_to_schedule_config(interaction, message_data)

        except Exception as e:
            await send_error_message(
                interaction,
                __("automaticMessages.errorMessages.configuringImage").format(error=str(e)),
            )


class FullEmbedConfigModal(Modal):
    """Modal para configurar embed completo con imagen"""

    def __init__(self, base_message_data: dict):
        super().__init__(title=__("automaticMessages.configureMessageEmbed.embedModal.title"))
        self.base_message_data = base_message_data

        self.title_input = TextInput(
            label=__("automaticMessages.labels.embedTitle"),
            placeholder=__("automaticMessages.placeholders.embedTitle"),
            required=False,
            max_length=256,
        )

        self.description_input = TextInput(
            label=__("automaticMessages.labels.embedDescription"),
            placeholder=__("automaticMessages.placeholders.embedDescription"),
            style=discord.TextStyle.paragraph,
            required=False,
            max_length=4000,
        )

        self.color_input = TextInput(
            label=__("automaticMessages.labels.embedColor"),
            placeholder=__("automaticMessages.placeholders.embedColor"),
            required=False,
            max_length=20,
        )

        self.image_url_input = TextInput(
            label=__("automaticMessages.labels.imageUrl"),
            placeholder=__("automaticMessages.placeholders.imageUrl"),
            required=False,
            max_length=500,
        )

        self.add_item(self.title_input)
        self.add_item(self.description_input)
        self.add_item(self.color_input)
        self.add_item(self.image_url_input)

    async def on_submit(self, interaction: Interaction):
        try:
            # Obtener valores de los inputs
            title_value = self.title_input.value.strip() if self.title_input.value else ""
            description_value = (
                self.description_input.value.strip() if self.description_input.value else ""
            )
            color_value = self.color_input.value.strip() if self.color_input.value else ""
            image_value = self.image_url_input.value.strip() if self.image_url_input.value else ""

            # Preparar configuración del embed
            embed_config = {
                'title': title_value if title_value else None,
                'description': (
                    description_value if description_value else self.base_message_data['text']
                ),
                'color': color_value if color_value else 'blue',
            }

            # Actualizar los datos del mensaje
            message_data = self.base_message_data.copy()
            message_data['embed_config'] = embed_config

            if image_value:
                message_data['attachment_image_url'] = image_value

            # Continuar con la configuración de programación
            from .message_config import MessageConfigOptionsView

            view = MessageConfigOptionsView(self.base_message_data)
            await view._continue_to_schedule_config(interaction, message_data)

        except Exception as e:
            await send_error_message(
                interaction,
                __("automaticMessages.errorMessages.configuringFullEmbed").format(error=str(e)),
            )
