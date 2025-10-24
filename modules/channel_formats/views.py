"""
Views para la selección interactiva de formatos de canal
"""

import discord
from discord import Interaction, Embed, Color
from typing import List, Callable, Any
from .models import ChannelFormat
from translator import __


class ChannelFormatSelectView(discord.ui.View):
    """Vista para seleccionar formatos de canal con paginación"""
    
    def __init__(self, channel_formats: List[ChannelFormat], callback: Callable, page: int = 0, per_page: int = 20):
        super().__init__(timeout=300)
        self.channel_formats = channel_formats
        self.callback_func = callback
        self.page = page
        self.per_page = per_page
        self.total_pages = (len(channel_formats) + per_page - 1) // per_page
        
        # Obtener los formatos para la página actual
        start_idx = page * per_page
        end_idx = start_idx + per_page
        page_formats = channel_formats[start_idx:end_idx]
        
        # Crear botones para cada formato de la página actual
        for channel_format in page_formats:
            button = ChannelFormatButton(channel_format, self.callback_func)
            self.add_item(button)
        
        # Agregar botones de navegación si hay múltiples páginas
        if self.total_pages > 1:
            self.add_navigation_buttons()
    
    def add_navigation_buttons(self):
        """Agregar botones de navegación para paginación"""
        # Botón anterior
        if self.page > 0:
            prev_button = discord.ui.Button(
                label=constants.PAGE_PREVIOUS,
                style=discord.ButtonStyle.secondary,
                emoji="⬅️"
            )
            prev_button.callback = self.previous_page
            self.add_item(prev_button)
        
        # Indicador de página
        page_button = discord.ui.Button(
            label=constants.PAGE_INDICATOR.format(current=self.page + 1, total=self.total_pages),
            style=discord.ButtonStyle.secondary,
            disabled=True
        )
        self.add_item(page_button)
        
        # Botón siguiente
        if self.page < self.total_pages - 1:
            next_button = discord.ui.Button(
                label=constants.PAGE_NEXT,
                style=discord.ButtonStyle.secondary,
                emoji="➡️"
            )
            next_button.callback = self.next_page
            self.add_item(next_button)
    
    async def previous_page(self, interaction: Interaction):
        """Ir a la página anterior"""
        if self.page > 0:
            new_view = ChannelFormatSelectView(
                self.channel_formats, 
                self.callback_func, 
                self.page - 1, 
                self.per_page
            )
            embed = create_channel_format_selection_embed(self.channel_formats, self.page - 1, self.per_page)
            await interaction.response.edit_message(embed=embed, view=new_view)
    
    async def next_page(self, interaction: Interaction):
        """Ir a la página siguiente"""
        if self.page < self.total_pages - 1:
            new_view = ChannelFormatSelectView(
                self.channel_formats, 
                self.callback_func, 
                self.page + 1, 
                self.per_page
            )
            embed = create_channel_format_selection_embed(self.channel_formats, self.page + 1, self.per_page)
            await interaction.response.edit_message(embed=embed, view=new_view)


class ChannelFormatButton(discord.ui.Button):
    """Botón para seleccionar un formato de canal específico"""
    
    def __init__(self, channel_format: ChannelFormat, callback: Callable):
        # Obtener el nombre del canal o usar ID si no está disponible
        channel_name = f"<#{channel_format.channel_id}>"
        label = f"{channel_format.id[:8]}... | {channel_name}"
        
        super().__init__(
            label=label,
            style=discord.ButtonStyle.primary,
            custom_id=channel_format.id
        )
        self.channel_format = channel_format
        self.callback_func = callback
    
    async def callback(self, interaction: Interaction):
        """Ejecutar el callback con el formato seleccionado"""
        await self.callback_func(interaction, self.channel_format)


def create_channel_format_selection_embed(channel_formats: List[ChannelFormat], page: int = 0, per_page: int = 20) -> Embed:
    """Crear embed para la selección de formatos de canal"""
    embed = Embed(
        title=constants.VIEW_SELECT_FORMAT_TITLE,
        description=constants.VIEW_SELECT_FORMAT_DESC,
        color=Color.blue()
    )
    
    # Agregar información de paginación si hay múltiples páginas
    total_pages = (len(channel_formats) + per_page - 1) // per_page
    if total_pages > 1:
        embed.set_footer(text=constants.PAGE_INFO.format(
            current=page + 1,
            total=total_pages,
            showing=min(per_page, len(channel_formats) - page * per_page),
            total_items=len(channel_formats)
        ))
    
    return embed
