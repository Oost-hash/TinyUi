"""Shared dataclasses for plugin manifests."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


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
    id:      str
    title:   str
    kind:    str        # "main" | "dialog"
    surface: Path
    chrome:  ChromePolicy = field(default_factory=ChromePolicy)


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
class PluginManifest:
    plugin_id:   str
    plugin_type: str                 # "host" | "plugin"
    windows:     list[AppManifest]
    menu:        list[MenuDecl]
