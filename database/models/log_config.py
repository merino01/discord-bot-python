"""Database model for logs"""

from typing import Literal
from dataclasses import dataclass

LogConfigType = Literal["chat", "voice", "join_leave", "members"]

@dataclass
class LogConfig:
    """
    Represents a log in the database.
    """
    type: LogConfigType
    channel_id: int
    enabled: bool

    def __post_init__(self):
        """Convert enabled to boolean"""
        self.enabled = bool(self.enabled)
