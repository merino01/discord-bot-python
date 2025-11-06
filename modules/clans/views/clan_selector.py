import discord
from discord import Interaction, Embed, Color
from typing import Optional
from modules.core import logger, send_paginated_embeds
from ..service import ClanService
from ..models import ClanMemberRole
from .. import constants


class ClanSelector(discord.ui.Select):
    def __init__(self, clans: list, action_type: str, **kwargs):
        self.clans = clans
        self.service = ClanService()
        self.action_type = action_type
        self.kwargs = kwargs

        # Crear opciones para el select (máximo 25)
        options = []
        for clan in clans[:25]:
            # Obtener información básica del clan
            member_count = len(clan.members) if clan.members else 0
            leaders = (
                [m for m in clan.members if m.role == ClanMemberRole.LEADER.value]
                if clan.members
                else []
            )
            leader_count = len(leaders)

            description = f"👑 {leader_count} líder{'es' if leader_count != 1 else ''} | 👥 {member_count} miembros"

            options.append(
                discord.SelectOption(
                    label=clan.name[:100],  # Discord limita a 100 caracteres
                    value=clan.id,
                    description=description[:100],  # Discord limita a 100 caracteres
                    emoji="🏰",
                )
            )

        super().__init__(
            placeholder="Selecciona un clan...", min_values=1, max_values=1, options=options
        )

    async def callback(self, interaction: Interaction):
        try:
            selected_clan_id = self.values[0]

            # Buscar el clan seleccionado
            selected_clan = None
            for clan in self.clans:
                if clan.id == selected_clan_id:
                    selected_clan = clan
                    break

            if not selected_clan:
                return await interaction.response.send_message(
                    "❌ Error: No se pudo encontrar el clan seleccionado.", ephemeral=True
                )

            # Ejecutar la acción según el tipo
            if self.action_type == "view_members":
                await self._handle_view_members(interaction, selected_clan)
            elif self.action_type == "info":
                # Mostrar embed de info de clan igual que el comando info
                embed = Embed(
                    title=constants.EMBED_CLAN_INFO_TITLE.format(clan_name=selected_clan.name),
                    description=constants.EMBED_CLAN_INFO_DESCRIPTION.format(
                        clan_name=selected_clan.name
                    ),
                    color=Color.blue(),
                    timestamp=discord.utils.utcnow(),
                )
                guild = interaction.guild
                embed.set_thumbnail(url=guild.icon.url if guild and guild.icon else None)
                embed.set_author(
                    name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url
                )
                embed.set_footer(
                    text=f"{guild.name}" if guild else "",
                    icon_url=guild.icon.url if guild and guild.icon else None,
                )
                embed.add_field(name=constants.FIELD_ID, value=selected_clan.id, inline=True)
                embed.add_field(name=constants.FIELD_NAME, value=selected_clan.name, inline=True)
                leaders = [
                    f"<@{member.user_id}>"
                    for member in selected_clan.members
                    if member.role == "leader"
                ]
                embed.add_field(
                    name=constants.FIELD_LEADERS,
                    value=", ".join(leaders) if leaders else "Ninguno",
                    inline=True,
                )
                embed.add_field(
                    name=constants.FIELD_MEMBERS, value=len(selected_clan.members), inline=True
                )
                embed.add_field(
                    name=constants.FIELD_MEMBER_LIMIT, value=selected_clan.max_members, inline=True
                )
                embed.add_field(
                    name=constants.FIELD_ROLE, value=f"<@&{selected_clan.role_id}>", inline=True
                )
                text_channels = [
                    f"<#{channel.channel_id}>"
                    for channel in selected_clan.channels
                    if channel.type == "text"
                ]
                voice_channels = [
                    f"<#{channel.channel_id}>"
                    for channel in selected_clan.channels
                    if channel.type == "voice"
                ]
                embed.add_field(
                    name=constants.FIELD_TEXT_CHANNELS,
                    value=f"{', '.join(text_channels) if text_channels else constants.VALUE_NONE} ({len(text_channels)}/{selected_clan.max_text_channels})",
                    inline=True,
                )
                embed.add_field(
                    name=constants.FIELD_VOICE_CHANNELS,
                    value=f"{', '.join(voice_channels) if voice_channels else constants.VALUE_NONE} ({len(voice_channels)}/{selected_clan.max_voice_channels})",
                    inline=True,
                )
                embed.add_field(
                    name=constants.FIELD_CREATION_DATE, value=selected_clan.created_at, inline=False
                )
                await interaction.response.send_message(
                    embed=embed, ephemeral=self.kwargs.get('ephemeral', True)
                )
            else:
                await interaction.response.send_message(
                    f"❌ Acción no reconocida: {self.action_type}", ephemeral=True
                )
        except Exception as e:
            logger.error(f"Error en callback del selector: {str(e)}")
            try:
                await interaction.response.send_message(
                    f"❌ Error interno: {str(e)}", ephemeral=True
                )
            except Exception:
                await interaction.followup.send(f"❌ Error interno: {str(e)}", ephemeral=True)

    async def _handle_view_members(self, interaction: Interaction, clan):
        """Manejar visualización de miembros del clan"""
        try:
            # Responder inmediatamente con mensaje de procesando
            await interaction.response.send_message(
                f"🔄 Procesando lista de miembros del clan **{clan.name}**...",
                ephemeral=self.kwargs.get('ephemeral', True),
            )

            if not clan.members:
                return await interaction.followup.send(
                    f"❌ El clan **{clan.name}** no tiene miembros.", ephemeral=True
                )

            # Separar líderes y miembros
            leaders = [m for m in clan.members if m.role == ClanMemberRole.LEADER.value]
            members = [m for m in clan.members if m.role == ClanMemberRole.MEMBER.value]

            # Crear listas simples de menciones
            leader_mentions = []
            member_mentions = []

            # Procesar líderes
            for leader in leaders:
                try:
                    user = await interaction.client.fetch_user(leader.user_id)
                    leader_mentions.append(f"� {user.mention}")
                except Exception:
                    leader_mentions.append(f"👑 <@{leader.user_id}>")

            # Procesar miembros
            for member in members:
                try:
                    user = await interaction.client.fetch_user(member.user_id)
                    member_mentions.append(f"� {user.mention}")
                except Exception:
                    member_mentions.append(f"👤 <@{member.user_id}>")

            # Crear embed principal
            embed = Embed(
                title=constants.EMBED_CLAN_MEMBERS_TITLE.format(clan_name=clan.name),
                color=Color.green(),
                description=constants.EMBED_CLAN_MEMBERS_DESCRIPTION.format(
                    member_count=len(clan.members)
                ),
            )

            # Dividir en chunks para evitar límites de Discord
            MAX_FIELD_LENGTH = 900

            # Añadir líderes si hay
            if leader_mentions:
                leaders_text = "\n".join(leader_mentions)
                if len(leaders_text) <= MAX_FIELD_LENGTH:
                    embed.add_field(name=constants.FIELD_LEADERS, value=leaders_text, inline=False)
                else:
                    # Si es muy largo, tomar solo los primeros
                    chunk_leaders = []
                    current_length = 0
                    for mention in leader_mentions:
                        if current_length + len(mention) + 1 > MAX_FIELD_LENGTH:
                            break
                        chunk_leaders.append(mention)
                        current_length += len(mention) + 1

                    embed.add_field(
                        name=f"{constants.FIELD_LEADERS} (Primeros {len(chunk_leaders)})",
                        value="\n".join(chunk_leaders),
                        inline=False,
                    )

            # Añadir miembros si hay
            if member_mentions:
                members_text = "\n".join(member_mentions)
                if len(members_text) <= MAX_FIELD_LENGTH:
                    embed.add_field(name=constants.FIELD_MEMBERS, value=members_text, inline=False)
                else:
                    # Si es muy largo, tomar solo los primeros
                    chunk_members = []
                    current_length = 0
                    for mention in member_mentions:
                        if current_length + len(mention) + 1 > MAX_FIELD_LENGTH:
                            break
                        chunk_members.append(mention)
                        current_length += len(mention) + 1

                    embed.add_field(
                        name=f"{constants.FIELD_MEMBERS} (Primeros {len(chunk_members)})",
                        value="\n".join(chunk_members),
                        inline=False,
                    )

            # Enviar el embed (editando el mensaje de procesando)
            await interaction.edit_original_response(
                content=None, embed=embed  # Limpiar el texto de procesando
            )

        except Exception as e:
            logger.error(f"Error en _handle_view_members: {str(e)}")
            try:
                await interaction.followup.send(
                    f"❌ Error al mostrar miembros: {str(e)}", ephemeral=True
                )
            except Exception:
                pass


class ClanSelectorView(discord.ui.View):
    def __init__(self, clans: list, action_type: str, **kwargs):
        super().__init__(timeout=300)
        self.clans = clans
        self.action_type = action_type
        self.kwargs = kwargs

        # Añadir el selector
        self.add_item(ClanSelector(clans, action_type, **kwargs))

    async def on_timeout(self):
        # Deshabilitar el selector cuando expire
        for item in self.children:
            item.disabled = True

        # Intentar editar el mensaje original
        try:
            if hasattr(self, 'message') and self.message:
                await self.message.edit(
                    content="⏰ **Tiempo agotado** - Selección de clan cancelada.",
                    view=self,
                    embed=None,
                )
        except Exception:
            pass
