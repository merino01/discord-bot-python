"""clans/models.py"""

from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class ChannelType(Enum):
    """Enum representing different types of channels."""
    TEXT = 'text'
    VOICE = 'voice'

class ClanMemberRole(Enum):
    """Enum representing different roles in a clan."""
    LEADER = 'leader'
    MEMBER = 'member'

@dataclass
class ClanChannel:
    """
    Represents a clan channel.
    """
    channel_id: int
    type: str
    name: str
    clan_id: str
    created_at: datetime

@dataclass
class ClanMember:
    """
    Represents a member of a clan.
    """
    user_id: int
    clan_id: str
    joined_at: datetime
    role: str = ClanMemberRole.MEMBER.value

@dataclass
class Clan:
    """
    Represents a clan.
    """
    id: str
    name: str
    role_id: int
    created_at: datetime
    member_count: int
    max_members: int

@dataclass
class FullClan:
    """
    Represents a clan with its members and channels.
    """
    clan: Clan
    members: list[ClanMember]
    channels: list[ClanChannel]
