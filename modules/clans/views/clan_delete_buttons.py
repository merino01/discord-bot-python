from typing import List
import discord
from discord import Interaction, ButtonStyle
from discord.ui import View, Button
from modules.core import logger
from ..models import FullClan
from ..service import ClanService
from ..utils import remove_clan_roles_from_member


class ClanDeleteView(View):
    def __init__(self, clans: List[FullClan], service: ClanService):
        super().__init__(timeout=300)  # 5 minutos
        self.clans = clans
        self.service = service

        # Crear botones para cada clan (máximo 25 botones por limitación de Discord)
        for i, clan in enumerate(clans[:25]):
            button = Button(
                label=f"{clan.name} (ID: {clan.id[:8]}...)",
                style=ButtonStyle.danger,
                custom_id=f"delete_clan_{clan.id}",
            )
            button.callback = self.create_delete_callback(clan)
            self.add_item(button)

        # Botón de cancelar
        cancel_button = Button(
            label="❌ Cancelar", style=ButtonStyle.secondary, custom_id="cancel_delete"
        )
        cancel_button.callback = self.cancel_callback
        self.add_item(cancel_button)

    def create_delete_callback(self, clan: FullClan):
        async def delete_callback(interaction: Interaction):
            try:
                # Confirmar eliminación
                confirm_view = ConfirmDeleteView(clan, self.service)
                embed = discord.Embed(
                    title="⚠️ Confirmar eliminación",
                    description=f"¿Estás seguro de que quieres eliminar el clan **{clan.name}**?\n\n"
                    f"**Esta acción no se puede deshacer**\n"
                    f"- Se eliminarán todos los canales del clan\n"
                    f"- Se quitarán todos los roles a los miembros\n"
                    f"- Se eliminará el rol del clan\n"
                    f"- Se perderán todos los datos del clan",
                    color=discord.Color.red(),
                )
                embed.add_field(name="👥 Miembros", value=str(len(clan.members)), inline=True)
                embed.add_field(name="📺 Canales", value=str(len(clan.channels)), inline=True)

                await interaction.response.edit_message(embed=embed, view=confirm_view)

            except Exception as e:
                logger.error(f"Error en delete_callback: {str(e)}")
                await interaction.response.send_message(
                    f"Error inesperado: {str(e)}", ephemeral=True
                )

        return delete_callback

    async def cancel_callback(self, interaction: Interaction):
        embed = discord.Embed(
            title="❌ Operación cancelada",
            description="No se eliminó ningún clan.",
            color=discord.Color.green(),
        )
        await interaction.response.edit_message(embed=embed, view=None)

    async def on_timeout(self):
        # Deshabilitar todos los botones cuando expire el timeout
        for item in self.children:
            item.disabled = True


class ConfirmDeleteView(View):
    def __init__(self, clan: FullClan, service: ClanService):
        super().__init__(timeout=60)  # 1 minuto para confirmar
        self.clan = clan
        self.service = service

    @discord.ui.button(label="✅ Sí, eliminar clan", style=ButtonStyle.danger)
    async def confirm_delete(self, interaction: Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)

        try:
            # Eliminar clan de la base de datos PRIMERO
            error = await self.service.delete_clan(self.clan.id)
            if error:
                return await interaction.followup.send(
                    f"No se ha podido eliminar el clan: {error}", ephemeral=True
                )

            # Quitar todos los roles de clan a todos los miembros
            for member in self.clan.members:
                await remove_clan_roles_from_member(
                    guild=interaction.guild,
                    member_id=member.user_id,
                    clan_role_id=self.clan.role_id,
                    should_check_other_clans=True,
                )

            # Eliminar el rol del clan
            role = interaction.guild.get_role(self.clan.role_id)
            if role:
                try:
                    await role.delete()
                except Exception as e:
                    logger.warning(f"No se pudo eliminar el rol del clan {self.clan.role_id}: {e}")

            # Eliminar canales
            for channel in self.clan.channels:
                channel_obj = interaction.guild.get_channel(channel.channel_id)
                if channel_obj:
                    try:
                        await channel_obj.delete()
                    except Exception as e:
                        logger.warning(f"No se pudo eliminar el canal {channel.channel_id}: {e}")

            # Actualizar mensaje con éxito
            embed = discord.Embed(
                title="✅ Clan eliminado",
                description=f"El clan **{self.clan.name}** ha sido eliminado exitosamente.",
                color=discord.Color.green(),
            )

            await interaction.edit_original_response(embed=embed, view=None)
            await interaction.followup.send("Clan eliminado con éxito.", ephemeral=True)

        except Exception as e:
            logger.error(f"Error al eliminar clan: {str(e)}")
            await interaction.followup.send(
                f"Error inesperado al eliminar el clan: {str(e)}", ephemeral=True
            )

    @discord.ui.button(label="❌ Cancelar", style=ButtonStyle.secondary)
    async def cancel_delete(self, interaction: Interaction, button: Button):
        embed = discord.Embed(
            title="❌ Eliminación cancelada",
            description=f"El clan **{self.clan.name}** no fue eliminado.",
            color=discord.Color.green(),
        )
        await interaction.response.edit_message(embed=embed, view=None)

    async def on_timeout(self):
        # Deshabilitar todos los botones cuando expire el timeout
        for item in self.children:
            item.disabled = True
