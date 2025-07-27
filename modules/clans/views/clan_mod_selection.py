import discord
from discord import Interaction, ButtonStyle, Embed, Color
from typing import Optional, Union
from datetime import datetime
from modules.core import logger
from modules.clan_settings.service import ClanSettingsService
from ..service import ClanService
from ..models import ClanChannel, ChannelType as ClanChannelType, ClanMemberRole
from ..utils import generate_channel_name, assign_clan_roles_to_leader, demote_leader_to_member, remove_clan_channel


class ClanModSelectionView(discord.ui.View):
    """View base para selección de clanes en comandos de moderación"""
    
    def __init__(self, clans: list, action_type: str, **kwargs):
        super().__init__(timeout=300)
        self.clans = clans
        self.action_type = action_type
        self.selected_clan = None
        self.kwargs = kwargs
        
        # Añadir botones para cada clan (máximo 25 botones por view)
        for i, clan in enumerate(clans[:25]):
            button = ClanSelectionButton(clan, i)
            self.add_item(button)
    
    async def on_timeout(self):
        # Deshabilitar todos los botones cuando expire
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
        except:
            pass

    async def execute_action(self, interaction: Interaction):
        """Ejecutar la acción específica según el tipo"""
        try:
            if self.action_type == "add_channel":
                await self._handle_add_channel(interaction)
            elif self.action_type == "add_leader":
                await self._handle_add_leader(interaction)
            elif self.action_type == "remove_leader":
                await self._handle_remove_leader(interaction)
            elif self.action_type == "remove_channel":
                await self._handle_remove_channel(interaction)
        except Exception as e:
            logger.error(f"Error en execute_action: {str(e)}")
            await interaction.followup.send(
                f"❌ Error al ejecutar la acción: {str(e)}", 
                ephemeral=True
            )
    
    async def _handle_add_channel(self, interaction: Interaction):
        """Manejar creación de canal"""
        clan = self.selected_clan
        tipo = self.kwargs.get('tipo')
        service = ClanService()
        
        try:
            # Obtener configuración para verificar límites
            settings_service = ClanSettingsService()
            settings, error = await settings_service.get_settings()
            if error:
                return await interaction.followup.send(
                    f"❌ Error al obtener configuración: {error}", ephemeral=True
                )
            
            # Verificar límites de canales
            canales_existentes = [c for c in clan.channels if c.type == tipo]
            max_canales = (settings.max_text_channels if tipo == "text" else settings.max_voice_channels)
            
            if len(canales_existentes) >= max_canales:
                return await interaction.followup.send(
                    f"❌ El clan **{clan.name}** ya tiene el máximo de canales de {tipo} ({max_canales}).", 
                    ephemeral=True
                )
            
            # Generar nombre automático
            nombre = generate_channel_name(clan.name, clan.channels, tipo)
            
            # Obtener el rol del clan para los permisos
            rol_clan = interaction.guild.get_role(clan.role_id)
            if not rol_clan:
                return await interaction.followup.send(
                    "❌ Error: No se encontró el rol del clan.", ephemeral=True
                )
            
            # Obtener categorías configuradas
            if tipo == "text":
                id_categoria = settings.text_category_id
            else:
                id_categoria = settings.voice_category_id
            
            categoria = interaction.guild.get_channel(id_categoria) if id_categoria else None
            
            # Configurar permisos
            permisos = {
                interaction.guild.default_role: discord.PermissionOverwrite(
                    view_channel=False,
                    read_messages=False if tipo == "text" else None,
                    connect=False if tipo == "voice" else None
                ),
                rol_clan: discord.PermissionOverwrite(
                    view_channel=True,
                    read_messages=True if tipo == "text" else None,
                    send_messages=True if tipo == "text" else None,
                    connect=True if tipo == "voice" else None,
                    speak=True if tipo == "voice" else None
                ),
            }
            
            # Calcular la posición del nuevo canal
            position = None
            if categoria:
                # Obtener todos los canales del clan en esta categoría del mismo tipo
                canales_clan_en_categoria = []
                for ch in categoria.channels:
                    # Verificar si este canal pertenece al clan
                    if any(clan_ch.channel_id == ch.id for clan_ch in clan.channels):
                        # Verificar que sea del mismo tipo
                        if (tipo == "text" and hasattr(ch, 'send')) or (tipo == "voice" and hasattr(ch, 'connect')):
                            canales_clan_en_categoria.append(ch)
                
                # Si hay canales del clan, colocar el nuevo después del último
                if canales_clan_en_categoria:
                    # Ordenar por posición y tomar el último
                    canales_clan_en_categoria.sort(key=lambda x: x.position)
                    ultimo_canal = canales_clan_en_categoria[-1]
                    position = ultimo_canal.position + 1
            
            # Crear el canal
            if tipo == "text":
                if categoria:
                    nuevo_canal = await categoria.create_text_channel(
                        name=nombre, 
                        overwrites=permisos, 
                        position=position
                    )
                else:
                    nuevo_canal = await interaction.guild.create_text_channel(name=nombre, overwrites=permisos)
            else:  # voice
                if categoria:
                    nuevo_canal = await categoria.create_voice_channel(
                        name=nombre, 
                        overwrites=permisos, 
                        position=position
                    )
                else:
                    nuevo_canal = await interaction.guild.create_voice_channel(name=nombre, overwrites=permisos)
            
            # Guardar en la base de datos
            canal_obj = ClanChannel(
                channel_id=nuevo_canal.id,
                name=nuevo_canal.name,
                type=ClanChannelType.TEXT.value if tipo == "text" else ClanChannelType.VOICE.value,
                clan_id=clan.id,
                created_at=datetime.now()
            )
            
            error = service.save_clan_channel(canal_obj)
            if error:
                # Si hay error al guardar, eliminar el canal creado
                await nuevo_canal.delete()
                return await interaction.followup.send(
                    f"❌ Error al guardar el canal: {error}", ephemeral=True
                )
            
            await interaction.followup.send(
                f"✅ Canal **{nombre}** ({tipo}) añadido exitosamente al clan **{clan.name}**. "
                f"Canal: {nuevo_canal.mention}", 
                ephemeral=True
            )
            
        except Exception as e:
            logger.error(f"Error al crear canal adicional: {str(e)}")
            await interaction.followup.send(
                f"❌ Error al crear el canal: {str(e)}", ephemeral=True
            )
    
    async def _handle_add_leader(self, interaction: Interaction):
        """Manejar promoción a líder"""
        service = ClanService()
        clan = self.selected_clan
        miembro = self.kwargs.get('miembro')
        
        # Verificar que el miembro está en el clan
        es_miembro = any(m.user_id == miembro.id for m in clan.members)
        if not es_miembro:
            return await interaction.followup.send(
                f"❌ {miembro.mention} no es miembro del clan **{clan.name}**.",
                ephemeral=True
            )
        
        # Verificar que no es ya líder
        es_lider = any(m.user_id == miembro.id and m.role == ClanMemberRole.LEADER.value for m in clan.members)
        if es_lider:
            return await interaction.followup.send(
                f"❌ {miembro.mention} ya es líder del clan **{clan.name}**.",
                ephemeral=True
            )
        
        # Promover a líder
        error = service.promote_member_to_leader(miembro.id, clan.id)
        if error:
            return await interaction.followup.send(
                f"❌ Error al promover a líder: {error}",
                ephemeral=True
            )
        
        # Asignar roles de Discord
        success, role_error = await assign_clan_roles_to_leader(
            interaction.guild, miembro, clan.id, service
        )
        
        if success:
            await interaction.followup.send(
                f"✅ {miembro.mention} ha sido promovido a líder del clan **{clan.name}** exitosamente.",
                ephemeral=True
            )
        else:
            await interaction.followup.send(
                f"⚠️ {miembro.mention} ha sido promovido a líder del clan **{clan.name}** en la base de datos, pero hubo un problema con los roles: {role_error}",
                ephemeral=True
            )
    
    async def _handle_remove_leader(self, interaction: Interaction):
        """Manejar degradación de líder"""
        service = ClanService()
        clan = self.selected_clan
        miembro = self.kwargs.get('miembro')
        
        # Quitar liderazgo
        success, error_msg = await demote_leader_to_member(
            interaction.guild, miembro, clan.id, service
        )
        
        if success:
            await interaction.followup.send(
                f"✅ {miembro.mention} ya no es líder del clan **{clan.name}**.", 
                ephemeral=True
            )
        else:
            await interaction.followup.send(
                f"❌ Error al quitar liderazgo: {error_msg}", 
                ephemeral=True
            )
    
    async def _handle_remove_channel(self, interaction: Interaction):
        """Manejar eliminación de canal"""
        clan = self.selected_clan
        canal = self.kwargs.get('canal')
        
        # Verificar que el canal pertenece al clan
        canal_existe = any(ch.channel_id == canal.id for ch in clan.channels)
        if not canal_existe:
            return await interaction.followup.send(
                f"❌ El canal {canal.mention} no pertenece al clan **{clan.name}**.", 
                ephemeral=True
            )
        
        # Eliminar canal
        success, error_msg = await remove_clan_channel(
            interaction.guild, canal.id, clan.id
        )
        
        if success:
            await interaction.followup.send(
                f"✅ Canal **{canal.name}** eliminado del clan **{clan.name}** exitosamente.", 
                ephemeral=True
            )
        else:
            await interaction.followup.send(
                f"❌ Error al eliminar canal: {error_msg}", 
                ephemeral=True
            )


class ClanSelectionButton(discord.ui.Button):
    """Botón individual para cada clan"""
    
    def __init__(self, clan, index: int):
        # Truncar nombre si es muy largo para el botón
        label = clan.name[:80] if len(clan.name) > 80 else clan.name
        super().__init__(
            style=ButtonStyle.primary,
            label=label,
            custom_id=f"clan_{clan.id}_{index}"
        )
        self.clan = clan
    
    async def callback(self, interaction: Interaction):
        view: ClanModSelectionView = self.view
        view.selected_clan = self.clan
        
        # Deshabilitar todos los botones
        for item in view.children:
            item.disabled = True
        
        # Cambiar el estilo del botón seleccionado
        self.style = ButtonStyle.success
        self.label = f"✅ {self.clan.name[:77]}"
        
        await interaction.response.edit_message(
            content=f"**Clan seleccionado:** {self.clan.name}",
            view=view
        )
        
        # Ejecutar la acción correspondiente
        await view.execute_action(interaction)
