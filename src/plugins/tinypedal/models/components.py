# Auto-generated component classes

from dataclasses import dataclass, fields
from typing import Any, Dict

from .base import FlatMixin


@dataclass
class CaptionConfig(FlatMixin):
    """Caption component — combines caption cell + caption_text."""

    font_color: str = "#CCCCCC"
    bkg_color: str = "#777777"
    show: bool = True
    caption_text: str = ""


@dataclass
class WarningFlashConfig(FlatMixin):
    """Warning flash configuration."""

    enabled: bool = True
    color: str = "#FF2200"
    number_of_flashes: int = 10
    highlight_duration: float = 0.4
    interval: float = 0.2
