from typing import Optional
from discord import app_commands, Interaction, TextChannel, Object, Embed, Color
from discord.ext import commands
from settings import guild_id
from .service import LogsConfigService
from .models import LogConfig, LogConfigType


class ConfigLogsCommands(commands.GroupCog, name="logs"):
    def __init__(self, bot):
        self.bot = bot
        self.service = LogsConfigService()

    #####################################################
    ### Comando para configurar los logs del servidor ###
    #####################################################
    @app_commands.command(name="configurar", description="Configura los logs del servidor")
    @app_commands.describe(
        tipo_de_log="Tipo de log a configurar",
        activar="Activar o desactivar los logs",
        canal="Canal donde se enviarán los logs",
    )
    @app_commands.choices(
        tipo_de_log=[
            app_commands.Choice(name="Mensajes", value="chat"),
            app_commands.Choice(name="Voz", value="voice"),
            app_commands.Choice(name="Miembros", value="members"),
            app_commands.Choice(name="Entradas/Salidas", value="join_leave"),
        ]
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def config_logs(
        self,
        interaction: Interaction,
        tipo_de_log: LogConfigType,
        activar: bool,
        canal: Optional[TextChannel] = None,
    ):
        if not canal and activar:
            await interaction.response.send_message(
                content="No puedes activar los logs sin especificar un canal",
                ephemeral=True,
            )
            return

        log_config = LogConfig(
            type=tipo_de_log, channel_id=canal.id if canal else None, enabled=activar
        )

        _, error = self.service.update(log_config)
        if error:
            await interaction.response.send_message(content=error, ephemeral=True)
            return

        if activar and canal:
            await interaction.response.send_message(
                content=f"{tipo_de_log}log activado en el canal <#{canal.id}>",
                ephemeral=True,
            )
        elif not activar:
            await interaction.response.send_message(
                content=f"{tipo_de_log}log desactivado", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                content=f"Ha habido un error al activar el {tipo_de_log}log",
                ephemeral=True,
            )

    #####################################################
    ### Comando para ver la configuración de los logs ###
    #####################################################
    @app_commands.command(name="listar", description="Muestra la configuración de los logs")
    @app_commands.checks.has_permissions(administrator=True)
    async def show_logs_config(self, interaction: Interaction, persistente: bool = False):
        log_configs, error = self.service.get_all()
        if error:
            await interaction.response.send_message(content=error, ephemeral=True)
            return

        if not log_configs:
            await interaction.response.send_message("No hay logs configurados", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=not persistente)

        embeds = []

        for log_config in log_configs:
            embed = Embed(
                title=f"{log_config.type}log",
                color=Color.dark_green() if log_config.enabled else Color.dark_red(),
            )

            if (channel_id := log_config.channel_id) and log_config.enabled:
                embed.add_field(name="Canal", value=f"<#{channel_id}>", inline=True)
            embed.add_field(
                name="Estado",
                value="activado" if log_config.enabled else "desactivado",
                inline=True,
            )
            embeds.append(embed)
        await interaction.followup.send(embeds=embeds, ephemeral=not persistente)


async def setup(bot):
    await bot.add_cog(ConfigLogsCommands(bot), guild=Object(id=guild_id))
