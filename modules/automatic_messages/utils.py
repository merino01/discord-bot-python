"""
Utilidades para el módulo de mensajes automáticos
"""

from typing import List, Optional
from discord import Interaction, Embed, Color, TextChannel
from .service import AutomaticMessagesService
from .models import AutomaticMessage
from .views import AutomaticMessageSelectView, create_message_selection_embed
from .tasks import stop_task_by_id
from . import constants


def process_message_text(text: str) -> str:
    """
    Procesa el texto del mensaje para interpretar caracteres de escape.
    
    Args:
        text: Texto original con posibles caracteres de escape
        
    Returns:
        Texto procesado con caracteres de escape interpretados
    """
    # Reemplazar las secuencias de escape más comunes
    return text.replace('\\n', '\n').replace('\\t', '\t')


async def show_message_selection_for_delete(interaction: Interaction):
    """Mostrar vista de selección para eliminar mensaje automático"""
    service = AutomaticMessagesService()
    messages, error = service.get_all()
    
    if error:
        await interaction.response.send_message(content=error, ephemeral=True)
        return
    
    if not messages:
        await interaction.response.send_message(
            constants.NO_MESSAGES_FOUND, 
            ephemeral=True
        )
        return
    
    # Crear vista de selección
    view = AutomaticMessageSelectView(messages, delete_message_callback)
    embed = create_message_selection_embed(messages)
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def delete_message_callback(interaction: Interaction, message: AutomaticMessage):
    """Callback para eliminar mensaje automático seleccionado"""
    service = AutomaticMessagesService()
    _, error = service.delete_by_id(message.id)
    
    if error:
        await interaction.response.edit_message(
            content=constants.ERROR_DELETING_MESSAGE.format(id=message.id), 
            embed=None, 
            view=None
        )
        return
    
    # Detener la tarea si existe
    stop_task_by_id(message.id)
    
    # Crear embed de confirmación
    embed = Embed(
        title=constants.CONFIRMATION_DELETE_TITLE,
        description=constants.CONFIRMATION_DELETE_DESC.format(id=message.id),
        color=Color.green()
    )
    
    await interaction.response.edit_message(embed=embed, view=None)


def get_messages_for_listing(service: AutomaticMessagesService, canal: Optional[TextChannel]):
    """Obtiene los mensajes automáticos según el filtro de canal."""
    if canal:
        return service.get_by_channel_id(canal.id)
    return service.get_all()


def create_message_embeds(automatic_messages: List[AutomaticMessage]) -> List[Embed]:
    """Crea los embeds para mostrar los mensajes automáticos."""
    if not automatic_messages:
        embed = Embed(title=constants.NO_MESSAGES_FOUND, color=Color.orange())
        return [embed]
    
    embeds = []
    for automatic_message in automatic_messages:
        embed = create_single_message_embed(automatic_message)
        embeds.append(embed)
    return embeds


def create_single_message_embed(automatic_message: AutomaticMessage) -> Embed:
    """Crea un embed individual para un mensaje automático."""
    # Usar el nombre si está disponible, sino usar el formato ID
    if automatic_message.name:
        title = constants.TITLE_MESSAGE_WITH_NAME.format(name=automatic_message.name)
    else:
        title = constants.TITLE_MESSAGE_ID.format(id=automatic_message.id)
    
    embed = Embed(title=title, color=Color.blue())
    
    # Mostrar el nombre como campo si existe
    if automatic_message.name:
        embed.add_field(name=constants.FIELD_NAME, value=automatic_message.name, inline=False)
    
    add_location_fields(embed, automatic_message)
    embed.add_field(name=constants.FIELD_MESSAGE, value=automatic_message.text, inline=False)
    
    if not automatic_message.is_category_based:
        add_timing_fields(embed, automatic_message)
    
    return embed


def add_location_fields(embed: Embed, automatic_message: AutomaticMessage):
    """Agrega los campos de ubicación (canal o categoría) al embed."""
    if automatic_message.is_category_based:
        embed.add_field(name=constants.FIELD_CATEGORY, value=f"<#{automatic_message.category_id}>", inline=False)
        embed.add_field(name=constants.FIELD_TYPE, value=constants.TYPE_CATEGORY, inline=False)
    else:
        embed.add_field(name=constants.FIELD_CHANNEL, value=f"<#{automatic_message.channel_id}>", inline=False)
        embed.add_field(name=constants.FIELD_TYPE, value=constants.TYPE_CHANNEL, inline=False)


def add_timing_fields(embed: Embed, automatic_message: AutomaticMessage):
    """Agrega los campos de temporización al embed."""
    if automatic_message.interval and automatic_message.interval_unit:
        _unit = automatic_message.interval_unit
        embed.add_field(
            name=constants.FIELD_INTERVAL,
            value=constants.INTERVAL_FORMAT.format(
                interval=automatic_message.interval, 
                unit=constants.TIME_TRANSLATIONS[_unit]
            ),
            inline=False,
        )
    elif automatic_message.hour is not None and automatic_message.minute is not None:
        embed.add_field(
            name=constants.FIELD_TIME,
            value=constants.TIME_FORMAT.format(
                hour=str(automatic_message.hour).zfill(2),
                minute=str(automatic_message.minute).zfill(2)
            ),
            inline=False,
        )