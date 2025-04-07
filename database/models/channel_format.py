"""ChannelFormat Model"""

from uuid import UUID
from dataclasses import dataclass

@dataclass
class ChannelFormat:
    """
    Represents a channel format in the database.
    """
    id: UUID
    channel_id: int
    regex: str
