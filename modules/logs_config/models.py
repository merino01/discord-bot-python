"""Database model for logs"""

from typing import Literal, Optional
from dataclasses import dataclass

LogConfigType = Literal["chat", "voice", "join_leave", "members"]

@dataclass
class LogConfig:
    """Represents a log config in the database."""
    type: LogConfigType
    enabled: bool
    channel_id: Optional[int] = None

    def __post_init__(self):
        """Convert enabled to boolean"""
        self.enabled = bool(self.enabled)
