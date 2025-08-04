from typing import Optional
from discord import Interaction, TextChannel, CategoryChannel, Embed, Color
from translator import __
from .. import views, services, utils


async def list_messages(
    bot,
    interaction: Interaction,
    canal: Optional[TextChannel] = None,
    categoria: Optional[CategoryChannel] = None,
):
    service = services.AutomaticMessagesService()
    # Obtener mensajes según los filtros
    if canal:
        messages, error = service.get_by_channel_id(canal.id)
    elif categoria:
        messages, error = service.get_by_category_id(categoria.id)
    else:
        messages, error = service.get_all()

    if error:
        await utils.send_error_message(
            interaction, __("automaticMessages.errorMessages.errorGettingMessages")
        )
        return

    if not messages:
        embed = Embed(
            title=__("automaticMessages.noMessagesTitle"),
            description=__("automaticMessages.noMessagesDescription"),
            color=Color.orange(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Mostrar select para elegir mensaje a ver en detalle
    embed = Embed(
        title=__("automaticMessages.messageList", count=len(messages)),
        description=__("automaticMessages.selectMessageForDetails", count=len(messages)),
        color=Color.blue(),
    )

    view = views.MessageSelectView(messages, "view", bot)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
