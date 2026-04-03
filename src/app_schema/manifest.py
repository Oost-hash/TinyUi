"""Shared dataclasses for plugin manifests."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ChromePolicy:
    show_menu_button: bool = False
    show_title_text: bool = True
    show_caption_buttons: bool = True
    show_tab_bar: bool = False
    show_status_bar: bool = False
    custom_chrome: Path | None = None  # Path to custom chrome QML (relative to plugin root)

    def to_qml_dict(self) -> dict:
        return {
            "showMenuButton":     self.show_menu_button,
            "showTitleText":      self.show_title_text,
            "showCaptionButtons": self.show_caption_buttons,
            "showTabBar":         self.show_tab_bar,
            "showStatusBar":      self.show_status_bar,
        }


@dataclass(frozen=True)
class MenuItem:
    label:  str
    action: str


@dataclass(frozen=True)
class MenuSeparator:
    pass


@dataclass(frozen=True)
class StatusbarItemDecl:
    """Statusbar item declaration from manifest."""
    icon: str = ""       # Icon identifier (optional)
    text: str = ""       # Text to display (optional)
    tooltip: str = ""    # Hover tooltip
    action: str = ""     # Action to trigger
    side: str = "left"   # "left" or "right"


@dataclass(frozen=True)
class AppManifest:
    id:       str
    title:    str
    surface:  Path | None = None
    chrome:   ChromePolicy = field(default_factory=ChromePolicy)
    requires: list[str] = field(default_factory=list)  # capabilities: "inspector", ...
    menu:     list[MenuItem | MenuSeparator] = field(default_factory=list)
    statusbar: list[StatusbarItemDecl] = field(default_factory=list)


@dataclass(frozen=True)
class SettingDecl:
    key:     str
    label:   str
    default: Any
    type:    str                       # "bool" | "str" | "int" | "float" | "choice"
    choices: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class PluginInfo:
    plugin_id:     str
    plugin_type:   str
    version:       str
    author:        str
    description:   str
    icon_url:      str
    requires:      list[str]
    windows:       list[str]
    setting_count: int
    state:         str = "disabled"        # PluginState name
    state_history: list[dict] = field(default_factory=list)
    error_message: str | None = None


@dataclass(frozen=True)
class SettingInfo:
    namespace:     str
    key:           str
    type:          str
    current_value: str


@dataclass(frozen=True)
class DevToolsData:
    plugins:  list[PluginInfo]
    settings: list[SettingInfo]


@dataclass(frozen=True)
class TabDecl:
    """Tab declaration from manifest."""
    id: str
    label: str
    target: str          # target window ID (e.g., "tinyui.main")
    surface: Path
    plugin_id: str       # which plugin owns this tab


@dataclass(frozen=True)
class PluginManifest:
    plugin_id:   str
    plugin_type: str                 # "host" | "plugin" | "connector"
    version:     str
    author:      str
    description: str
    icon:        str
    requires:    list[str]
    windows:     list[AppManifest]
    settings:    list[SettingDecl]
    tabs:        list[TabDecl] = field(default_factory=list)
    plugin_menu: list[MenuItem | MenuSeparator] = field(default_factory=list)
    menu_label:  str | None = None
    connector_provides: list[str] = field(default_factory=list)
    provider_module: str | None = None
    provider_class: str | None = None
