from uuid import uuid4
from typing import Optional
from discord import ButtonStyle, Interaction, Message, Guild, Member
from discord.ui import View, Button
from constants import ONE_DAY
from i18n import __
from modules.clans.models import Clan
from modules.clans.service import ClanService
from modules.clans.utils import add_member_to_clan


class ClanInviteView(View):
    def __init__(self, clan: Clan, guild: Guild, service: ClanService, channel_message: Optional[Message] = None):
        super().__init__(timeout=ONE_DAY)
        self.clan = clan
        self.value = None
        self.invite_id = str(uuid4())
        self.message: Optional[Message] = None
        self.guild = guild
        self.channel_message = channel_message
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
        """Callback cuando se acepta la invitación"""
        self.value = True
        for item in self.children:
            if isinstance(item, Button):
                item.disabled = True

        # Usar la función de utils que maneja roles adicionales
        error = await add_member_to_clan(
            guild=self.guild, 
            member_id=interaction.user.id, 
            clan_id=self.clan.id
        )
        
        if error:
            await interaction.response.edit_message(
                content=__("clans.messages.kickedFromClan", error=error), view=self
            )
            return

        # Responder la interacción con éxito
        await interaction.response.edit_message(
            content=__("clans.messages.acceptedInvitation", clan_name=self.clan.name), view=self
        )
        
        # Actualizar el mensaje del canal si existe
        if self.channel_message:
            try:
                await self.channel_message.edit(
                    content=__("clans.messages.joinedClanNotification", user=interaction.user.mention, clan_name=self.clan.name)
                )
            except:
                pass  # Si no se puede editar, continuar
                
        self.stop()

    async def reject_callback(self, interaction: Interaction):
        """Callback cuando se rechaza la invitación"""
        self.value = False
        for item in self.children:
            if isinstance(item, Button):
                item.disabled = True
                
        # Responder la interacción
        await interaction.response.edit_message(
            content=__("clans.messages.rejectedInvitation", clan_name=self.clan.name), view=self
        )
        
        # Actualizar el mensaje del canal si existe
        if self.channel_message:
            try:
                await self.channel_message.edit(
                    content=__("clans.messages.rejectedInvitationNotification", user=interaction.user.mention, clan_name=self.clan.name)
                )
            except Exception:
                pass  # Si no se puede editar, continuar
                
        self.stop()

    async def on_timeout(self) -> None:
        if self.message is None:
            return

        for item in self.children:
            if isinstance(item, Button):
                item.disabled = True

        await self.message.edit(
            content=__("clans.messages.invitationExpired", clan_name=self.clan.name), view=self
        )
