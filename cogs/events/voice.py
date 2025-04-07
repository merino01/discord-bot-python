"""
Voice events for the bot.
"""

from enum import Enum
from discord.ext import commands
from utils.channels import get_voicelog_channel, send_message_to_channel
from utils.embeds import (
    get_voice_state_join_embed,
    get_voice_state_leave_embed,
    get_voice_state_move_embed
)

class Actions(Enum):
    """
    Enum for voice actions.
    """
    JOINED = 0
    LEFT = 1
    MOVED = 2
    UNKNOWN = -1

class VoiceEvents(commands.Cog):
    """
    Base events for the bot.
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """
        Event when a user joins or leaves a voice channel.
        """
        channel_to_send = await get_voicelog_channel(self.bot)
        if not channel_to_send:
            return

        action = self.get_action(before, after)
        embed = None

        match action:
            case Actions.JOINED:
                embed = get_voice_state_join_embed(member, after)
            case Actions.LEFT:
                embed = get_voice_state_leave_embed(member, before)
            case Actions.MOVED:
                embed = get_voice_state_move_embed(member, before, after)
            case _:
                return
        if embed is None:
            return

        await send_message_to_channel(channel_to_send, embed=embed)


    def get_action(self, before, after):
        """
        Obtiene la acción realizada en el estado de voz.
        """
        if before.channel is None and after.channel is not None:
            return Actions.JOINED
        if before.channel is not None and after.channel is None:
            return Actions.LEFT
        if before.channel != after.channel:
            return Actions.MOVED
        return Actions.UNKNOWN

async def setup(bot):
    """setup"""
    await bot.add_cog(VoiceEvents(bot))
