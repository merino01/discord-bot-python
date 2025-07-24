from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
from datetime import datetime


class ChannelType(Enum):
    TEXT = "text"
    VOICE = "voice"


class ClanMemberRole(Enum):
    LEADER = "leader"
    MEMBER = "member"


@dataclass
class ClanChannel:
    channel_id: int
    type: str
    name: str
    clan_id: str
    created_at: datetime


@dataclass
class ClanMember:
    user_id: int
    clan_id: str
    joined_at: datetime
    role: str = ClanMemberRole.MEMBER.value


@dataclass
class Clan:
    id: str
    name: str
    role_id: int
    created_at: datetime
    member_count: int
    max_members: int
    deleted: bool = False
    deleted_at: Optional[datetime] = None


@dataclass
class FullClan(Clan):
    members: list[ClanMember] = field(default_factory=list)
    channels: list[ClanChannel] = field(default_factory=list)
