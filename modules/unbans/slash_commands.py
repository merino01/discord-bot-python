from discord import (
	app_commands,
	Interaction,
	TextChannel,
	Object,
	Embed,
	Color,
	Member,
	ui,
	TextStyle,
	ButtonStyle,
	utils
)

from discord.ext import commands
from settings import guild_id
from datetime import datetime, timezone

class MyButtonsView(ui.View):

	def __init__(self, member: Member):
		super().__init__()
		self.member = member

	@ui.button(label="Aceptar", style=ButtonStyle.green)
	async def onAccept(self, interaction: Interaction, button: ui.Button):

		try:
			await self.disable_all_buttons(interaction)
			await interaction.followup.send(content="Se ha aceptado la solicitud de desbaneo del usuario: "+ self.member.display_name +" por: "+interaction.user.display_name, ephemeral=True)
		except Exception as exception:
			print(exception)

	@ui.button(label="Rechazar", style=ButtonStyle.red)
	async def onReject(self, interaction: Interaction, button: ui.Button):

		try:
			await self.disable_all_buttons(interaction)
			await interaction.followup.send(content="Se ha rechazado la solicitud de desbaneo del usuario: "+ self.member.display_name +" por: "+interaction.user.display_name, ephemeral=True)
		except Exception as exception:
			print(exception)

	async def disable_all_buttons(self, interaction: Interaction):
		for btn in self.children:
			btn.disabled = True
		await interaction.response.edit_message(content="Todos los botones han sido deshabilitados.", view=self)

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

		await interaction.response.send_message(embed=embed, view=view)

class UnbanCommands(commands.GroupCog, name="solicitud"):
	
	def __init__(self, bot):
		self.bot = bot

	##########################################################
	### Comando para mandar una solicitud de desbaneo ########
	##########################################################

	@app_commands.command(name="desbaneo", description="Solicitar desbaneo a Dead by daylight España")
	@app_commands.checks.has_permissions(
		manage_channels=True,
		manage_messages=True
	)
	async def generateModal(
		self,
		interaction: Interaction,
	):
		modal = UnbanModal(interaction.user)
		await interaction.response.send_modal(modal)

async def setup(bot):
	"""setup"""
	await bot.add_cog(
		UnbanCommands(bot),
		guild=Object(id=guild_id)
	)