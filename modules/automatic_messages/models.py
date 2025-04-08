"""Automatic message model for the database."""

from dataclasses import dataclass
from typing import Literal, Optional

@dataclass
class AutomaticMessage:
    """Dataclass representing an automatic message."""
    id: str
    channel_id: int
    text: str
    interval: Optional[int] = None
    interval_unit: Optional[Literal["seconds", "minutes", "hours"]] = None
    hour: Optional[int] = None
    minute: Optional[int] = None

    def __post_init__(self):
        """Post-initialization to validate the automatic message."""
        if not self.hour and not self.minute and not self.interval:
            self.interval = 10
        if self.interval and not self.interval_unit:
            self.interval_unit = "seconds"
        if self.hour and self.minute:
            self.interval = None

        if self.hour and self.hour < 0:
            self.hour = 0
        if self.hour and self.hour > 23:
            self.hour = 23
        if self.minute and self.minute < 0:
            self.minute = 0
        if self.minute and self.minute > 59:
            self.minute = 59
        if self.interval and self.interval < 1:
            self.interval = 1
