from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional
import json

DEFAULT_CLAN_SETTINGS = {
    "text_category_id": None,
    "voice_category_id": None,
    "max_text_channels": 1,
    "max_voice_channels": 1,
    "default_role_color": "000000",
    "leader_role_id": None,
    "additional_roles": [],
    "max_members": 50,
    "allow_multiple_clans": False,
    "allow_multiple_leaders": True,
}


@dataclass
class ClanSetting:
    key: str
    value: str
    description: Optional[str] = None
    updated_at: Optional[datetime] = None


@dataclass
class ClanSettings:
    text_category_id: Optional[int]
    voice_category_id: Optional[int]
    max_text_channels: int
    max_voice_channels: int

    default_role_color: str
    leader_role_id: Optional[int]
    additional_roles: List[int]

    max_members: int
    allow_multiple_clans: bool
    allow_multiple_leaders: bool

    @classmethod
    def get_default(cls) -> 'ClanSettings':
        return cls(**DEFAULT_CLAN_SETTINGS)

    def to_dict(self) -> dict:
        return {
            'text_category_id': str(self.text_category_id or 0),
            'voice_category_id': str(self.voice_category_id or 0),
            'max_text_channels': str(self.max_text_channels),
            'max_voice_channels': str(self.max_voice_channels),
            'default_role_color': self.default_role_color,
            'leader_role_id': str(self.leader_role_id or 0),
            'additional_roles': json.dumps(self.additional_roles or []),
            'max_members': str(self.max_members),
            'allow_multiple_clans': 'true' if self.allow_multiple_clans else 'false',
            'allow_multiple_leaders': 'true' if self.allow_multiple_leaders else 'false',
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ClanSettings':
        return cls(
            text_category_id=int(data.get('text_category_id', 0)) or None,
            voice_category_id=int(data.get('voice_category_id', 0)) or None,
            max_text_channels=int(
                data.get('max_text_channels', DEFAULT_CLAN_SETTINGS['max_text_channels'])
            ),
            max_voice_channels=int(
                data.get('max_voice_channels', DEFAULT_CLAN_SETTINGS['max_voice_channels'])
            ),
            default_role_color=data.get(
                'default_role_color', DEFAULT_CLAN_SETTINGS['default_role_color']
            ),
            leader_role_id=int(data.get('leader_role_id', 0)) or None,
            additional_roles=json.loads(data.get('additional_roles', '[]')),
            max_members=int(data.get('max_members', DEFAULT_CLAN_SETTINGS['max_members'])),
            allow_multiple_clans=data.get('allow_multiple_clans', 'false') == 'true',
            allow_multiple_leaders=data.get('allow_multiple_leaders', 'false') == 'true',
        )
