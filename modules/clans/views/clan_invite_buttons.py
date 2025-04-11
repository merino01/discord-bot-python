"""
Vista para aceptar/rechazar invitación a clan
"""

from uuid import uuid4
from typing import Optional
from discord import ButtonStyle, Interaction, Message
from discord.ui import View, Button
from modules.clans.models import Clan
from modules.clans.service import ClanService

class ClanInviteView(View):
    """Vista para aceptar/rechazar invitación a clan"""

    def __init__(self, clan: Clan):
        super().__init__(timeout=60 * 60 * 24) # 24 horas
        self.clan = clan
        self.value = None
        self.invite_id = str(uuid4())
        self.message: Optional[Message]

        # Botón de aceptar
        accept_button = Button(
            style=ButtonStyle.success,
            label="Aceptar",
            custom_id=f"accept{self.invite_id}"
        )
        accept_button.callback = self.accept_callback
        self.add_item(accept_button)

        # Botón de rechazar
        reject_button = Button(
            style=ButtonStyle.danger,
            label="Rechazar",
            custom_id=f"reject{self.invite_id}"
        )
        reject_button.callback = self.reject_callback
        self.add_item(reject_button)

    async def accept_callback(self, interaction: Interaction):
        """Callback cuando se acepta la invitación"""
        self.value = True
        for item in self.children:
            if isinstance(item, Button):
                item.disabled = True

        # Añadir el usuario al clan
        error = await ClanService.add_member_to_clan(
            member_id=interaction.user.id,
            clan_id=self.clan.id
        )
        if error:
            await interaction.response.edit_message(
                content=f"Error al aceptar la invitación: {error}",
                view=None
            )
            return

        await interaction.response.edit_message(
            content=f"Te has unido al clan **{self.clan.name}**",
            view=self
        )
        self.stop()

    async def reject_callback(self, interaction: Interaction):
        """Callback cuando se rechaza la invitación"""
        self.value = False
        for item in self.children:
            if isinstance(item, Button):
                item.disabled = True
        await interaction.response.edit_message(
            content=f"Has rechazado la invitación al clan **{self.clan.name}**",
            view=self
        )
        self.stop()

    async def on_timeout(self) -> None:
        """Se ejecuta cuando pasa el tiempo límite"""
        if not self.message:
            return
        for item in self.children:
            if isinstance(item, Button):
                item.disabled = True
        await self.message.edit(
            content=f"La invitación al clan **{self.clan.name}** ha expirado",
            view=self
        )
