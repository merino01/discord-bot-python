from datetime import datetime, timezone
from discord import (
	Interaction,
	Embed,
	Color,
	Member,
	ui,
	TextStyle,
	ButtonStyle
)
from modules.core.utils import send_message_to_channel

class MyButtonsView(ui.View):
	def __init__(self, member: Member):
		super().__init__()
		self.member = member

	@ui.button(label="Aceptar", style=ButtonStyle.green)
	async def onAccept(self, interaction: Interaction, button: ui.Button):
		try:
			await self.disable_all_buttons(interaction)
			await self.member.send(
				content=f"Se ha aceptado la solicitud de desbaneo del usuario: {self.member.display_name}"
			)
			await self.member.unban()
			await interaction.message.edit(view=None)
			await interaction.response.send_message(
				content=f"Se ha desbaneado al usuario <@{self.member.id}>"
            )
		except Exception as exception:
			print(exception)

	@ui.button(label="Rechazar", style=ButtonStyle.red)
	async def onReject(self, interaction: Interaction, button: ui.Button):

		try:
			await self.disable_all_buttons(interaction)
			await self.member.send(
				content=f"Se ha rechazado la solicitud de desbaneo del usuario: {self.member.display_name}"
			)
			await interaction.message.edit(view=None)
			await interaction.response.send_message(
				content=f"No se va a desbanear al usuario <@{self.member.id}>"
            )
		except Exception as exception:
			print(exception)

	async def disable_all_buttons(self, interaction: Interaction):
		for btn in self.children:
			btn.disabled = True
		await interaction.message.edit(view=self)

class UnbanModal(ui.Modal, title="Solicitud de desbaneo"):
	razon = ui.TextInput(
		label="¿Por qué deberías ser desbaneado?",
		style=TextStyle.paragraph,
		placeholder="Explica brevemente...",
		required=True,
		max_length=300,
	)

	def __init__(self, member: Member):
		super().__init__()
		self.member = member

	async def on_submit(self, interaction: Interaction):
		embed = Embed(
			colour=Color.red(),
			title=f"Solicitud desbaneo de: {self.member.display_name}",
			description=self.razon.value,
			timestamp= datetime.now(timezone.utc)
		)
		embed.set_footer(text="Bot Dead by daylight España")
		embed.set_author(name="ID usuario: "+str(self.member.id))
		embed.set_thumbnail(url=self.member.display_avatar.url)
		view = MyButtonsView(self.member)

		try:
			channel = await interaction.client.fetch_channel(1373253661467082754)
			await send_message_to_channel(channel=channel, view=view, embed=embed)
			await interaction.response.send_message(content="Solicitud de desbaneo enviada")
		except Exception as exception:
			print(exception)

class OpenUnbanModal(ui.View):
	def __init__(self, member: Member):
		super().__init__()
		self.member = member

	@ui.button(label="Solicitar desbaneo", style=ButtonStyle.primary)
	async def openModal(self, interaction: Interaction, button: ui.Button):
		await interaction.response.send_modal(UnbanModal(self.member))
		await interaction.message.edit(view=None)