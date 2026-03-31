"""Shared dataclasses for plugin manifests."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ChromePolicy:
    show_menu_button: bool = True
    show_title_text: bool = True
    show_caption_buttons: bool = True
    show_tab_bar: bool = False
    show_status_bar: bool = False

    def to_qml_dict(self) -> dict:
        return {
            "showMenuButton":     self.show_menu_button,
            "showTitleText":      self.show_title_text,
            "showCaptionButtons": self.show_caption_buttons,
            "showTabBar":         self.show_tab_bar,
            "showStatusBar":      self.show_status_bar,
        }


@dataclass(frozen=True)
class AppManifest:
    id:       str
    title:    str
    window_type: str                     # "main" | "dialog"
    surface:  Path
    chrome:   ChromePolicy = field(default_factory=ChromePolicy)
    requires: list[str] = field(default_factory=list)  # capabilities: "inspector", ...


@dataclass(frozen=True)
class MenuItemDecl:
    window: str
    label:  str
    action: str


@dataclass(frozen=True)
class MenuSeparatorDecl:
    window: str


MenuDecl = MenuItemDecl | MenuSeparatorDecl


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
    windows:       list[tuple[str, str]]   # [(id, window_type), ...]
    setting_count: int


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
class PluginManifest:
    plugin_id:   str
    plugin_type: str                 # "host" | "plugin"
    windows:     list[AppManifest]
    menu:        list[MenuDecl]
    settings:    list[SettingDecl]
