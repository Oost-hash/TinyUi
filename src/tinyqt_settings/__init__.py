"""Settings feature package for TinyQt-hosted settings surfaces."""

from .actions import build_settings_button_actions
from .window import NativeSettingsWindow

__all__ = ["NativeSettingsWindow", "build_settings_button_actions"]
