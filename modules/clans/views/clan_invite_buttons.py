from uuid import uuid4
from typing import Optional
from discord import ButtonStyle, Interaction, Message, Guild, Member
from discord.ui import View, Button
from constants import ONE_SECOND
from modules.clans.models import Clan
from modules.clans.service import ClanService


class ClanInviteView(View):
    def __init__(self, clan: Clan, guild: Guild, service: ClanService, channel_message: Optional[Message] = None):
        super().__init__(timeout=ONE_SECOND * 30)
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
        self.value = True
        for item in self.children:
            if isinstance(item, Button):
                item.disabled = True

        error = await self.service.add_member_to_clan(
            member_id=interaction.user.id, clan_id=self.clan.id
        )
        if error:
            return await interaction.response.edit_message(
                content=f"Error al aceptar la invitación: {error}", view=None
            )

        role = await self.guild.fetch_role(self.clan.role_id)
        member = await self.guild.fetch_member(interaction.user.id)
        if role is not None and member is not None:
            await member.add_roles(role, reason="Se ha unido al clan")
        if self.channel_message:
            await self.channel_message.edit(
                content=f"{interaction.user.mention} se ha unido al clan.", view=None, ephemeral=False
            )
        self.stop()

    async def reject_callback(self, interaction: Interaction):
        self.value = False
        for item in self.children:
            if isinstance(item, Button):
                item.disabled = True
        if self.channel_message:
            await self.channel_message.edit(
                content=f"{interaction.user.mention} ha rechazado la invitación al clan.",
                ephemeral=True,
                view=None,
            )
        self.stop()

    async def on_timeout(self) -> None:
        if self.message is None:
            return

        for item in self.children:
            if isinstance(item, Button):
                item.disabled = True

        await self.message.edit(
            content=f"La invitación al clan **{self.clan.name}** ha expirado", view=self
        )
