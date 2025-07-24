from typing import Literal, Optional
from enum import Enum
from dataclasses import dataclass

TriggerTextPosition = Literal[
    "contains", "starts_with", "ends_with", "equal", "text_between", "regex"
]


@dataclass
class Trigger:
    id: str
    channel_id: int
    delete_message: bool
    response: Optional[str]
    key: str
    position: TriggerTextPosition
    response_timeout: Optional[int]

    def __post_init__(self):
        self.delete_message = bool(self.delete_message)
        self.response_timeout = int(self.response_timeout) if self.response_timeout else None
        self.response_timeout = min(self.response_timeout, 60) if self.response_timeout else None
        self.response_timeout = max(self.response_timeout, 1) if self.response_timeout else None


class TriggerPosition(Enum):
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    EXACT_MATCH = "equal"
    TEXT_BETWEEN = "text_between"
    REGEX = "regex"
