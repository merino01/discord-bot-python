"""ChannelFormat Model"""
from dataclasses import dataclass

@dataclass
class ChannelFormat:
    """Represents a channel format in the database"""
    id: str
    channel_id: int
    regex: str
