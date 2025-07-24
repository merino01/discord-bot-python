"""
Vista para seleccionar de qué clan salir cuando el usuario está en múltiples clanes
"""

from typing import List, Optional
from discord import ButtonStyle, Interaction, Member, Message
from discord.ui import View, Button
from modules.core import logger
from modules.clans.models import FullClan
from modules.clans.service import ClanService
from modules.clans.utils import logica_salir_del_clan
from constants import ONE_SECOND


class ClanLeaveView(View):
    def __init__(self, clans: List[FullClan], user: Member, service: ClanService):
        super().__init__(timeout=ONE_SECOND * 30)
        self.clans = clans
        self.selected_clan: Optional[FullClan] = None
        self.user = user
        self.message: Optional[Message] = None
        self.service = service

        for clan in clans:
            button = Button(label=clan.name, custom_id=str(clan.id), style=ButtonStyle.danger)
            button.callback = self.leave_clan_callback
            self.add_item(button)

    async def leave_clan_callback(self, interaction: Interaction):
        if not interaction.data or not (clan_id := interaction.data.get("custom_id")):
            return
        
        self.selected_clan = next((clan for clan in self.clans if clan.id == clan_id), None)
        if not self.selected_clan:
            await interaction.response.send_message("Clan no encontrado", ephemeral=True)
            return

        try:
            error = await logica_salir_del_clan(
                self.user.id, 
                self.selected_clan.id, 
                interaction.guild
            )
            
            if error:
                await interaction.response.edit_message(
                    content=f"Error al salir del clan: {error}", view=None
                )
                return

            self.stop()
            await interaction.response.edit_message(
                content=f"Has salido del clan **{self.selected_clan.name}** exitosamente.",
                view=None
            )

        except Exception as e:
            logger.error(f"Error al salir del clan: {e}")
            await interaction.response.edit_message(
                content="Error al procesar la solicitud. Inténtalo de nuevo.",
                view=None
            )

    async def on_timeout(self) -> None:
        if not self.message:
            return

        for item in self.children:
            if isinstance(item, Button):
                item.disabled = True
        await self.message.edit(content="Se acabó el tiempo para seleccionar un clan", view=self)
