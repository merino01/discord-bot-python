from discord import Interaction


async def send_error_message(interaction: Interaction, error_message: str):
    """Envía un mensaje de error de forma consistente"""
    if interaction.response.is_done():
        await interaction.followup.send(error_message, ephemeral=True)
    else:
        await interaction.response.send_message(error_message, ephemeral=True)


async def send_success_message(interaction: Interaction, success_message: str):
    """Envía un mensaje de éxito de forma consistente"""
    if interaction.response.is_done():
        await interaction.followup.send(success_message, ephemeral=True)
    else:
        await interaction.response.send_message(success_message, ephemeral=True)
