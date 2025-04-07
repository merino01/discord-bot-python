"""
Moderation commands
"""
from uuid import uuid4
from discord.ext import commands
from database.models import Trigger
from services import TriggersService
from tasks.automatic_messages import setup_automatic_messages

class TasksCommands(commands.Cog):
    """
    Moderation commands for the bot
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="reloadAutomaticMessages")
    @commands.is_owner()
    async def logs(self, ctx):
        """
        Command for reloading automatic messages
        """
        setup_automatic_messages(self.bot)
        await ctx.send("Mensajes automáticos reiniciados")

    @commands.command(name="add")
    @commands.is_owner()
    async def add(self, ctx):
        """
        Command for adding a message
        """
        TriggersService.add(Trigger(
            id=uuid4(),
            channel_id=ctx.channel.id,
            key="Hola",
            position="contains",
            response="Hola, soy un bot",
            response_timeout=10,
            delete_message=False
        ))
        await ctx.send("Trigger añadido")

async def setup(bot):
    """setup"""
    await bot.add_cog(TasksCommands(bot))
