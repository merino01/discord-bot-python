"""clan select buttons view"""

from typing import List, Optional
from discord import ButtonStyle, Interaction, Member, Message
from discord.ui import View, Button
from modules.core import logger
from modules.clans.models import Clan
from constants import ONE_SECOND
from .clan_invite_buttons import ClanInviteView
from .clan_kick_buttons import ClanKickView
from ..service import ClanService


class ClanSelectView(View):
    def __init__(
        self, clans: List[Clan], member: Member, service: ClanService, interaction: Interaction
    ):
        super().__init__(timeout=ONE_SECOND * 30)
        self.clans = clans
        self.selected_clan: Optional[Clan] = None
        self.member_to_send = member
        self.message: Optional[Message] = None
        self.service = service
        self.interaction = interaction

        for clan in clans:
            button = Button(label=clan.name, custom_id=str(clan.id), style=ButtonStyle.primary)
            button.callback = self.send_invite_to_user
            self.add_item(button)

    async def send_invite_to_user(self, interaction: Interaction):
        if not interaction.data or not (clan_id := interaction.data.get("custom_id")):
            return
        self.selected_clan = next((clan for clan in self.clans if clan.id == clan_id), None)
        if not self.selected_clan:
            return await interaction.response.send_message("Clan no encontrado", ephemeral=True)
        try:
            view = ClanInviteView(self.selected_clan, interaction.guild, self.service, None)
            invite_message = await self.member_to_send.send(
                content=f"Te han invitado al clan **{self.selected_clan.name}**", view=view
            )
            view.message = invite_message

            self.stop()
            await interaction.response.edit_message(
                content=f"Se le ha enviado la invitación al clan a **{self.member_to_send.name}**",
                view=None,
            )

            # Esperar respuesta
            await view.wait()

            if view.value is True:
                await interaction.followup.send(
                    f"**{self.member_to_send.name}** ha aceptado la invitación", ephemeral=True
                )
            elif view.value is False:
                await interaction.followup.send(
                    f"**{self.member_to_send.name}** ha rechazado la invitación", ephemeral=True
                )
        except Exception as e:
            logger.error(f"Error al enviar el mensaje: {e}")
            await interaction.response.send_message(
                "Error al enviar el mensaje al usuario. \
                Asegúrate de que tenga los mensajes directos habilitados.",
                ephemeral=True,
            )
            return

    async def send_kick_request_to_leader(self, interaction: Interaction):
        """Callback cuando se presiona un botón"""
        if not interaction.data or not (clan_id := interaction.data.get("custom_id")):
            return
        self.selected_clan = next((clan for clan in self.clans if clan.id == clan_id), None)
        if not self.selected_clan:
            await interaction.response.send_message("Clan no encontrado", ephemeral=True)
            return
        try:
            view = ClanKickView(self.selected_clan, self.member_to_send, self.service)
            kick_message = await self.interaction.user.send(
                content=f"Has solicitado la expulsión del clan **{self.selected_clan.name}** al miembro **{self.member_to_send.name}** ¿Deseas continuar?",
                view=view,
            )
            self.message = kick_message

            self.stop()
            await interaction.response.edit_message(
                content=f"Se le ha enviado la solicitud de expulsión del clan a **{interaction.user.name}**",
                view=None,
            )

            # Esperar respuesta
            await view.wait()

            if view.value is True:
                await interaction.followup.send(
                    f"Se ha expulsado del clan **{self.selected_clan.name}** a **{self.member_to_send.name}**.",
                    ephemeral=True,
                )
            elif view.value is False:
                await interaction.followup.send(
                    f"**{interaction.user.name}** ha rechazado la solicitud de expulsión del clan.",
                    ephemeral=True,
                )
        except Exception as e:
            logger.error(f"Error al enviar el mensaje: {e}")
            await interaction.response.send_message(
                "Error al enviar el mensaje al usuario. \
                Asegúrate de que tenga los mensajes directos habilitados.",
                ephemeral=True,
            )
            return

    async def on_timeout(self) -> None:
        if not self.message:
            return

        for item in self.children:
            if isinstance(item, Button):
                item.disabled = True
        await self.message.edit(content="Se acabó el tiempo para seleccionar un clan", view=self)
