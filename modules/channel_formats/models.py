from dataclasses import dataclass


@dataclass
class ChannelFormat:
    id: str
    channel_id: int
    regex: str
