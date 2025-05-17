"""init for core module."""

from .logger import logger
from .utils import send_message_to_channel, send_message_to_admin, send_paginated_embeds

__all__ = [
    "logger",
    "send_message_to_channel",
    "send_message_to_admin",
    "send_paginated_embeds",
]
