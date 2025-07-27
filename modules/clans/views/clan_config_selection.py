import discord
from discord import Interaction, ButtonStyle, Embed, Color
from discord.ui import View, Button, Select
from typing import List, Optional

from modules.core.logger import logger
from ..models import FullClan
from ..service import ClanService


class ClanConfigSelectionView(View):
    def __init__(self, clans: List[FullClan], service: ClanService, **config_params):
        super().__init__(timeout=300)
        self.clans = clans
        self.service = service
        self.config_params = config_params  # max_miembros, max_canales_texto, max_canales_voz
        self.selected_clan = None
        self.message = None

        # Crear dropdown si hay muchos clanes, botones si hay pocos
        if len(clans) > 10:
            self.add_item(ClanConfigSelect(clans))
        else:
            # Crear botones para cada clan (máximo 25 botones por view)
            for i, clan in enumerate(clans[:25]):
                button = Button(
                    label=clan.name[:80],  # Discord limita a 80 chars
                    style=ButtonStyle.secondary,
                    custom_id=f"config_clan_{i}",
                    emoji="🔧"
                )
                button.callback = self.create_clan_callback(clan)
                self.add_item(button)

    def create_clan_callback(self, clan: FullClan):
        async def clan_callback(interaction: Interaction):
            self.selected_clan = clan
            await self.execute_config(interaction)
        return clan_callback

    async def execute_config(self, interaction: Interaction):
        """Ejecutar la configuración del clan seleccionado"""
        try:
            await interaction.response.defer()
            
            clan = self.selected_clan
            
            # Construir mensaje de configuración actual
            embed = Embed(
                title=f"🔧 Configurando clan: {clan.name}",
                color=Color.blue()
            )
            
            # Mostrar configuración actual
            embed.add_field(
                name="📊 **Configuración Actual**",
                value=(
                    f"👥 **Miembros:** {clan.member_count}/{clan.max_members}\n"
                    f"💬 **Canales texto:** {len([c for c in clan.channels if c.type == 'text'])}/{clan.max_text_channels}\n" 
                    f"🔊 **Canales voz:** {len([c for c in clan.channels if c.type == 'voice'])}/{clan.max_voice_channels}"
                ),
                inline=False
            )
            
            # Aplicar cambios
            updates = []
            max_miembros = self.config_params.get('max_miembros')
            max_canales_texto = self.config_params.get('max_canales_texto')
            max_canales_voz = self.config_params.get('max_canales_voz')
            
            # Actualizar max_members si se proporcionó
            if max_miembros is not None:
                update_members_sql = "UPDATE clans SET max_members = ? WHERE id = ?"
                self.service.db.execute(update_members_sql, (max_miembros, clan.id))
                updates.append(f"👥 Máximo miembros: {clan.max_members} → **{max_miembros}**")
            
            # Actualizar configuración de canales
            error = await self.service.update_clan_config(
                clan.id,
                max_text_channels=max_canales_texto,
                max_voice_channels=max_canales_voz
            )
            
            if error:
                return await interaction.followup.send(
                    f"❌ Error al actualizar configuración: {error}", ephemeral=True
                )
            
            if max_canales_texto is not None:
                updates.append(f"💬 Máximo canales texto: {clan.max_text_channels} → **{max_canales_texto}**")
            
            if max_canales_voz is not None:
                updates.append(f"🔊 Máximo canales voz: {clan.max_voice_channels} → **{max_canales_voz}**")
            
            if updates:
                embed.add_field(
                    name="✅ **Cambios Aplicados**",
                    value="\n".join(updates),
                    inline=False
                )
                
                embed.add_field(
                    name="ℹ️ **Información**",
                    value="Los nuevos límites se aplicarán inmediatamente. Los elementos existentes que excedan los nuevos límites no se eliminarán automáticamente.",
                    inline=False
                )
            else:
                embed.add_field(
                    name="ℹ️ **Sin cambios**",
                    value="No se especificaron parámetros para actualizar.",
                    inline=False
                )

            # Desactivar la vista
            for item in self.children:
                item.disabled = True

            await interaction.edit_original_response(embed=embed, view=self)
            
        except Exception as e:
            logger.error(f"Error en execute_config: {str(e)}")
            await interaction.followup.send(
                f"❌ Error al configurar el clan: {str(e)}", 
                ephemeral=True
            )

    async def on_timeout(self):
        """Cuando la vista expira"""
        if self.message:
            try:
                for item in self.children:
                    item.disabled = True
                await self.message.edit(view=self)
            except:
                pass


class ClanConfigSelect(Select):
    def __init__(self, clans: List[FullClan]):
        options = []
        for clan in clans[:25]:  # Discord limita a 25 opciones
            options.append(discord.SelectOption(
                label=clan.name[:100],  # Discord limita a 100 chars
                description=f"Miembros: {clan.member_count}/{clan.max_members} | Canales: {len(clan.channels)}",
                value=clan.id,
                emoji="🔧"
            ))
        
        super().__init__(placeholder="Selecciona un clan para configurar...", options=options)

    async def callback(self, interaction: Interaction):
        view: ClanConfigSelectionView = self.view
        selected_clan_id = self.values[0]
        
        # Buscar el clan seleccionado
        for clan in view.clans:
            if clan.id == selected_clan_id:
                view.selected_clan = clan
                break
        
        await view.execute_config(interaction)
