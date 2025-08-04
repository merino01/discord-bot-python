from discord import Interaction, TextChannel, CategoryChannel, Embed, Color
from typing import Optional
from translator import __
from .. import views, utils, services


async def delete_message(
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

    # Mostrar select para elegir mensaje a eliminar
    embed = Embed(
        title=__("automaticMessages.messageList", count=len(messages)),
        description=__("automaticMessages.selectMessageToDelete", count=len(messages)),
        color=Color.red(),
    )

    view = views.MessageSelectView(messages, "delete", bot)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
