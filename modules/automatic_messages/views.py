from typing import List, Optional
from uuid import uuid4
import discord
import json
from discord import Interaction, SelectOption
from discord.ui import View, Select, Button, Modal, TextInput
from .models import AutomaticMessage
from .service import AutomaticMessagesService
from .utils import format_message_for_embed, send_error_message, send_success_message
from . import constants
from .tasks import reload_all_schedules


class ProgramMessageTextModal(Modal):
    """Modal para capturar el texto del mensaje automático"""
    
    def __init__(self, schedule_type: str, destination, name: Optional[str] = None):
        super().__init__(title=constants.TITLE_MESSAGE_TEXT_MODAL)
        self.schedule_type = schedule_type
        self.destination = destination
        self.name = name
        
        # Input para el texto del mensaje (permite múltiples líneas)
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
            # Obtener el texto
            text = self.text_input.value.strip()

            # Respuesta simple para debug
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
        # Crear datos base del mensaje
        base_message_data = {
            'text': text,
            'name': self.name,
            'schedule_type': self.schedule_type
        }
        
        # Determinar si es canal o categoría (solo uno de los dos)
        if isinstance(self.destination, discord.CategoryChannel):
            base_message_data['category_id'] = self.destination.id
            base_message_data['channel_id'] = None
        else:
            # Es un canal de texto
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
        # No hay configuración avanzada, continuar con la programación
        await self._continue_to_schedule_config(interaction, self.base_message_data)
    
    @discord.ui.button(
        label=constants.BUTTON_CREATE_EMBED,
        style=discord.ButtonStyle.primary,
        emoji="🎨"
    )
    async def create_embed(self, interaction: Interaction, button: discord.ui.Button):
        """Mostrar modal para configurar embed"""
        modal = EmbedConfigModal(self.base_message_data)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(
        label=constants.BUTTON_ADD_IMAGE_BTN,
        style=discord.ButtonStyle.primary,
        emoji="🖼️"  
    )
    async def add_image(self, interaction: Interaction, button: discord.ui.Button):
        """Mostrar modal para configurar imagen"""
        modal = ImageConfigModal(self.base_message_data)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(
        label=constants.BUTTON_EMBED_AND_IMAGE,
        style=discord.ButtonStyle.primary,
        emoji="✨"
    )
    async def embed_and_image(self, interaction: Interaction, button: discord.ui.Button):
        """Mostrar modal para configurar embed completo con imagen"""
        modal = FullEmbedConfigModal(self.base_message_data)
        await interaction.response.send_modal(modal)
    
    async def _continue_to_schedule_config(self, interaction: Interaction, message_data: dict):
        """Continúa a la configuración de programación"""
        if message_data['schedule_type'] == "on_channel_create":
            # Para mensajes de creación de canal, crear directamente
            await self._create_channel_message_directly(interaction, message_data)
        else:
            # Para otros tipos, mostrar configuración de programación
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
            # Validar que el mensaje tenga contenido útil
            is_valid, error_msg = validate_message_content(message_data)
            if not is_valid:
                await send_error_message(interaction, error_msg)
                return
            
            # Generar ID único
            message_id = str(uuid4())
            
            # Preparar el texto con configuración avanzada si existe
            final_text = message_data['text']
            if message_data.get('embed_config') or message_data.get('attachment_image_url'):
                advanced_config = {}
                if message_data.get('embed_config'):
                    advanced_config['embed'] = message_data['embed_config']
                if message_data.get('attachment_image_url'):
                    advanced_config['attachment_image_url'] = message_data['attachment_image_url']
                
                final_text = f"{final_text}\n__ADVANCED_CONFIG__:{json.dumps(advanced_config)}"
            
            # Crear el mensaje automático - asegurar que solo se use uno de los dos IDs
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
            
            # Guardar en la base de datos
            service = AutomaticMessagesService()
            success, error = service.add(new_message)
            
            if error or not success:
                await send_error_message(interaction, constants.ERROR_CREATING_MESSAGE)
                return
            
            # IMPORTANTE: Recargar el scheduler después de crear el mensaje
            reload_all_schedules()
            
            # Mostrar confirmación
            embed = discord.Embed(
                title=f"{constants.EMOJI_SUCCESS} {constants.SUCCESS_MESSAGE_CREATED}",
                description=f"**{new_message.display_name}**\n\n"
                           f"{constants.TEXT_AUTO_SEND_CHANNEL_CREATE}",
                color=discord.Color.green()
            )
            
            await interaction.response.edit_message(embed=embed, view=None)
            
        except Exception as e:
            await send_error_message(interaction, f"Error creando el mensaje: {str(e)}")


class EmbedConfigModal(Modal):
    """Modal para configurar un embed simple"""
    
    def __init__(self, base_message_data: dict):
        super().__init__(title=constants.TITLE_EMBED_CONFIG)
        self.base_message_data = base_message_data
        
        self.title_input = TextInput(
            label=constants.LABEL_EMBED_TITLE_OPTIONAL,
            placeholder=constants.PLACEHOLDER_EMBED_TITLE,
            required=False,
            max_length=256
        )
        
        self.description_input = TextInput(
            label=constants.LABEL_EMBED_DESCRIPTION,
            placeholder=constants.PLACEHOLDER_EMBED_DESCRIPTION,
            style=discord.TextStyle.paragraph,
            required=False,
            max_length=4000
        )
        
        self.color_input = TextInput(
            label=constants.LABEL_EMBED_COLOR,
            placeholder=constants.PLACEHOLDER_EMBED_COLOR,
            required=False,
            max_length=20
        )
        
        self.add_item(self.title_input)
        self.add_item(self.description_input)
        self.add_item(self.color_input)
    
    async def on_submit(self, interaction: Interaction):
        try:
            # Obtener valores de los inputs
            title_value = self.title_input.value.strip() if self.title_input.value else ""
            description_value = self.description_input.value.strip() if self.description_input.value else ""
            color_value = self.color_input.value.strip() if self.color_input.value else ""
            
            # Preparar configuración del embed
            embed_config = {
                'title': title_value if title_value else None,
                'description': description_value if description_value else self.base_message_data['text'],
                'color': color_value if color_value else 'blue'
            }
            
            # Actualizar los datos del mensaje
            message_data = self.base_message_data.copy()
            message_data['embed_config'] = embed_config
            
            # Continuar con la configuración de programación
            view = MessageConfigOptionsView(self.base_message_data)
            await view._continue_to_schedule_config(interaction, message_data)
            
        except Exception as e:
            await send_error_message(interaction, constants.ERROR_CONFIGURING_EMBED.format(error=str(e)))


class ImageConfigModal(Modal):
    """Modal para configurar solo una imagen"""
    
    def __init__(self, base_message_data: dict):
        super().__init__(title=constants.TITLE_IMAGE_CONFIG)
        self.base_message_data = base_message_data
        
        self.image_url_input = TextInput(
            label=constants.LABEL_IMAGE_URL_REQUIRED,
            placeholder=constants.PLACEHOLDER_IMAGE_URL,
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=500
        )
        
        self.add_item(self.image_url_input)
    
    async def on_submit(self, interaction: Interaction):
        try:
            image_url = self.image_url_input.value.strip()
            
            if not image_url:
                await send_error_message(interaction, constants.ERROR_IMAGE_URL_REQUIRED)
                return
            
            # Actualizar los datos del mensaje
            message_data = self.base_message_data.copy()
            message_data['attachment_image_url'] = image_url
            
            # Continuar con la configuración de programación
            view = MessageConfigOptionsView(self.base_message_data)
            await view._continue_to_schedule_config(interaction, message_data)
            
        except Exception as e:
            await send_error_message(interaction, constants.ERROR_CONFIGURING_IMAGE.format(error=str(e)))


class FullEmbedConfigModal(Modal):
    """Modal para configurar embed completo con imagen"""
    
    def __init__(self, base_message_data: dict):
        super().__init__(title=constants.TITLE_FULL_EMBED_CONFIG)
        self.base_message_data = base_message_data
        
        self.title_input = TextInput(
            label=constants.LABEL_EMBED_TITLE_OPTIONAL,
            placeholder=constants.PLACEHOLDER_EMBED_TITLE_EXAMPLE,
            required=False,
            max_length=256
        )
        
        self.description_input = TextInput(
            label=constants.LABEL_EMBED_DESCRIPTION,
            placeholder=constants.PLACEHOLDER_EMBED_DESCRIPTION_FULL,
            style=discord.TextStyle.paragraph,
            required=False,
            max_length=4000
        )
        
        self.color_input = TextInput(
            label=constants.LABEL_EMBED_COLOR,
            placeholder=constants.PLACEHOLDER_EMBED_COLOR,
            required=False,
            max_length=20
        )
        
        self.image_url_input = TextInput(
            label=constants.LABEL_IMAGE_URL_REQUIRED,
            placeholder=constants.PLACEHOLDER_IMAGE_URL,
            required=False,
            max_length=500
        )
        
        self.add_item(self.title_input)
        self.add_item(self.description_input)
        self.add_item(self.color_input)
        self.add_item(self.image_url_input)
    
    async def on_submit(self, interaction: Interaction):
        try:
            # Obtener valores de los inputs
            title_value = self.title_input.value.strip() if self.title_input.value else ""
            description_value = self.description_input.value.strip() if self.description_input.value else ""
            color_value = self.color_input.value.strip() if self.color_input.value else ""
            image_value = self.image_url_input.value.strip() if self.image_url_input.value else ""
            
            # Preparar configuración del embed
            embed_config = {
                'title': title_value if title_value else None,
                'description': description_value if description_value else self.base_message_data['text'],
                'color': color_value if color_value else 'blue'
            }
            
            # Actualizar los datos del mensaje
            message_data = self.base_message_data.copy()
            message_data['embed_config'] = embed_config
            
            if image_value:
                message_data['attachment_image_url'] = image_value
            
            # Continuar con la configuración de programación
            view = MessageConfigOptionsView(self.base_message_data)
            await view._continue_to_schedule_config(interaction, message_data)
            
        except Exception as e:
            await send_error_message(interaction, constants.ERROR_CONFIGURING_FULL_EMBED.format(error=str(e)))



class MessageSelectView(View):
    """Vista base para seleccionar mensajes automáticos"""
    
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
            options.append(SelectOption(
                label=label,
                description=description,
                value=message.id
            ))
        
        if options:
            select = MessageSelect(options, action, bot)
            self.add_item(select)
    
    def _get_message_description(self, message: AutomaticMessage) -> str:
        """Genera una descripción corta para el mensaje"""
        if message.channel_id:
            channel = self.bot.get_channel(message.channel_id)
            target = f"#{channel.name}" if channel else "Canal desconocido"
        else:
            category = self.bot.get_channel(message.category_id)
            target = f"{constants.CATEGORY_PREFIX}{category.name}" if category else constants.CATEGORY_UNKNOWN
        
        schedule_info = ""
        if message.schedule_type == "interval":
            schedule_info = "Intervalo"
        elif message.schedule_type == "daily":
            schedule_info = "Diario"
        elif message.schedule_type == "weekly":
            schedule_info = "Semanal"
        elif message.schedule_type == "on_channel_create":
            schedule_info = "Al crear canal"
        
        return f"{target} - {schedule_info}"[:100]


class MessageSelect(Select):
    """Select para elegir un mensaje automático"""
    
    def __init__(self, options: List[SelectOption], action: str, bot):
        placeholder = (
            constants.SELECT_PLACEHOLDER_DELETE if action == "delete" 
            else constants.SELECT_PLACEHOLDER_VIEW
        )
        super().__init__(placeholder=placeholder, options=options)
        self.action = action
        self.bot = bot
        self.service = AutomaticMessagesService()
    
    async def callback(self, interaction: Interaction):
        message_id = self.values[0]
        message, error = self.service.get_by_id(message_id)
        
        if error or not message:
            await send_error_message(
                interaction, 
                constants.ERROR_MESSAGE_NOT_FOUND.format(id=message_id)
            )
            return
        
        if self.action == "delete":
            # Mostrar confirmación de eliminación
            embed = format_message_for_embed(message, self.bot)
            embed.color = discord.Color.red()
            embed.description = constants.CONFIRM_DELETE
            
            confirm_view = ConfirmDeleteView(message)
            await interaction.response.edit_message(embed=embed, view=confirm_view)
        
        elif self.action == "view":
            # Mostrar detalles del mensaje
            embed = format_message_for_embed(message, self.bot)
            await interaction.response.edit_message(embed=embed, view=None)


class ConfirmDeleteView(View):
    """Vista de confirmación para eliminar mensajes"""
    
    def __init__(self, message: AutomaticMessage):
        super().__init__(timeout=30)
        self.message = message
        self.service = AutomaticMessagesService()
    
    @discord.ui.button(
        label=constants.BUTTON_CONFIRM_DELETE, 
        style=discord.ButtonStyle.danger,
        emoji="✅"
    )
    async def confirm_delete(self, interaction: Interaction, button: Button):
        success, error = self.service.delete(self.message.id)
        
        if error or not success:
            await send_error_message(interaction, constants.ERROR_DELETING_MESSAGE)
            return
        
        # IMPORTANTE: Recargar el scheduler después de eliminar el mensaje
        reload_all_schedules()
        
        embed = discord.Embed(
            title=constants.SUCCESS_MESSAGE_DELETED,
            description=constants.TEXT_MESSAGE_DELETED.format(name=self.message.display_name),
            color=discord.Color.green()
        )
        
        await interaction.response.edit_message(embed=embed, view=None)
    
    @discord.ui.button(
        label=constants.BUTTON_CANCEL_DELETE,
        style=discord.ButtonStyle.secondary,
        emoji="❌"
    )
    async def cancel_delete(self, interaction: Interaction, button: Button):
        embed = discord.Embed(
            title=constants.TITLE_OPERATION_CANCELLED,
            description=constants.TEXT_NO_MESSAGE_DELETED,
            color=discord.Color.orange()
        )
        
        await interaction.response.edit_message(embed=embed, view=None)


class ProgramMessageModal(Modal):
    """Modal para programar mensajes con programación por intervalo"""
    
    def __init__(self, title: str = constants.TITLE_SCHEDULE_MESSAGE):
        super().__init__(title=title)
        
        self.name_input = TextInput(
            label=constants.LABEL_MESSAGE_NAME,
            placeholder=constants.PLACEHOLDER_MESSAGE_NAME,
            max_length=constants.MAX_NAME_LENGTH,
            required=False
        )
        
        self.text_input = TextInput(
            label=constants.LABEL_MESSAGE_TEXT,
            placeholder=constants.PLACEHOLDER_MESSAGE_TEXT,
            style=discord.TextStyle.paragraph,
            max_length=constants.MAX_MESSAGE_LENGTH,
            required=True
        )
        
        self.add_item(self.name_input)
        self.add_item(self.text_input)
    
    async def on_submit(self, interaction: Interaction):
        # Esta implementación se completará en slash_commands.py
        await interaction.response.send_message(
            constants.TEXT_MODAL_COMPLETED,
            ephemeral=True
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
            placeholder=constants.SELECT_TYPE_PLACEHOLDER,
            options=[
                SelectOption(
                    label=constants.OPTION_INTERVAL_LABEL,
                    description=constants.OPTION_INTERVAL_DESC,
                    value="interval",
                    emoji="⏰"
                ),
                SelectOption(
                    label=constants.OPTION_DAILY_LABEL,
                    description=constants.OPTION_DAILY_DESC,
                    value="daily",
                    emoji="📅"
                ),
                SelectOption(
                    label=constants.OPTION_WEEKLY_LABEL,
                    description=constants.OPTION_WEEKLY_DESC,
                    value="weekly",
                    emoji="📆"
                ),
                SelectOption(
                    label=constants.OPTION_CHANNEL_CREATE_LABEL,
                    description=constants.OPTION_CHANNEL_CREATE_DESC,
                    value="on_channel_create",
                    emoji="🆕"
                )
            ]
        )
        select.callback = self._handle_type_selection
        self.add_item(select)
    
    def _add_config_buttons(self, schedule_type: str):
        """Añade botones de configuración según el tipo"""
        if schedule_type == "interval":
            button = discord.ui.Button(
                label=constants.TITLE_CONFIGURE_INTERVAL,
                style=discord.ButtonStyle.primary,
                emoji="⏰"
            )
            button.callback = self._configure_interval
            self.add_item(button)
        
        elif schedule_type in ["daily", "weekly"]:
            button = discord.ui.Button(
                label=constants.BUTTON_CONFIGURE_HOUR,
                style=discord.ButtonStyle.primary,
                emoji="🕐"
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
            view = IntervalConfigView(self.message_data)
            embed = discord.Embed(
                title=constants.TITLE_CONFIGURE_INTERVAL,
                description=constants.DESC_CONFIGURE_INTERVAL,
                color=discord.Color.blue()
            )
            await interaction.response.edit_message(embed=embed, view=view)
            
        elif schedule_type == "daily":
            view = TimeConfigView(self.message_data, schedule_type)
            embed = discord.Embed(
                title=constants.TITLE_DAILY_HOUR_CONFIG,
                description=constants.DESC_DAILY_CONFIG,
                color=discord.Color.blue()
            )
            await interaction.response.edit_message(embed=embed, view=view)
            
        elif schedule_type == "weekly":
            view = TimeConfigView(self.message_data, schedule_type)
            embed = discord.Embed(
                title=constants.TITLE_WEEKLY_CONFIG,
                description=constants.DESC_WEEKLY_CONFIG,
                color=discord.Color.blue()
            )
            await interaction.response.edit_message(embed=embed, view=view)
            
        elif schedule_type == "on_channel_create":
            # Para este tipo, crear directamente el mensaje
            await self._create_channel_message(interaction)
    
    async def _configure_interval(self, interaction: Interaction):
        """Configurar intervalo"""
        view = IntervalConfigView(self.message_data)
        embed = discord.Embed(
            title=constants.TITLE_CONFIGURE_INTERVAL,
            description=constants.DESC_CONFIGURE_INTERVAL,
            color=discord.Color.blue()
        )
        await interaction.response.edit_message(embed=embed, view=view)
    
    async def _configure_time(self, interaction: Interaction):
        """Configurar hora"""
        schedule_type = self.message_data['schedule_type']
        view = TimeConfigView(self.message_data, schedule_type)
        
        title = constants.TITLE_DAILY_HOUR_CONFIG if schedule_type == "daily" else constants.TITLE_WEEKLY_CONFIG
        description = constants.DESC_DAILY_CONFIG if schedule_type == "daily" else constants.DESC_WEEKLY_CONFIG
        
        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.blue()
        )
        await interaction.response.edit_message(embed=embed, view=view)
    
    async def _create_channel_message(self, interaction: Interaction):
        """Crea directamente un mensaje para creación de canal"""
        try:
            from uuid import uuid4
            from .models import AutomaticMessage
            
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
                cron_expression=None
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
            embed = discord.Embed(
                title=f"{constants.EMOJI_SUCCESS} {constants.SUCCESS_MESSAGE_CREATED}",
                description=f"**{new_message.display_name}**\n\n"
                           f"{constants.TEXT_AUTO_SEND_CHANNEL_CREATE}",
                color=discord.Color.green()
            )
            
            await interaction.response.edit_message(embed=embed, view=None)
            
        except Exception as e:
            await send_error_message(interaction, f"Error creando el mensaje: {str(e)}")


class IntervalConfigModal(Modal):
    """Modal para configurar intervalos"""
    
    def __init__(self, message_data: dict):
        super().__init__(title=constants.TITLE_INTERVAL_CONFIG)
        self.message_data = message_data
        
        self.interval_input = TextInput(
            label=constants.LABEL_INTERVAL_NUMBER_SIMPLE,
            placeholder=constants.PLACEHOLDER_INTERVAL_EXAMPLE,
            max_length=10,
            required=True
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
                "Selecciona la unidad de tiempo:",
                view=view,
                ephemeral=True
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
        ]
    )
    async def select_unit(self, interaction: Interaction, select: Select):
        self.message_data['interval_unit'] = select.values[0]
        await self._create_message(interaction)
    
    async def _create_message(self, interaction: Interaction):
        """Crear el mensaje con configuración de intervalo"""
        await interaction.response.edit_message(
            content=constants.MESSAGE_AUTO_CONFIGURED,
            view=None
        )


class DailyConfigModal(Modal):
    """Modal para configurar programación diaria"""
    
    def __init__(self, message_data: dict):
        super().__init__(title=constants.TITLE_DAILY_CONFIG)
        self.message_data = message_data
        
        self.hour_input = TextInput(
            label=constants.INPUT_HOUR_LABEL,
            placeholder=constants.PLACEHOLDER_HOUR_EXAMPLE,
            max_length=2,
            required=True
        )
        
        self.minute_input = TextInput(
            label=constants.INPUT_MINUTE_LABEL,
            placeholder=constants.INPUT_MINUTE_PLACEHOLDER,
            max_length=2,
            required=True
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
            await send_error_message(interaction, constants.ERROR_INVALID_TIME)
    
    async def _create_message(self, interaction: Interaction):
        """Crear el mensaje con configuración diaria"""
        await interaction.response.send_message(
            constants.MESSAGE_AUTO_CONFIGURED,
            ephemeral=True
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
        ]
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
        row=1
    )
    async def custom_interval_button(self, interaction: Interaction, button: discord.ui.Button):
        modal = CustomIntervalModal(self.message_data)
        await interaction.response.send_modal(modal)
    
    async def _create_interval_message(self, interaction: Interaction, interval: int, unit: str):
        """Crea el mensaje automático con intervalo"""
        try:
            from uuid import uuid4
            from .models import AutomaticMessage
            import json
            
            # Validar que el mensaje tenga contenido útil
            is_valid, error_msg = validate_message_content(self.message_data)
            if not is_valid:
                await send_error_message(interaction, error_msg)
                return
            
            # Preparar el texto con configuración avanzada si existe
            final_text = self.message_data['text']
            if self.message_data.get('embed_config') or self.message_data.get('attachment_image_url'):
                advanced_config = {}
                if self.message_data.get('embed_config'):
                    advanced_config['embed'] = self.message_data['embed_config']
                if self.message_data.get('attachment_image_url'):
                    advanced_config['attachment_image_url'] = self.message_data['attachment_image_url']
                
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
                cron_expression=None
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
                color=discord.Color.green()
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
            required=True
        )
        
        self.unit_select = TextInput(
            label=constants.LABEL_UNIT_INTERVAL,
            placeholder=constants.PLACEHOLDER_UNIT_SELECT,
            max_length=10,
            required=True
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


class TimeConfigView(View):
    """Vista para configurar hora (diario o semanal)"""
    
    def __init__(self, message_data: dict, schedule_type: str):
        super().__init__(timeout=300)
        self.message_data = message_data
        self.schedule_type = schedule_type
    
    @discord.ui.button(
        label=constants.BUTTON_CONFIGURE_TIME,
        style=discord.ButtonStyle.primary,
        emoji="🕐",
        custom_id="configure_time_button"
    )
    async def time_button(self, interaction: Interaction, button: discord.ui.Button):
        modal = TimeConfigModal(self.message_data, self.schedule_type)
        await interaction.response.send_modal(modal)


class TimeConfigModal(Modal):
    """Modal para configurar la hora"""
    
    def __init__(self, message_data: dict, schedule_type: str):
        super().__init__(title=constants.TITLE_TIME_CONFIG_MODAL)
        self.message_data = message_data
        self.schedule_type = schedule_type
        
        self.hour_input = TextInput(
            label=constants.INPUT_HOUR_LABEL,
            placeholder=constants.PLACEHOLDER_WEEKLY_HOUR if schedule_type == "weekly" else constants.PLACEHOLDER_DAILY_HOUR,
            max_length=2,
            required=True
        )
        
        self.minute_input = TextInput(
            label=constants.INPUT_MINUTE_LABEL,
            placeholder=constants.INPUT_MINUTE_PLACEHOLDER,
            max_length=2,
            required=True
        )
        
        self.add_item(self.hour_input)
        self.add_item(self.minute_input)
    
    async def on_submit(self, interaction: Interaction):
        try:
            hour = int(self.hour_input.value)
            minute = int(self.minute_input.value)
            
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError(constants.ERROR_HOUR_MINUTE_INVALID)
            
            self.message_data['hour'] = hour
            self.message_data['minute'] = minute
            
            if self.schedule_type == "daily":
                await self._create_daily_message(interaction)
            elif self.schedule_type == "weekly":
                # Mostrar selector de días
                view = WeekdaySelectionView(self.message_data)
                embed = discord.Embed(
                    title=constants.TITLE_SELECT_DAYS,
                    description=constants.DESC_TIME_CONFIGURED.format(hour=hour, minute=minute),
                    color=discord.Color.blue()
                )
                await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
        except ValueError:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=constants.TITLE_ERROR,
                    description=constants.ERROR_HOUR_MINUTE_INVALID,
                    color=discord.Color.red()
                ),
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=constants.TITLE_ERROR,  
                    description=constants.ERROR_UNEXPECTED.format(error=str(e)),
                    color=discord.Color.red()
                ),
                ephemeral=True
            )
    
    async def _create_daily_message(self, interaction: Interaction):
        """Crea un mensaje automático diario"""
        try:
            from uuid import uuid4
            from .models import AutomaticMessage
            import json
            
            # Validar que el mensaje tenga contenido útil
            is_valid, error_msg = validate_message_content(self.message_data)
            if not is_valid:
                await send_error_message(interaction, error_msg)
                return
            
            # Preparar el texto con configuración avanzada si existe
            final_text = self.message_data['text']
            if self.message_data.get('embed_config') or self.message_data.get('attachment_image_url'):
                advanced_config = {}
                if self.message_data.get('embed_config'):
                    advanced_config['embed'] = self.message_data['embed_config']
                if self.message_data.get('attachment_image_url'):
                    advanced_config['attachment_image_url'] = self.message_data['attachment_image_url']
                
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
                cron_expression=None
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
            embed = discord.Embed(
                title=f"{constants.EMOJI_SUCCESS} {constants.SUCCESS_MESSAGE_CREATED}",
                description=f"**{new_message.display_name}**\n\n"
                           f"📅 Se enviará todos los días a las {self.message_data['hour']:02d}:{self.message_data['minute']:02d}",
                color=discord.Color.green()
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)  
            
        except Exception as e:
            await send_error_message(interaction, f"Error creando el mensaje: {str(e)}")


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
        label=constants.BUTTON_CONFIRM_WEEKDAYS,
        style=discord.ButtonStyle.success,
        emoji="✅",
        custom_id="confirm_weekdays_button"
    )
    async def confirm_button(self, interaction: Interaction, button: discord.ui.Button):
        if not self.selected_weekdays:
            await send_error_message(
                interaction,
                constants.ERROR_SELECT_ONE_DAY
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
            from uuid import uuid4
            from .models import AutomaticMessage
            import json
            
            # Validar que el mensaje tenga contenido útil
            is_valid, error_msg = validate_message_content(self.message_data)
            if not is_valid:
                await send_error_message(interaction, error_msg)
                return
            
            # Preparar el texto con configuración avanzada si existe
            final_text = self.message_data['text']
            if self.message_data.get('embed_config') or self.message_data.get('attachment_image_url'):
                advanced_config = {}
                if self.message_data.get('embed_config'):
                    advanced_config['embed'] = self.message_data['embed_config']
                if self.message_data.get('attachment_image_url'):
                    advanced_config['attachment_image_url'] = self.message_data['attachment_image_url']
                
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
                cron_expression=None
            )
            
            # Guardar en la base de datos
            service = AutomaticMessagesService()
            success, error = service.add(new_message)
            
            if error or not success:
                await send_error_message(interaction, constants.ERROR_CREATING_MESSAGE)
                return
            
            # IMPORTANTE: Recargar el scheduler después de crear el mensaje
            reload_all_schedules()
            
            # Mostrar confirmación final
            weekday_names = [constants.WEEKDAY_TRANSLATIONS[day] for day in sorted(self.selected_weekdays)]
            days_text = ", ".join(weekday_names)
            
            embed = discord.Embed(
                title=f"{constants.EMOJI_SUCCESS} {constants.SUCCESS_MESSAGE_CREATED}",
                description=f"**{new_message.display_name}**\n\n"
                           f"📅 Días: {days_text}\n"
                           f"🕐 Hora: {self.message_data['hour']:02d}:{self.message_data['minute']:02d}",
                color=discord.Color.green()
            )
            
            await interaction.response.edit_message(embed=embed, view=None)
            
        except Exception as e:
            await send_error_message(interaction, f"Error creando el mensaje: {str(e)}")


class WeekdayMultiSelect(Select):
    """Multiselect para elegir días de la semana"""
    
    def __init__(self):
        options = [
            SelectOption(
                label=constants.WEEKDAY_MONDAY,
                value="0",
                emoji="📅"
            ),
            SelectOption(
                label=constants.WEEKDAY_TUESDAY, 
                value="1",
                emoji="📅"
            ),
            SelectOption(
                label=constants.WEEKDAY_WEDNESDAY,
                value="2", 
                emoji="📅"
            ),
            SelectOption(
                label=constants.WEEKDAY_THURSDAY,
                value="3",
                emoji="📅"
            ),
            SelectOption(
                label=constants.WEEKDAY_FRIDAY,
                value="4",
                emoji="📅"
            ),
            SelectOption(
                label=constants.WEEKDAY_SATURDAY,
                value="5",
                emoji="📅"
            ),
            SelectOption(
                label=constants.WEEKDAY_SUNDAY,
                value="6",
                emoji="📅"
            )
        ]
        
        super().__init__(
            placeholder=constants.DESC_WEEKDAY_SELECTION,
            options=options,
            min_values=1,
            max_values=7,
            custom_id="weekday_multiselect"
        )
    
    async def callback(self, interaction: Interaction):
        # Actualizar la selección en la vista padre
        view = self.view
        if isinstance(view, WeekdaySelectionView):
            view.selected_weekdays = {int(value) for value in self.values}
            
            # Crear mensaje de confirmación
            selected_days = [constants.WEEKDAY_TRANSLATIONS[int(day)] for day in self.values]
            days_text = ", ".join(selected_days)
            
            embed = discord.Embed(
                title=constants.TITLE_DAYS_SELECTED,
                description=constants.DESC_CONFIRM_DAYS.format(days=days_text),
                color=discord.Color.blue()
            )
            
            await interaction.response.edit_message(embed=embed, view=view)


class WeeklyConfigModal(Modal):
    """Modal para configurar programación semanal"""
    
    def __init__(self, message_data: dict):
        super().__init__(title=constants.TITLE_WEEKLY_CONFIG_MODAL)
        self.message_data = message_data
        
        self.hour_input = TextInput(
            label=constants.INPUT_HOUR_LABEL,
            placeholder=constants.PLACEHOLDER_HOUR_EXAMPLE,
            max_length=2,
            required=True
        )
        
        self.minute_input = TextInput(
            label=constants.INPUT_MINUTE_LABEL,
            placeholder=constants.INPUT_MINUTE_PLACEHOLDER,
            max_length=2,
            required=True
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
                title=constants.TITLE_SELECT_DAYS,
                description=f"Hora configurada: {hour:02d}:{minute:02d}\n\nAhora selecciona los días:",
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
        except ValueError:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=constants.TITLE_ERROR_EMOJI,
                    description=constants.ERROR_INVALID_TIME,
                    color=discord.Color.red()
                ),
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=constants.TITLE_ERROR_EMOJI,
                    description=f"Error inesperado: {str(e)}",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )


def validate_message_content(message_data: dict):
    """
    Valida que el mensaje tenga contenido útil (texto, embed o imagen)
    
    Args:
        message_data: Diccionario con los datos del mensaje
        
    Returns:
        Tupla (es_valido, mensaje_error)
    """
    text = message_data.get('text', '').strip()
    has_embed = bool(message_data.get('embed_config'))
    has_attachment_image = bool(message_data.get('attachment_image_url'))
    
    # Si no hay texto, debe haber al menos embed o imagen
    if not text and not has_embed and not has_attachment_image:
        return False, constants.ERROR_MESSAGE_NO_CONTENT
    
    # Si solo hay embed, debe tener título o descripción
    if not text and has_embed and not has_attachment_image:
        embed_config = message_data['embed_config']
        if not embed_config.get('title') and not embed_config.get('description'):
            return False, constants.ERROR_EMBED_NO_CONTENT
    
    return True, ""


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
            'schedule_type': schedule_type
        }
        
        # Determinar si es canal o categoría
        if isinstance(destination, discord.CategoryChannel):
            self.message_data['category_id'] = destination.id
            self.message_data['channel_id'] = None
        else:
            self.message_data['channel_id'] = destination.id
            self.message_data['category_id'] = None
    
    @discord.ui.button(
        label=constants.LABEL_ADD_TEXT,
        style=discord.ButtonStyle.secondary,
        emoji="📝",
        row=0
    )
    async def add_text_button(self, interaction: Interaction, button: discord.ui.Button):
        """Botón para añadir o editar texto del mensaje"""
        modal = MessageTextModal(self.message_data.get('text', ''))
        modal.callback_view = self
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(
        label=constants.LABEL_ADD_EMBED,
        style=discord.ButtonStyle.secondary,
        emoji="🎨",
        row=0
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
        row=0
    )
    async def add_image_button(self, interaction: Interaction, button: discord.ui.Button):
        """Botón para añadir imagen como attachment independiente"""
        modal = ImageBuilderModal(self.message_data.get('attachment_image_url', ''))
        modal.callback_view = self
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(
        label=constants.LABEL_COMPLETE,
        style=discord.ButtonStyle.success,
        emoji="✅",
        row=1
    )
    async def complete_button(self, interaction: Interaction, button: discord.ui.Button):
        """Botón para completar y programar el mensaje"""
        # Validar que hay contenido
        if not self.message_data.get('text') and not self.message_data.get('embed_config') and not self.message_data.get('attachment_image_url'):
            await send_error_message(interaction, constants.ERROR_NO_CONTENT_BEFORE_COMPLETE)
            return
        
        # Mostrar mensaje de configuración completada
        embed = discord.Embed(
            title=constants.TITLE_CONFIG_COMPLETED,
            description=constants.DESC_CONFIG_COMPLETED,
            color=discord.Color.green()
        )
        
        embed.add_field(
            name=constants.FIELD_NAME_SUMMARY,
            value=self._get_content_summary(),
            inline=False
        )
        
        # Pequeña pausa visual y luego continuar
        await interaction.response.edit_message(embed=embed, view=None)
        
        # Esperar un poco y luego mostrar la configuración de programación
        import asyncio
        await asyncio.sleep(1.5)
        
        # Continuar con la configuración de programación
        if self.schedule_type == "on_channel_create":
            # Para mensajes de creación de canal, crear directamente
            # Usar followup porque ya respondimos antes
            await self._create_channel_message_directly_followup(interaction)
        else:
            # Para otros tipos, mostrar configuración de programación
            view = ScheduleConfigView(self.message_data)
            
            embed = discord.Embed(
                title=constants.TITLE_CONFIG_PROGRAMMING,
                description=self._get_content_summary() + "\n\nAhora configura cuándo se debe enviar el mensaje:",
                color=discord.Color.blue()
            )
            
            await interaction.edit_original_response(embed=embed, view=view)
    
    @discord.ui.button(
        label=constants.LABEL_CANCEL,
        style=discord.ButtonStyle.danger,
        emoji="❌",
        row=1
    )
    async def cancel_button(self, interaction: Interaction, button: discord.ui.Button):
        """Botón para cancelar la configuración"""
        embed = discord.Embed(
            title=constants.TITLE_CONFIG_CANCELLED,
            description=constants.DESC_CONFIG_CANCELLED,
            color=discord.Color.red()
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
            color=discord.Color.blue()
        )
        
        # Información básica
        embed.add_field(
            name=constants.FIELD_NAME_BASIC_CONFIG,
            value=f"**📍 Destino:** {self.destination.mention}\n"
                  f"**⏰ Tipo:** {self._get_schedule_type_display()}\n"
                  f"**📝 Nombre:** {self.name or 'Sin nombre'}",
            inline=False
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
            name=constants.FIELD_NAME_CONTENT_STATUS,
            value="\n".join(content_status),
            inline=False
        )
        
        # Vista previa del contenido si existe
        if any([self.message_data.get('text'), self.message_data.get('embed_config'), self.message_data.get('attachment_image_url')]):
            embed.add_field(
                name=constants.FIELD_NAME_PREVIEW,
                value=self._get_content_summary(),
                inline=False
            )
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    def _get_schedule_type_display(self) -> str:
        """Convierte el tipo de programación a un formato amigable"""
        displays = {
            "interval": constants.SCHEDULE_INTERVAL_DISPLAY,
            "daily": constants.SCHEDULE_DAILY_DISPLAY, 
            "weekly": constants.SCHEDULE_WEEKLY_DISPLAY,
            "on_channel_create": constants.SCHEDULE_CHANNEL_CREATE_DISPLAY
        }
        return displays.get(self.schedule_type, self.schedule_type)
    
    async def _create_channel_message_directly_followup(self, interaction: Interaction):
        """Crea directamente un mensaje para creación de canal usando followup"""
        try:
            from uuid import uuid4
            from .models import AutomaticMessage
            import json
            
            # Generar ID único
            message_id = str(uuid4())
            
            # Preparar el texto con configuración avanzada si existe
            final_text = self.message_data.get('text', '')
            if self.message_data.get('embed_config') or self.message_data.get('attachment_image_url'):
                advanced_config = {}
                if self.message_data.get('embed_config'):
                    advanced_config['embed'] = self.message_data['embed_config']
                if self.message_data.get('attachment_image_url'):
                    advanced_config['attachment_image_url'] = self.message_data['attachment_image_url']
                
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
                cron_expression=None
            )
            
            # Guardar en la base de datos
            service = AutomaticMessagesService()
            success, error = service.add(new_message)
            
            if error or not success:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title=constants.TITLE_ERROR_EMOJI,
                        description=constants.ERROR_CREATING_MESSAGE,
                        color=discord.Color.red()
                    ),
                    ephemeral=True
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
                color=discord.Color.green()
            )
            
            await interaction.edit_original_response(embed=embed, view=None)
            
        except Exception as e:
            await interaction.followup.send(
                embed=discord.Embed(
                    title=constants.TITLE_ERROR_EMOJI,
                    description=f"Error creando el mensaje: {str(e)}",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )
    
    async def _create_channel_message_directly(self, interaction: Interaction):
        """Crea directamente un mensaje para creación de canal"""
        try:
            from uuid import uuid4
            from .models import AutomaticMessage
            import json
            
            # Generar ID único
            message_id = str(uuid4())
            
            # Preparar el texto con configuración avanzada si existe
            final_text = self.message_data.get('text', '')
            if self.message_data.get('embed_config') or self.message_data.get('attachment_image_url'):
                advanced_config = {}
                if self.message_data.get('embed_config'):
                    advanced_config['embed'] = self.message_data['embed_config']
                if self.message_data.get('attachment_image_url'):
                    advanced_config['attachment_image_url'] = self.message_data['attachment_image_url']
                
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
                cron_expression=None
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
                color=discord.Color.green()
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
            default=current_text
        )
        
        self.add_item(self.text_input)
    
    async def on_submit(self, interaction: Interaction):
        try:
            # Actualizar el texto en la vista principal
            if self.callback_view:
                self.callback_view.message_data['text'] = self.text_input.value.strip()
                await self.callback_view.update_embed(interaction)
            else:
                await interaction.response.send_message(constants.MESSAGE_TEXT_CONFIGURED, ephemeral=True)
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
            default=current_embed.get('title', '')
        )
        
        self.description_input = TextInput(
            label=constants.LABEL_EMBED_DESCRIPTION,
            placeholder=constants.PLACEHOLDER_EMBED_DESCRIPTION_MODAL,
            style=discord.TextStyle.paragraph,
            required=False,
            max_length=4000,
            default=current_embed.get('description', '')
        )
        
        self.color_input = TextInput(
            label=constants.LABEL_EMBED_COLOR,
            placeholder=constants.PLACEHOLDER_EMBED_COLOR_OPTIONS,
            required=False,
            max_length=20,
            default=current_embed.get('color', '')
        )
        
        self.embed_image_input = TextInput(
            label=constants.LABEL_EMBED_IMAGE_URL,
            placeholder=constants.PLACEHOLDER_EMBED_IMAGE,
            required=False,
            max_length=500,
            default=current_embed.get('image', '')
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
                'description': self.description_input.value.strip() if self.description_input.value else None,
                'color': self.color_input.value.strip() if self.color_input.value else 'blue',
                'image': self.embed_image_input.value.strip() if self.embed_image_input.value else None
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
                await interaction.response.send_message(constants.MESSAGE_EMBED_CONFIGURED, ephemeral=True)
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
            default=current_image
        )
        
        self.add_item(self.image_url_input)
    
    async def on_submit(self, interaction: Interaction):
        try:
            image_url = self.image_url_input.value.strip()
            
            # Actualizar la imagen en la vista principal
            if self.callback_view:
                self.callback_view.message_data['attachment_image_url'] = image_url if image_url else None
                await self.callback_view.update_embed(interaction)
            else:
                await interaction.response.send_message(constants.MESSAGE_IMAGE_CONFIGURED, ephemeral=True)
        except Exception as e:
            await send_error_message(interaction, f"Error: {str(e)}")
