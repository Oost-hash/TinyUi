"""Parser for plugin manifest.toml files."""

from __future__ import annotations

import tomllib
from pathlib import Path

from app_schema.manifest import (
    AppManifest, ChromePolicy,
    MenuItemDecl, MenuSeparatorDecl, MenuDecl,
    PluginManifest,
)


def load_plugin_manifest(path: Path) -> PluginManifest:
    with path.open("rb") as f:
        data = tomllib.load(f)

    manifest_dir = path.parent
    plugin = data.get("plugin", {})
    windows = [_parse_window(w, manifest_dir) for w in data.get("window", [])]
    menu    = [_parse_menu(m) for m in data.get("menu", [])]

    return PluginManifest(
        plugin_id=plugin.get("id", manifest_dir.name),
        plugin_type=plugin.get("type", "plugin"),
        windows=windows,
        menu=menu,
    )


def _parse_window(entry: dict, manifest_dir: Path) -> AppManifest:
    chrome_data = entry.get("chrome", {})
    chrome = ChromePolicy(
        show_menu_button=chrome_data.get("show_menu_button", True),
        show_title_text=chrome_data.get("show_title_text", True),
        show_caption_buttons=chrome_data.get("show_caption_buttons", True),
        show_tab_bar=chrome_data.get("show_tab_bar", False),
        show_status_bar=chrome_data.get("show_status_bar", False),
    )
    return AppManifest(
        id=entry["id"],
        title=entry.get("title", ""),
        kind=entry["kind"],
        surface=(manifest_dir / entry["surface"]).resolve(),
        chrome=chrome,
    )


def _parse_menu(entry: dict) -> MenuDecl:
    window = entry["window"]
    if entry.get("separator"):
        return MenuSeparatorDecl(window=window)
    return MenuItemDecl(
        window=window,
        label=entry["label"],
        action=entry["action"],
    )
