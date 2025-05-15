from discord import (
    app_commands,
    Interaction,
    TextChannel,
    Object,
    Embed,
    Color,
	Member,
	ui,
	TextStyle
)
from discord.ext import commands
from settings import guild_id

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
            description=self.razon.value
        )
        embed.set_footer(text="Bot Dead by daylight España")
        embed.set_author(name="ID usuario: "+str(self.member.id))
        embed.set_thumbnail(url=self.member.display_avatar.url)

        await interaction.response.send_message(embed=embed)

class UnbanCommands(commands.GroupCog, name="desbaneo"):
    
	def __init__(self, bot):
		self.bot = bot

	##########################################################
    ### Comando para mandar una solicitud de desbaneo ########
    ##########################################################

	@app_commands.command(name="unban", description="Solicitar desbaneo a Dead by daylight España")
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