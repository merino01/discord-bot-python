"""Trigger model for the database."""

from typing import Literal, Optional
from dataclasses import dataclass
from uuid import UUID

TriggerTextPosition = Literal[
    "contains",
    "starts_with",
    "ends_with",
    "equal",
    "text_between",
    "regex"
]

@dataclass
class Trigger:
    """
    Represents a trigger in the database.
    """
    id: UUID
    channel_id: int
    delete_message: bool
    response: str
    key: str
    position: TriggerTextPosition
    response_timeout: Optional[int]

    def __post_init__(self):
        """
        Post-initialization processing.
        """
        self.delete_message = bool(self.delete_message)
