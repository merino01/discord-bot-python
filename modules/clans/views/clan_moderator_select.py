from typing import List, Callable, Any, Optional
from discord import Interaction, Embed, Color, ButtonStyle
from discord.ui import View, Button
from ..models import FullClan
from modules.core import logger


class ClanModeratorSelectView(View):
    """View para que los moderadores seleccionen un clan para ejecutar acciones"""

    def __init__(
        self, clans: List[FullClan], action_name: str, callback_func: Callable, *args, **kwargs
    ):
        super().__init__(timeout=300)
        self.clans = clans
        self.action_name = action_name
        self.callback_func = callback_func
        self.callback_args = args
        self.callback_kwargs = kwargs
        self.message = None

        # Añadir botones para cada clan (máximo 25 botones por View)
        for i, clan in enumerate(clans[:25]):
            button_obj = Button(
                label=f"{clan.name}",
                custom_id=f"clan_{clan.id}",
                style=ButtonStyle.primary,
                row=i // 5,  # Distribuir en filas de 5
            )
            button_obj.callback = self._make_callback(clan)
            self.add_item(button_obj)

    def _make_callback(self, clan: FullClan):
        async def callback(interaction: Interaction):
            try:
                await interaction.response.defer(ephemeral=True)

                # Deshabilitar todos los botones
                for item in self.children:
                    item.disabled = True

                # Actualizar el mensaje original
                embed = Embed(
                    title="✅ Clan seleccionado",
                    description=f"Has seleccionado el clan **{clan.name}** para {self.action_name}",
                    color=Color.green(),
                )

                if self.message:
                    await self.message.edit(embed=embed, view=self)

                # Ejecutar la función callback con el clan seleccionado
                await self.callback_func(
                    interaction, clan, *self.callback_args, **self.callback_kwargs
                )

            except Exception as e:
                logger.error(f"Error en callback de selección de clan: {str(e)}")
                await interaction.followup.send(
                    f"Error al procesar la selección: {str(e)}", ephemeral=True
                )

        return callback

    async def on_timeout(self):
        # Deshabilitar todos los botones cuando expire el timeout
        for item in self.children:
            item.disabled = True

        if self.message:
            try:
                embed = Embed(
                    title="⏰ Selección expirada",
                    description="El tiempo para seleccionar un clan ha expirado.",
                    color=Color.orange(),
                )
                await self.message.edit(embed=embed, view=self)
            except Exception:
                pass  # El mensaje pudo haber sido eliminado
