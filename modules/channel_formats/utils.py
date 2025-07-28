from re import compile as regex_compile, error as re_error
from typing import Optional
from discord import Message, TextChannel, Interaction, Embed, Color
from modules.core import logger
from .service import ChannelFormatsService
from .models import ChannelFormat
from .views import ChannelFormatSelectView, create_channel_format_selection_embed
from . import constants


async def check_channel_format(message: Message):
    service = ChannelFormatsService()
    channel_format, error = service.get_one_by_channel_id(message.channel.id)
    if error:
        logger.error(f"Error al obtener el formato de canal: {error}")
        return
    if channel_format is None:
        return

    try:
        regex = regex_compile(channel_format.regex)
        is_valid_format = regex.search(message.content)
        if is_valid_format:
            return
    except re_error as e:
        logger.error("Error en la expresión regular: %s", e)
        return

    if not isinstance(message.channel, TextChannel):
        logger.error("El canal no es de texto")
        return

    log_info = {
        "channel_id": message.channel.id,
        "channel_name": message.channel.name,
        "author_id": message.author.id,
        "author_name": message.author.name,
        "message_content": message.content,
    }
    logger.info("Formato de mensaje incorrecto")
    logger.info(log_info)
    await message.delete()


async def show_channel_format_selection_for_delete(interaction: Interaction):
    """Mostrar vista de selección para eliminar formato de canal"""
    service = ChannelFormatsService()
    channel_formats, error = service.get_all()
    
    if error:
        await interaction.response.send_message(content=error, ephemeral=True)
        return
    
    if not channel_formats:
        await interaction.response.send_message(
            constants.NO_FORMATS_FOUND, 
            ephemeral=True
        )
        return
    
    # Crear vista de selección
    view = ChannelFormatSelectView(channel_formats, delete_channel_format_callback)
    embed = create_channel_format_selection_embed(channel_formats)
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def delete_channel_format_callback(interaction: Interaction, channel_format: ChannelFormat):
    """Callback para eliminar formato de canal seleccionado"""
    service = ChannelFormatsService()
    _, error = service.delete(channel_format)
    
    if error:
        await interaction.response.edit_message(content=error, embed=None, view=None)
        return
    
    # Crear embed de confirmación
    embed = Embed(
        title=constants.CONFIRMATION_DELETE_TITLE,
        description=constants.CONFIRMATION_DELETE_DESC.format(id=channel_format.id),
        color=Color.green()
    )
    
    await interaction.response.edit_message(embed=embed, view=None)


async def show_channel_format_selection_for_edit(interaction: Interaction, canal: Optional[TextChannel], formato: Optional[str]):
    """Mostrar vista de selección para editar formato de canal"""
    service = ChannelFormatsService()
    channel_formats, error = service.get_all()
    
    if error:
        await interaction.response.send_message(content=error, ephemeral=True)
        return
    
    if not channel_formats:
        await interaction.response.send_message(
            constants.NO_FORMATS_FOUND, 
            ephemeral=True
        )
        return
    
    # Crear callback parcial con los parámetros de edición
    def edit_callback(interaction_inner: Interaction, channel_format: ChannelFormat):
        return edit_channel_format_callback(interaction_inner, channel_format, canal, formato)
    
    # Crear vista de selección
    view = ChannelFormatSelectView(channel_formats, edit_callback)
    embed = create_channel_format_selection_embed(channel_formats)
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def edit_channel_format_callback(interaction: Interaction, channel_format: ChannelFormat, canal: Optional[TextChannel], formato: Optional[str]):
    """Callback para editar formato de canal seleccionado"""
    result = edit_channel_format_by_id(channel_format.id, canal, formato)
    
    if result['success']:
        # Crear embed de confirmación
        embed = Embed(
            title=constants.CONFIRMATION_EDIT_TITLE,
            description=constants.CONFIRMATION_EDIT_DESC.format(id=channel_format.id),
            color=Color.green()
        )
        await interaction.response.edit_message(embed=embed, view=None)
    else:
        await interaction.response.edit_message(content=result['error'], embed=None, view=None)


def edit_channel_format_by_id(format_id: str, canal: Optional[TextChannel], formato: Optional[str]) -> dict:
    """Editar formato de canal por ID - función auxiliar reutilizable"""
    return _edit_channel_format_internal(format_id, canal, formato)


def _edit_channel_format_internal(format_id: str, canal: Optional[TextChannel], formato: Optional[str]) -> dict:
    """Lógica interna para editar formato de canal"""
    service = ChannelFormatsService()
    
    # Validar regex si se proporciona
    if formato:
        try:
            regex_compile(formato)
        except re_error:
            return {
                'success': False, 
                'error': constants.ERROR_INVALID_REGEX
            }
    
    # Obtener formato existente
    channel_format, error = service.get_by_id(format_id)
    if error:
        return {'success': False, 'error': error}
    
    if not channel_format:
        return {
            'success': False, 
            'error': constants.ERROR_FORMAT_NOT_FOUND.format(id=format_id)
        }
    
    # Aplicar cambios
    if canal:
        channel_format.channel_id = canal.id
    if formato:
        channel_format.regex = formato
    
    # Actualizar en base de datos
    error = service.update(channel_format)
    if error:
        return {'success': False, 'error': error}
    
    return {'success': True, 'error': None}
