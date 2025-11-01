import discord
from discord import Interaction, ButtonStyle
from datetime import datetime
from modules.core import logger
from modules.clan_settings.service import ClanSettingsService
from ..service import ClanService
from ..models import ClanChannel, ChannelType as ClanChannelType, ClanMemberRole
from ..utils import (
    generate_channel_name,
    assign_clan_roles_to_leader,
    demote_leader_to_member,
    remove_clan_channel,
)
from .. import constants


class ClanModSelectionView(discord.ui.View):
    """View base para selección de clanes en comandos de moderación"""

    def __init__(self, clans: list, action_type: str, **kwargs):
        super().__init__(timeout=300)
        self.clans = clans
        self.service = ClanService()
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
                    embed=None,
                )
        except Exception:
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
            elif self.action_type == "add_member":
                await self._handle_add_member(interaction)
        except Exception as e:
            logger.error(f"Error en execute_action: {str(e)}")
            await interaction.followup.send(
                f"❌ Error al ejecutar la acción: {str(e)}", ephemeral=True
            )

    async def _handle_add_channel(self, interaction: Interaction):
        """Manejar creación de canal"""
        clan = self.selected_clan
        tipo = self.kwargs.get('tipo')

        try:
            # Obtener servicios necesarios
            settings_service = ClanSettingsService()

            # Verificar límites de canales usando configuración per-clan
            canales_existentes = [c for c in clan.channels if c.type == tipo]

            # Obtener límite del clan directamente
            if tipo == "text":
                max_canales = clan.max_text_channels
            else:
                max_canales = clan.max_voice_channels

            if len(canales_existentes) >= max_canales:
                return await interaction.followup.send(
                    f"❌ El clan **{clan.name}** ya tiene el máximo de canales de {tipo} ({max_canales}).",
                    ephemeral=True,
                )

            # Obtener configuración para categorías
            settings, error = await settings_service.get_settings()
            if error:
                return await interaction.followup.send(
                    f"❌ Error al obtener configuración: {error}", ephemeral=True
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
                    connect=False if tipo == "voice" else None,
                ),
                rol_clan: discord.PermissionOverwrite(
                    view_channel=True,
                    read_messages=True if tipo == "text" else None,
                    send_messages=True if tipo == "text" else None,
                    connect=True if tipo == "voice" else None,
                    speak=True if tipo == "voice" else None,
                ),
            }

            # Calcular la posición del nuevo canal
            position = None
            if categoria:
                # Obtener información actualizada del clan desde la BD
                clan_actualizado, _ = await self.service.get_clan_by_id(clan.id)
                if clan_actualizado:
                    # Obtener todos los canales del clan en esta categoría del mismo tipo
                    canales_clan_en_categoria = []
                    for ch in categoria.channels:
                        # Verificar si este canal pertenece al clan usando la información actualizada
                        pertenece_al_clan = any(
                            clan_ch.channel_id == ch.id for clan_ch in clan_actualizado.channels
                        )

                        if pertenece_al_clan:
                            # Verificar que sea del mismo tipo usando el tipo nativo de Discord
                            canal_es_texto = ch.type == discord.ChannelType.text
                            canal_es_voz = ch.type == discord.ChannelType.voice

                            if (tipo == "text" and canal_es_texto) or (
                                tipo == "voice" and canal_es_voz
                            ):
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
                        name=nombre, overwrites=permisos
                    )
                else:
                    nuevo_canal = await interaction.guild.create_text_channel(
                        name=nombre, overwrites=permisos
                    )
            else:  # voice
                if categoria:
                    nuevo_canal = await categoria.create_voice_channel(
                        name=nombre, overwrites=permisos
                    )
                else:
                    nuevo_canal = await interaction.guild.create_voice_channel(
                        name=nombre, overwrites=permisos
                    )

            # Si se calculó una posición específica, mover el canal después de crearlo
            if position is not None:
                try:
                    await nuevo_canal.edit(position=position)
                except Exception as e:
                    logger.error(f"Error al posicionar canal {nuevo_canal.name}: {e}")

            # Guardar en la base de datos
            canal_obj = ClanChannel(
                channel_id=nuevo_canal.id,
                name=nuevo_canal.name,
                type=ClanChannelType.TEXT.value if tipo == "text" else ClanChannelType.VOICE.value,
                clan_id=clan.id,
                created_at=datetime.now(),
            )

            error = self.service.save_clan_channel(canal_obj)
            if error:
                # Si hay error al guardar, eliminar el canal creado
                await nuevo_canal.delete()
                return await interaction.followup.send(
                    f"❌ Error al guardar el canal: {error}", ephemeral=True
                )

            await interaction.followup.send(
                f"✅ Canal **{nombre}** ({tipo}) añadido exitosamente al clan **{clan.name}**. "
                f"Canal: {nuevo_canal.mention}",
                ephemeral=True,
            )

        except Exception as e:
            logger.error(f"Error al crear canal adicional: {str(e)}")
            await interaction.followup.send(f"❌ Error al crear el canal: {str(e)}", ephemeral=True)

    async def _handle_add_leader(self, interaction: Interaction):
        """Manejar promoción a líder"""
        clan = self.selected_clan
        miembro = self.kwargs.get('miembro')

        # Verificar que el miembro está en el clan
        es_miembro = any(m.user_id == miembro.id for m in clan.members)
        if not es_miembro:
            return await interaction.followup.send(
                f"❌ {miembro.mention} no es miembro del clan **{clan.name}**.", ephemeral=True
            )

        # Verificar que no es ya líder
        es_lider = any(
            m.user_id == miembro.id and m.role == ClanMemberRole.LEADER.value for m in clan.members
        )
        if es_lider:
            return await interaction.followup.send(
                f"❌ {miembro.mention} ya es líder del clan **{clan.name}**.", ephemeral=True
            )

        # Promover a líder
        error = self.service.promote_member_to_leader(miembro.id, clan.id)
        if error:
            return await interaction.followup.send(
                f"❌ Error al promover a líder: {error}", ephemeral=True
            )

        # Asignar roles de Discord
        success, role_error = await assign_clan_roles_to_leader(
            interaction.guild, miembro, clan.id, self.service
        )

        if success:
            await interaction.followup.send(
                f"✅ {miembro.mention} ha sido promovido a líder del clan **{clan.name}** exitosamente.",
                ephemeral=True,
            )
        else:
            await interaction.followup.send(
                f"⚠️ {miembro.mention} ha sido promovido a líder del clan **{clan.name}** en la base de datos, pero hubo un problema con los roles: {role_error}",
                ephemeral=True,
            )

    async def _handle_remove_leader(self, interaction: Interaction):
        """Manejar degradación de líder"""
        clan = self.selected_clan
        miembro = self.kwargs.get('miembro')

        # Quitar liderazgo
        success, error_msg = await demote_leader_to_member(
            interaction.guild, miembro, clan.id, self.service
        )

        if success:
            await interaction.followup.send(
                f"✅ {miembro.mention} ya no es líder del clan **{clan.name}**.", ephemeral=True
            )
        else:
            await interaction.followup.send(
                f"❌ Error al quitar liderazgo: {error_msg}", ephemeral=True
            )

    async def _handle_remove_channel(self, interaction: Interaction):
        """Manejar eliminación de canal"""
        clan = self.selected_clan
        canal = self.kwargs.get('canal')

        # Verificar que el canal pertenece al clan
        canal_existe = any(ch.channel_id == canal.id for ch in clan.channels)
        if not canal_existe:
            return await interaction.followup.send(
                f"❌ El canal {canal.mention} no pertenece al clan **{clan.name}**.", ephemeral=True
            )

        # Eliminar canal
        success, error_msg = await remove_clan_channel(interaction.guild, canal.id, clan.id)

        if success:
            await interaction.followup.send(
                f"✅ Canal **{canal.name}** eliminado del clan **{clan.name}** exitosamente.",
                ephemeral=True,
            )
        else:
            await interaction.followup.send(
                f"❌ Error al eliminar canal: {error_msg}", ephemeral=True
            )

    async def _handle_add_member(self, interaction: Interaction):
        """Manejar adición directa de miembro al clan"""
        clan = self.selected_clan
        miembro = self.kwargs.get('miembro')

        if not miembro:
            return await interaction.followup.send(
                "❌ Error: No se especificó el miembro a añadir.", ephemeral=True
            )

        # Verificar que el miembro no esté ya en el clan
        es_miembro = any(m.user_id == miembro.id for m in clan.members)
        if es_miembro:
            return await interaction.followup.send(
                f"❌ {miembro.mention} ya es miembro del clan **{clan.name}**.", ephemeral=True
            )

        # Añadir miembro al clan
        error = await self.service.add_member_to_clan(miembro.id, clan.id)
        if error:
            return await interaction.followup.send(
                constants.ERROR_ADDING_MEMBER.format(error=error), ephemeral=True
            )

        # Asignar el rol del clan al miembro
        try:
            rol_clan = interaction.guild.get_role(clan.role_id)
            if rol_clan:
                await miembro.add_roles(rol_clan)
        except Exception as role_error:
            logger.error(f"Error al asignar rol al miembro {miembro.id}: {role_error}")
            # Continuar aunque falle la asignación del rol

        await interaction.followup.send(
            constants.SUCCESS_MEMBER_ADDED.format(member=miembro.mention, clan_name=clan.name),
            ephemeral=True,
        )


class ClanSelectionButton(discord.ui.Button):
    """Botón individual para cada clan"""

    def __init__(self, clan, index: int):
        # Truncar nombre si es muy largo para el botón
        label = clan.name[:80] if len(clan.name) > 80 else clan.name
        super().__init__(
            style=ButtonStyle.primary, label=label, custom_id=f"clan_{clan.id}_{index}"
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

        # Usar defer para poder seguir procesando
        await interaction.response.defer(ephemeral=True)

        # Editar el mensaje original
        try:
            await interaction.edit_original_response(
                content=f"**Clan seleccionado:** {self.clan.name}", view=view, embed=None
            )
        except Exception as e:
            logger.error(f"Error al editar mensaje: {e}")

        # Ejecutar la acción correspondiente
        await view.execute_action(interaction)
