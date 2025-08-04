from typing import Union, Optional
from discord import Interaction, TextChannel, CategoryChannel, Embed, Color
from modules.core import logger
from translator import __
from .. import constants, views, utils


async def program_message(
    interaction: Interaction,
    tipo_programacion: str,
    destino: Union[TextChannel, CategoryChannel],
    nombre: Optional[str] = None,
):
    try:
        # Validar nombre si se proporciona
        if nombre and len(nombre) > constants.MAX_NAME_LENGTH:
            await utils.send_error_message(
                interaction,
                __(
                    "automaticMessages.errorMessages.nameTooLong",
                    max_length=constants.MAX_NAME_LENGTH,
                ),
            )
            return

        # Validar destino
        if not isinstance(destino, (TextChannel, CategoryChannel)):
            await utils.send_error_message(
                interaction, __("automaticMessages.errorMessages.invalidDestination")
            )
            return

        # Validar que para "on_channel_create" se use una categoría
        if tipo_programacion == "on_channel_create" and not isinstance(destino, CategoryChannel):
            await utils.send_error_message(
                interaction, __("automaticMessages.errorMessages.categoryRequired")
            )
            return

        # Mostrar la nueva interfaz de configuración con embed y botones
        view = views.MessageBuilderView(tipo_programacion, destino, nombre)

        embed = Embed(
            title=__("automaticMessages.configureMessageEmbed.title"),
            description=__("automaticMessages.configureMessageEmbed.description"),
            color=Color.blue(),
        )

        embed.add_field(
            name=__("currentConfiguration"),
            value=__(
                "automaticMessages.configureMessageEmbed.destination", destination=destino.mention
            )
            + "\n"
            + __(
                "automaticMessages.configureMessageEmbed.type",
                type=_get_schedule_type_display(tipo_programacion),
            )
            + "\n"
            + __(
                "automaticMessages.configureMessageEmbed.name",
                name=nombre or __("automaticMessages.configureMessageEmbed.noName"),
            )
            + "\n\n"
            + __(
                "automaticMessages.configureMessageEmbed.status",
                status=__("automaticMessages.configureMessageEmbed.noContent"),
            ),
            inline=False,
        )

        embed.add_field(
            name=__("instructions"),
            value=__("automaticMessages.configureMessageEmbed.instructions.addText")
            + "\n"
            + __("automaticMessages.configureMessageEmbed.instructions.addEmbed")
            + "\n"
            + __("automaticMessages.configureMessageEmbed.instructions.addImage")
            + "\n"
            + __("automaticMessages.configureMessageEmbed.instructions.complete"),
            inline=False,
        )

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    except Exception as e:
        logger.error(e)


def _get_schedule_type_display(schedule_type: str) -> str:
    """Convierte el tipo de programación a un formato amigable"""
    displays = {
        "interval": __("automaticMessages.scheduleTypeChoices.interval"),
        "daily": __("automaticMessages.scheduleTypeChoices.daily"),
        "weekly": __("automaticMessages.scheduleTypeChoices.weekly"),
        "on_channel_create": __("automaticMessages.scheduleTypeChoices.on_channel_create"),
    }
    return displays.get(schedule_type, schedule_type)
