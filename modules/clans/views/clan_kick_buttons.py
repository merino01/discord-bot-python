"""
Vista para aceptar/rechazar kick de un clan
"""

from uuid import uuid4
from typing import Optional
from discord import ButtonStyle, Interaction, Message, Member
from discord.ui import View, Button
from modules.clans.models import Clan
from modules.clans.service import ClanService
from modules.clans.utils import logica_expulsar_del_clan


class ClanKickView(View):
    """Vista para aceptar/rechazar solicitud de expulsar de clan"""

    def __init__(self, clan: Clan, member_to_send: Member, service: ClanService):
        super().__init__(timeout=60 * 60 * 24)  # 24 horas
        self.clan = clan
        self.value = None
        self.invite_id = str(uuid4())
        self.message: Optional[Message]
        self.member_to_send = member_to_send
        self.service = service

        # Botón de aceptar
        accept_button = Button(
            style=ButtonStyle.success, label="Aceptar", custom_id=f"accept{self.invite_id}"
        )
        accept_button.callback = self.accept_callback
        self.add_item(accept_button)

        # Botón de rechazar
        reject_button = Button(
            style=ButtonStyle.danger, label="Rechazar", custom_id=f"reject{self.invite_id}"
        )
        reject_button.callback = self.reject_callback
        self.add_item(reject_button)

    async def accept_callback(self, interaction: Interaction):
        """Callback cuando se acepta la solicitud de expulsión"""
        self.value = True
        for item in self.children:
            if isinstance(item, Button):
                item.disabled = True

        # Expulsar a miembro del clan usando la lógica completa
        error = await logica_expulsar_del_clan(
            id_usuario=self.member_to_send.id, id_clan=self.clan.id, guild=interaction.guild
        )
        if error:
            await interaction.response.edit_message(
                content=f"Error al aceptar la solicitud: {error}", view=None
            )
            return

        await interaction.response.edit_message(
            content=f"Has expulsado a **{self.member_to_send.name}** del clan **{self.clan.name}**",
            view=None,
        )
        self.stop()

    async def reject_callback(self, interaction: Interaction):
        """Callback cuando se rechaza la invitación"""
        self.value = False
        for item in self.children:
            if isinstance(item, Button):
                item.disabled = True
        await interaction.response.edit_message(
            content=f"Has rechazado la solicitud de expulsión de **{self.member_to_send.name}** del clan **{self.clan.name}**",
            view=self,
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
            content=f"La invitación al clan **{self.clan.name}** ha expirado", view=self
        )
