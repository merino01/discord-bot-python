"""
Views para la selección interactiva de mensajes automáticos
"""

from discord import Interaction, Embed, Color, ButtonStyle
from discord.ui import View, Button
from typing import List, Callable
from .models import AutomaticMessage
from . import constants


class AutomaticMessageSelectView(View):
    """Vista para seleccionar mensajes automáticos con paginación"""
    
    def __init__(self, messages: List[AutomaticMessage], callback: Callable, page: int = 0, per_page: int = 20):
        super().__init__(timeout=300)
        self.messages = messages
        self.callback_func = callback
        self.page = page
        self.per_page = per_page
        self.total_pages = (len(messages) + per_page - 1) // per_page
        
        # Obtener los mensajes para la página actual
        start_idx = page * per_page
        end_idx = start_idx + per_page
        page_messages = messages[start_idx:end_idx]
        
        # Crear botones para cada mensaje de la página actual
        for message in page_messages:
            button = AutomaticMessageButton(message, self.callback_func)
            self.add_item(button)
        
        # Agregar botones de navegación si hay múltiples páginas
        if self.total_pages > 1:
            self.add_navigation_buttons()
    
    def add_navigation_buttons(self):
        """Agregar botones de navegación para paginación"""
        # Botón anterior
        if self.page > 0:
            prev_button = Button(
                label=constants.PAGE_PREVIOUS,
                style=ButtonStyle.secondary,
                emoji="⬅️"
            )
            prev_button.callback = self.previous_page
            self.add_item(prev_button)
        
        # Indicador de página
        page_button = Button(
            label=constants.PAGE_INDICATOR.format(current=self.page + 1, total=self.total_pages),
            style=ButtonStyle.secondary,
            disabled=True
        )
        self.add_item(page_button)
        
        # Botón siguiente
        if self.page < self.total_pages - 1:
            next_button = Button(
                label=constants.PAGE_NEXT,
                style=ButtonStyle.secondary,
                emoji="➡️"
            )
            next_button.callback = self.next_page
            self.add_item(next_button)
    
    async def previous_page(self, interaction: Interaction):
        """Ir a la página anterior"""
        if self.page > 0:
            new_view = AutomaticMessageSelectView(
                self.messages, 
                self.callback_func, 
                self.page - 1, 
                self.per_page
            )
            embed = create_message_selection_embed(self.messages, self.page - 1, self.per_page)
            await interaction.response.edit_message(embed=embed, view=new_view)
    
    async def next_page(self, interaction: Interaction):
        """Ir a la página siguiente"""
        if self.page < self.total_pages - 1:
            new_view = AutomaticMessageSelectView(
                self.messages, 
                self.callback_func, 
                self.page + 1, 
                self.per_page
            )
            embed = create_message_selection_embed(self.messages, self.page + 1, self.per_page)
            await interaction.response.edit_message(embed=embed, view=new_view)


class AutomaticMessageButton(Button):
    """Botón para seleccionar un mensaje automático específico"""
    
    def __init__(self, message: AutomaticMessage, callback: Callable):
        # Crear label usando el nombre si está disponible, sino usar ID truncado
        if message.name:
            label = f"🏷️ {message.name}"
        else:
            # Usar información del canal/categoría como fallback
            if message.channel_id:
                label = f"📢 {message.id[:8]}..."
            else:
                label = f"📁 {message.id[:8]}..."
        
        super().__init__(
            label=label[:80],  # Discord limita a 80 caracteres
            style=ButtonStyle.primary,
            custom_id=message.id
        )
        self.message = message
        self.callback_func = callback
    
    async def callback(self, interaction: Interaction):
        """Ejecutar el callback con el mensaje seleccionado"""
        await self.callback_func(interaction, self.message)


def create_message_selection_embed(messages: List[AutomaticMessage], page: int = 0, per_page: int = 20) -> Embed:
    """Crear embed para la selección de mensajes automáticos"""
    embed = Embed(
        title=constants.VIEW_SELECT_MESSAGE_TITLE,
        description=constants.VIEW_SELECT_MESSAGE_DESC,
        color=Color.blue()
    )
    
    # Agregar información de paginación si hay múltiples páginas
    total_pages = (len(messages) + per_page - 1) // per_page
    if total_pages > 1:
        embed.set_footer(text=constants.PAGE_INFO.format(
            current=page + 1,
            total=total_pages,
            showing=min(per_page, len(messages) - page * per_page),
            total_items=len(messages)
        ))
    
    return embed
