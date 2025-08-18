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
            leaders = [m for m in clan.members if m.role == ClanMemberRole.LEADER.value] if clan.members else []
            leader_count = len(leaders)
            
            description = f"👑 {leader_count} líder{'es' if leader_count != 1 else ''} | 👥 {member_count} miembros"
            
            options.append(discord.SelectOption(
                label=clan.name[:100],  # Discord limita a 100 caracteres
                value=clan.id,
                description=description[:100],  # Discord limita a 100 caracteres
                emoji="🏰"
            ))
        
        super().__init__(
            placeholder="Selecciona un clan...",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: Interaction):
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
    
    async def _handle_view_members(self, interaction: Interaction, clan):
        """Manejar visualización de miembros del clan"""
        await interaction.response.defer(ephemeral=self.kwargs.get('ephemeral', True))
        
        if not clan.members:
            return await interaction.followup.send(
                f"❌ El clan **{clan.name}** no tiene miembros.", ephemeral=True
            )

        # Separar líderes y miembros
        leaders = [m for m in clan.members if m.role == ClanMemberRole.LEADER.value]
        members = [m for m in clan.members if m.role == ClanMemberRole.MEMBER.value]

        # Preparar listas con un máximo de elementos por embed
        MAX_MEMBERS_PER_PAGE = 15  # Límite conservador para evitar problemas

        async def create_member_pages(member_list, role_type):
            pages = []
            for i in range(0, len(member_list), MAX_MEMBERS_PER_PAGE):
                chunk = member_list[i:i + MAX_MEMBERS_PER_PAGE]
                member_strings = []
                
                for member in chunk:
                    try:
                        user = await interaction.client.fetch_user(member.user_id)
                        if user:
                            if role_type == "leader":
                                member_strings.append(f"👑 {user.mention}")
                            else:
                                member_strings.append(f"👤 {user.mention}")
                        else:
                            # Si no podemos obtener el usuario, usar solo la mención
                            if role_type == "leader":
                                member_strings.append(f"👑 <@{member.user_id}>")
                            else:
                                member_strings.append(f"👤 <@{member.user_id}>")
                    except Exception:
                        # En caso de error, usar solo la mención
                        if role_type == "leader":
                            member_strings.append(f"👑 <@{member.user_id}>")
                        else:
                            member_strings.append(f"👤 <@{member.user_id}>")
                
                pages.append(member_strings)
            return pages

        # Crear páginas
        leader_pages = await create_member_pages(leaders, "leader") if leaders else []
        member_pages = await create_member_pages(members, "member") if members else []

        # Si todo cabe en una página, usar un solo embed
        if len(leaders) <= MAX_MEMBERS_PER_PAGE and len(members) <= MAX_MEMBERS_PER_PAGE:
            embed = Embed(
                title=constants.EMBED_CLAN_MEMBERS_TITLE.format(clan_name=clan.name),
                color=Color.green(),
                description=constants.EMBED_CLAN_MEMBERS_DESCRIPTION.format(member_count=len(clan.members))
            )

            if leader_pages:
                embed.add_field(
                    name=constants.FIELD_LEADERS,
                    value="\n".join(leader_pages[0]) if leader_pages[0] else "Ninguno",
                    inline=False
                )

            if member_pages:
                embed.add_field(
                    name=constants.FIELD_MEMBERS,
                    value="\n".join(member_pages[0]) if member_pages[0] else "Ninguno",
                    inline=False
                )

            return await interaction.followup.send(embed=embed, ephemeral=self.kwargs.get('ephemeral', True))

        # Si necesitamos múltiples páginas
        embeds = []
        max_pages = max(len(leader_pages), len(member_pages))

        for page_num in range(max_pages):
            embed = Embed(
                title=constants.EMBED_CLAN_MEMBERS_TITLE.format(clan_name=clan.name),
                color=Color.green(),
                description=constants.EMBED_CLAN_MEMBERS_DESCRIPTION.format(member_count=len(clan.members))
            )

            # Añadir información de página
            embed.set_footer(text=f"Página {page_num + 1} de {max_pages}")

            # Añadir líderes si hay en esta página
            if page_num < len(leader_pages):
                field_name = constants.FIELD_LEADERS
                if len(leader_pages) > 1:
                    field_name += f" (Página {page_num + 1})"
                
                embed.add_field(
                    name=field_name,
                    value="\n".join(leader_pages[page_num]),
                    inline=False
                )

            # Añadir miembros si hay en esta página
            if page_num < len(member_pages):
                field_name = constants.FIELD_MEMBERS
                if len(member_pages) > 1:
                    field_name += f" (Página {page_num + 1})"
                
                embed.add_field(
                    name=field_name,
                    value="\n".join(member_pages[page_num]),
                    inline=False
                )

            embeds.append(embed)

        # Si solo hay un embed, enviarlo directamente
        if len(embeds) == 1:
            await interaction.followup.send(embed=embeds[0], ephemeral=self.kwargs.get('ephemeral', True))
        else:
            # Para múltiples embeds, enviar el primero y luego los demás como followups
            await interaction.followup.send(embed=embeds[0], ephemeral=self.kwargs.get('ephemeral', True))
            
            # Enviar los demás embeds como followups adicionales
            for embed in embeds[1:]:
                await interaction.followup.send(embed=embed, ephemeral=self.kwargs.get('ephemeral', True))


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
                    embed=None
                )
        except Exception:
            pass
