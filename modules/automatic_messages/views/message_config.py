from typing import Optional
from uuid import uuid4
import discord
import json
from discord import Interaction
from discord.ui import View, Modal, TextInput
from modules.automatic_messages.models import AutomaticMessage
from modules.automatic_messages.services import AutomaticMessagesService
from modules.automatic_messages.utils import send_error_message, validate_message_content
from modules.automatic_messages import constants
from modules.automatic_messages.tasks import reload_all_schedules


class ProgramMessageTextModal(Modal):
    """Modal para capturar el texto del mensaje automático"""
    
    def __init__(self, schedule_type: str, destination, name: Optional[str] = None):
        super().__init__(title=constants.TITLE_MESSAGE_TEXT_MODAL)
        self.schedule_type = schedule_type
        self.destination = destination
        self.name = name
        
        # Input para el texto del mensaje
        self.text_input = TextInput(
            label=constants.LABEL_MESSAGE_TEXT,
            placeholder=constants.PLACEHOLDER_MESSAGE_TEXT,
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=2000
        )
        
        self.add_item(self.text_input)
    
    async def on_submit(self, interaction: Interaction):
        try:
            text = self.text_input.value.strip()

            await interaction.response.send_message(
                constants.TEXT_MODAL_DEBUG.format(type=self.schedule_type, text=text[:100]),
                ephemeral=True
            )
                
        except Exception as e:
            await interaction.response.send_message(
                constants.TEXT_ERROR_PREFIX.format(error=str(e)), 
                ephemeral=True
            )
    
    async def _show_message_config_options(self, interaction: Interaction, text: str):
        """Muestra opciones para configurar el mensaje (simple, embed, imagen)"""
        base_message_data = {
            'text': text,
            'name': self.name,
            'schedule_type': self.schedule_type
        }
        
        if isinstance(self.destination, discord.CategoryChannel):
            base_message_data['category_id'] = self.destination.id
            base_message_data['channel_id'] = None
        else:
            base_message_data['channel_id'] = self.destination.id
            base_message_data['category_id'] = None
        
        view = MessageConfigOptionsView(base_message_data)
        
        embed = discord.Embed(
            title=constants.TITLE_CONFIGURE_MESSAGE_TYPE,
            description=constants.DESC_MESSAGE_PREVIEW.format(
                preview=text[:200] + (constants.TEXT_CONTINUE_ELLIPSIS if len(text) > 200 else '') 
                        if text else constants.TEXT_NO_TEXT_ONLY_EMBED
            ) + "\n\n" + constants.DESC_HOW_TO_SEND,
            color=discord.Color.blue()
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class MessageConfigOptionsView(View):
    """Vista para seleccionar el tipo de mensaje (simple, embed, imagen)"""
    
    def __init__(self, base_message_data: dict):
        super().__init__(timeout=300)
        self.base_message_data = base_message_data
    
    @discord.ui.button(
        label=constants.BUTTON_SIMPLE_MESSAGE,
        style=discord.ButtonStyle.secondary,
        emoji="📝"
    )
    async def simple_message(self, interaction: Interaction, button: discord.ui.Button):
        """Continuar con mensaje simple"""
        await self._continue_to_schedule_config(interaction, self.base_message_data)
    
    @discord.ui.button(
        label=constants.BUTTON_CREATE_EMBED,
        style=discord.ButtonStyle.primary,
        emoji="🎨"
    )
    async def create_embed(self, interaction: Interaction, button: discord.ui.Button):
        """Mostrar modal para configurar embed"""
        from .embed_config import EmbedConfigModal
        modal = EmbedConfigModal(self.base_message_data)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(
        label=constants.BUTTON_ADD_IMAGE_BTN,
        style=discord.ButtonStyle.primary,
        emoji="🖼️"  
    )
    async def add_image(self, interaction: Interaction, button: discord.ui.Button):
        """Mostrar modal para configurar imagen"""
        from .embed_config import ImageConfigModal
        modal = ImageConfigModal(self.base_message_data)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(
        label=constants.BUTTON_EMBED_AND_IMAGE,
        style=discord.ButtonStyle.primary,
        emoji="✨"
    )
    async def embed_and_image(self, interaction: Interaction, button: discord.ui.Button):
        """Mostrar modal para configurar embed completo con imagen"""
        from .embed_config import FullEmbedConfigModal
        modal = FullEmbedConfigModal(self.base_message_data)
        await interaction.response.send_modal(modal)
    
    async def _continue_to_schedule_config(self, interaction: Interaction, message_data: dict):
        """Continúa a la configuración de programación"""
        if message_data['schedule_type'] == "on_channel_create":
            await self._create_channel_message_directly(interaction, message_data)
        else:
            from .schedule_config import ScheduleConfigView
            view = ScheduleConfigView(message_data)
            
            embed = discord.Embed(
                title=constants.TITLE_CONFIGURE_SCHEDULE,
                description=constants.DESC_SCHEDULE_CONFIG.format(
                    preview=message_data['text'][:200] + (constants.TEXT_CONTINUE_ELLIPSIS if len(message_data['text']) > 200 else '')
                ),
                color=discord.Color.blue()
            )
            
            await interaction.response.edit_message(embed=embed, view=view)
    
    async def _create_channel_message_directly(self, interaction: Interaction, message_data: dict):
        """Crea directamente un mensaje para creación de canal"""
        try:
            is_valid, error_msg = validate_message_content(message_data)
            if not is_valid:
                await send_error_message(interaction, error_msg)
                return
            
            message_id = str(uuid4())
            
            final_text = message_data['text']
            if message_data.get('embed_config') or message_data.get('attachment_image_url'):
                advanced_config = {}
                if message_data.get('embed_config'):
                    advanced_config['embed'] = message_data['embed_config']
                if message_data.get('attachment_image_url'):
                    advanced_config['attachment_image_url'] = message_data['attachment_image_url']
                
                final_text = f"{final_text}\n__ADVANCED_CONFIG__:{json.dumps(advanced_config)}"
            
            new_message = AutomaticMessage(
                id=message_id,
                channel_id=message_data.get('channel_id'),
                category_id=message_data.get('category_id'),
                text=final_text,
                name=message_data.get('name') or f"Mensaje {message_id[:8]}",
                interval=None,
                interval_unit=None,
                hour=None,
                minute=None,
                schedule_type=message_data['schedule_type'],
                weekdays=None,
                cron_expression=None
            )
            
            service = AutomaticMessagesService()
            success, error = service.add(new_message)
            
            if error or not success:
                await send_error_message(interaction, constants.ERROR_CREATING_MESSAGE)
                return
            
            reload_all_schedules()
            
            embed = discord.Embed(
                title=f"{constants.EMOJI_SUCCESS} {constants.SUCCESS_MESSAGE_CREATED}",
                description=f"**{new_message.display_name}**\n\n"
                           f"{constants.TEXT_AUTO_SEND_CHANNEL_CREATE}",
                color=discord.Color.green()
            )
            
            await interaction.response.edit_message(embed=embed, view=None)
            
        except Exception as e:
            await send_error_message(interaction, f"Error creando el mensaje: {str(e)}")
