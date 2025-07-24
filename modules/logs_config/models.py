from typing import Literal, Optional
from dataclasses import dataclass

LogConfigType = Literal["chat", "voice", "join_leave", "members"]


@dataclass
class LogConfig:
    type: LogConfigType
    enabled: bool
    channel_id: Optional[int] = None

    def __post_init__(self):
        self.enabled = bool(self.enabled)
