from discord.ext import commands
from settings import guild_id
from .views.unban_action_buttons import OpenUnbanModal

class UnbanCommands(commands.GroupCog):
	
	def __init__(self, bot):
		self.bot = bot

	##########################################################
	### Comando para mandar una solicitud de desbaneo ########
	##########################################################
	@commands.command(name="solicitar-desbaneo")
	@commands.dm_only()
	async def generateModal(self, ctx: commands.Context):
		print("Solicitando desbaneo")
		# TODO: Cambiar autor por Member
		button = OpenUnbanModal(ctx.author)
		await ctx.send(view=button)

async def setup(bot):
	await bot.add_cog(UnbanCommands(bot))
