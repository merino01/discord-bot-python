from discord import (
    app_commands,
    Interaction,
    TextChannel,
    Object,
    Embed,
    Color
)
from discord.ext import commands
from settings import guild_id

class UnbanCommands(commands.GroupCog, name="desbaneo"):
    
	def __init__(self, bot):
		self.bot = bot
		super().__init__()

	@app_commands.command(name="unban", description="Desbanea a un usuario")
	@app_commands.describe(
		idusuario="Id del usuario a desbanear"
	)
	@app_commands.checks.has_permissions(
        manage_channels=True,
        manage_messages=True
    )
	async def unban_user(
		self,
		interaction: Interaction,
		idusuario: str
	):
		"""Desbanear a un usuario"""

		print("Hello world!")
	
async def setup(bot):
	"""setup"""
	await bot.add_cog(
		UnbanCommands(bot),
		guild=Object(id=guild_id)
	)