"""
Views para la selección interactiva de triggers
"""

from typing import List, Callable, Any
from discord import Interaction, ui, ButtonStyle, Embed, Color
from .models import Trigger
from i18n import __


class TriggerSelectView(ui.View):
    """Vista con botones para seleccionar un trigger con paginación"""
    
    def __init__(self, triggers: List[Trigger], callback_func: Callable[[Interaction, str], Any], base_title: str, timeout: float = 180):
        super().__init__(timeout=timeout)
        self.triggers = triggers
        self.callback_func = callback_func
        self.base_title = base_title
        self.current_page = 0
        self.triggers_per_page = 20  # 20 triggers por página (4 filas de 5)
        self.max_pages = (len(triggers) - 1) // self.triggers_per_page + 1
        
        self._update_buttons()
    
    def _update_buttons(self):
        """Actualizar los botones mostrados según la página actual"""
        # Limpiar botones existentes
        self.clear_items()
        
        # Calcular el rango de triggers para la página actual
        start_idx = self.current_page * self.triggers_per_page
        end_idx = min(start_idx + self.triggers_per_page, len(self.triggers))
        page_triggers = self.triggers[start_idx:end_idx]
        
        # Añadir botones para los triggers de la página actual
        for i, trigger in enumerate(page_triggers):
            button = TriggerButton(
                trigger=trigger,
                callback_func=self.callback_func,
                row=i // 5  # 5 botones por fila
            )
            self.add_item(button)
        
        # Añadir botones de navegación si hay múltiples páginas
        if self.max_pages > 1:
            # Botón "Anterior" 
            if self.current_page > 0:
                prev_button = ui.Button(
                    label=__("triggers.views.buttonPrevious"),
                    style=ButtonStyle.primary,
                    row=4
                )
                prev_button.callback = self._prev_page
                self.add_item(prev_button)
            
            # Indicador de página
            page_indicator = ui.Button(
                label=__("triggers.pagination.indicator", 
                    current=self.current_page + 1,
                    total=self.max_pages
                ),
                style=ButtonStyle.secondary,
                disabled=True,
                row=4
            )
            self.add_item(page_indicator)
            
            # Botón "Siguiente"
            if self.current_page < self.max_pages - 1:
                next_button = ui.Button(
                    label=__("triggers.views.buttonNext"),
                    style=ButtonStyle.primary,
                    row=4
                )
                next_button.callback = self._next_page
                self.add_item(next_button)
    
    async def _prev_page(self, interaction: Interaction):
        """Ir a la página anterior"""
        if self.current_page > 0:
            self.current_page -= 1
            self._update_buttons()
            
            # Actualizar embed para la nueva página
            title = __("triggers.views.pageTitle", 
                action=self.base_title,
                current=self.current_page + 1,
                total=self.max_pages
            )
            embed = create_trigger_selection_embed(
                self.triggers, 
                title,
                self.current_page,
                self.triggers_per_page
            )
            
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()
    
    async def _next_page(self, interaction: Interaction):
        """Ir a la página siguiente"""
        if self.current_page < self.max_pages - 1:
            self.current_page += 1
            self._update_buttons()
            
            # Actualizar embed para la nueva página
            title = __("triggers.views.pageTitle", 
                action=self.base_title,
                current=self.current_page + 1,
                total=self.max_pages
            )
            embed = create_trigger_selection_embed(
                self.triggers, 
                title,
                self.current_page,
                self.triggers_per_page
            )
            
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()
    
    async def on_timeout(self) -> None:
        # Deshabilitar todos los botones cuando expire
        for item in self.children:
            item.disabled = True


class TriggerButton(ui.Button):
    """Botón individual para un trigger"""
    
    def __init__(self, trigger: Trigger, callback_func: Callable[[Interaction, str], Any], row: int):
        # Crear etiqueta del botón con información más útil del trigger
        # Formato: "palabra_clave (canal) #ID"
        key_display = trigger.key[:15] + "..." if len(trigger.key) > 15 else trigger.key
        label = f"{key_display} #{trigger.id[:6]}"
        
        super().__init__(
            label=label,
            style=ButtonStyle.secondary,
            row=row
        )
        
        self.trigger = trigger
        self.callback_func = callback_func
    
    async def callback(self, interaction: Interaction) -> None:
        # Llamar al callback con el ID del trigger seleccionado
        await self.callback_func(interaction, self.trigger.id)


def create_trigger_selection_embed(
    triggers: List[Trigger], 
    title: str, 
    current_page: int = 0, 
    triggers_per_page: int = 20
) -> Embed:
    """Crear embed para mostrar la lista de triggers disponibles con paginación"""
    embed = Embed(
        title=title,
        description=__("triggers.views.selectionDescription"),
        color=Color.blue()
    )
    
    # Información de paginación
    total_triggers = len(triggers)
    max_pages = (total_triggers - 1) // triggers_per_page + 1 if total_triggers > 0 else 1
    
    # Calcular el rango de triggers para la página actual
    start_idx = current_page * triggers_per_page
    end_idx = min(start_idx + triggers_per_page, len(triggers))
    triggers_in_page = end_idx - start_idx
    
    embed.add_field(
        name=__("triggers.views.summaryTitle"),
        value=__("triggers.views.summaryText", 
            total=total_triggers,
            in_page=triggers_in_page
        ),
        inline=True
    )
    
    if max_pages > 1:
        embed.add_field(
            name=__("triggers.views.paginationTitle"),
            value=__("triggers.pagination.info", 
                current=current_page + 1,
                total=max_pages,
                count=total_triggers
            ),
            inline=True
        )
    
    embed.add_field(
        name=__("triggers.views.instructionsTitle"),
        value=__("triggers.views.instructionsText"),
        inline=False
    )
    
    return embed
