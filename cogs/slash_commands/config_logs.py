"""
logs config commands
"""

from discord import app_commands, Interaction, TextChannel, Object, Embed, Color
from discord.ext import commands
from settings import guild_id
from services import LogsConfigService
from database.models import LogConfig, LogConfigType

class ConfigLogsCommands(commands.GroupCog, name="logs"):
    """
    Commands for configuring the logs
    """
    def __init__(self, bot):
        self.bot = bot


    #####################################################
    ### Comando para configurar los logs del servidor ###
    #####################################################
    @app_commands.command(
        name="configurar",
        description="Configura los logs del servidor"
    )
    @app_commands.describe(
        tipo_de_log="Tipo de log a configurar",
        activar="Activar o desactivar los logs",
        canal="Canal donde se enviarán los logs"
    )
    @app_commands.choices(tipo_de_log=[
        app_commands.Choice(name="Mensajes", value="chat"),
        app_commands.Choice(name="Voz", value="voice"),
        app_commands.Choice(name="Miembros", value="members"),
        app_commands.Choice(name="Entradas/Salidas", value="join_leave")
    ])
    @app_commands.checks.has_permissions(administrator=True)
    async def config_logs(
        self,
        interaction: Interaction,
        tipo_de_log: LogConfigType,
        activar: bool,
        canal: TextChannel
    ):
        """Config logs command"""
        log_config = LogConfig(
            type=tipo_de_log,
            channel_id=canal.id,
            enabled=activar
        )

        text = 'activado' if activar else 'desactivado'
        updated_ok = LogsConfigService.update(log_config)
        if updated_ok:
            await interaction.response.send_message(
                f"{tipo_de_log}log {text} en el canal {canal.mention}",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"Error al actualizar el {tipo_de_log}log",
                ephemeral=True
            )


    #####################################################
    ### Comando para ver la configuración de los logs ###
    #####################################################
    @app_commands.command(
        name="listar",
        description="Muestra la configuración de los logs"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def show_logs_config(
        self,
        interaction: Interaction
    ):
        """List logs command"""
        log_configs = LogsConfigService.get_all()
        if not log_configs:
            await interaction.response.send_message(
                "No hay logs configurados",
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        embeds = []

        for log_config in log_configs:
            embed = Embed(
                title=f"{log_config.type}log",
                color=Color.dark_green() if log_config.enabled else Color.dark_red()
            )
            embed.add_field(
                name="Canal",
                value=f"<#{log_config.channel_id}>",
                inline=True
            )
            embed.add_field(
                name="Estado",
                value="activado" if log_config.enabled else "desactivado",
                inline=True
            )
            embeds.append(embed)
        await interaction.followup.send(embeds=embeds, ephemeral=True)


async def setup(bot):
    """setup"""
    await bot.add_cog(
        ConfigLogsCommands(bot),
        guild=Object(id=guild_id)
    )
