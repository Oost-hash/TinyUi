"""Parser for plugin manifest.toml files."""

from __future__ import annotations

import tomllib
from pathlib import Path

from app_schema.manifest import (
    AppManifest, ChromePolicy,
    MenuItem, MenuSeparator,
    SettingDecl,
    PluginManifest,
)


def _parse_menu_items(entries: list[dict]) -> list[MenuItem | MenuSeparator]:
    result: list[MenuItem | MenuSeparator] = []
    for m in entries:
        if m.get("separator"):
            result.append(MenuSeparator())
        else:
            result.append(MenuItem(label=m["label"], action=m["action"]))
    return result


def load_plugin_manifest(path: Path) -> PluginManifest:
    with path.open("rb") as f:
        data = tomllib.load(f)

    manifest_dir = path.parent
    plugin   = data.get("plugin", {})
    windows  = [_parse_window(w, manifest_dir) for w in data.get("window", [])]
    settings = [_parse_setting(s) for s in data.get("setting", [])]
    plugin_menu = []
    for pm in data.get("plugin_menu", []):
        plugin_menu.extend(_parse_menu_items(pm.get("items", [])))

    return PluginManifest(
        plugin_id=plugin.get("id", manifest_dir.name),
        plugin_type=plugin.get("type", "plugin"),
        windows=windows,
        settings=settings,
        plugin_menu=plugin_menu,
        menu_label=plugin.get("menu"),
    )


def _parse_window(entry: dict, manifest_dir: Path) -> AppManifest:
    chrome_data = entry.get("chrome", {})
    chrome = ChromePolicy(
        show_menu_button=chrome_data.get("show_menu_button", False),
        show_title_text=chrome_data.get("show_title_text", True),
        show_caption_buttons=chrome_data.get("show_caption_buttons", True),
        show_tab_bar=chrome_data.get("show_tab_bar", False),
        show_status_bar=chrome_data.get("show_status_bar", False),
    )
    menu = _parse_menu_items([m for m in entry.get("menu", [])])
    return AppManifest(
        id=entry["id"],
        title=entry.get("title", ""),
        window_type=entry["window_type"],
        surface=(manifest_dir / entry["surface"]).resolve() if "surface" in entry else None,
        chrome=chrome,
        requires=list(entry.get("requires", [])),
        menu=menu,
    )


def _parse_setting(entry: dict) -> SettingDecl:
    return SettingDecl(
        key=entry["key"],
        label=entry.get("label", entry["key"]),
        default=entry["default"],
        type=entry["type"],
        choices=list(entry.get("choices", [])),
    )
