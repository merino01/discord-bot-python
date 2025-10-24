from typing import Optional
from discord import app_commands, Interaction, TextChannel, Object, Embed, Color
from discord.ext import commands
from settings import guild_id
from .service import LogsConfigService
from .models import LogConfig, LogConfigType
from translator import __


class ConfigLogsCommands(commands.GroupCog, name="logs"):
    def __init__(self, bot):
        self.bot = bot
        self.service = LogsConfigService()

    #####################################################
    ### Comando para configurar los logs del servidor ###
    #####################################################
    @app_commands.command(name="configurar", description=constants.COMMAND_CONFIG_DESC)
    @app_commands.describe(
        tipo_de_log=constants.PARAM_LOG_TYPE_DESC,
        activar=constants.PARAM_ACTIVATE_DESC,
        canal=constants.PARAM_CHANNEL_DESC,
    )
    @app_commands.choices(
        tipo_de_log=[
            app_commands.Choice(name=constants.CHOICE_CHAT, value=constants.LOG_TYPE_CHAT),
            app_commands.Choice(name=constants.CHOICE_VOICE, value=constants.LOG_TYPE_VOICE),
            app_commands.Choice(name=constants.CHOICE_MEMBERS, value=constants.LOG_TYPE_MEMBERS),
            app_commands.Choice(name=constants.CHOICE_JOIN_LEAVE, value=constants.LOG_TYPE_JOIN_LEAVE),
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
                content=__("logsConfig.errorMessages.noChannelForActivation"),
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
                content=__("logsConfig.successMessages.logActivated", log_type=tipo_de_log, channel_id=canal.id),
                ephemeral=True,
            )
        elif not activar:
            await interaction.response.send_message(
                content=__("logsConfig.successMessages.logDeactivated", log_type=tipo_de_log), ephemeral=True
            )
        else:
            await interaction.response.send_message(
                content=__("logsConfig.errorMessages.activatingLog", log_type=tipo_de_log),
                ephemeral=True,
            )

    #####################################################
    ### Comando para ver la configuración de los logs ###
    #####################################################
    @app_commands.command(name="listar", description=constants.COMMAND_LIST_DESC)
    @app_commands.checks.has_permissions(administrator=True)
    async def show_logs_config(self, interaction: Interaction, persistente: bool = False):
        log_configs, error = self.service.get_all()
        if error:
            await interaction.response.send_message(content=error, ephemeral=True)
            return

        if not log_configs:
            await interaction.response.send_message(__("logsConfig.messages.noLogsConfigured"), ephemeral=True)
            return

        await interaction.response.defer(ephemeral=not persistente)

        embeds = []

        for log_config in log_configs:
            embed = Embed(
                title=__("logsConfig.embeds.titles.logType", log_type=log_config.type),
                color=Color.dark_green() if log_config.enabled else Color.dark_red(),
            )

            if (channel_id := log_config.channel_id) and log_config.enabled:
                embed.add_field(name=__("logsConfig.embeds.fields.channel"), value=f"<#{channel_id}>", inline=True)
            embed.add_field(
                name=__("logsConfig.embeds.fields.status"),
                value=__("logsConfig.embeds.values.enabled") if log_config.enabled else __("logsConfig.embeds.values.disabled"),
                inline=True,
            )
            embeds.append(embed)
        await interaction.followup.send(embeds=embeds, ephemeral=not persistente)


async def setup(bot):
    await bot.add_cog(ConfigLogsCommands(bot), guild=Object(id=guild_id))
