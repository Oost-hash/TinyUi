"""Parser for plugin manifest.toml files."""

from __future__ import annotations

import tomllib
from pathlib import Path

from app_schema.manifest import (
    AppManifest, ChromePolicy,
    MenuItem, MenuSeparator,
    SettingDecl, StatusbarItemDecl,
    TabDecl, PluginManifest,
)


def _parse_menu_items(entries: list[dict]) -> list[MenuItem | MenuSeparator]:
    result: list[MenuItem | MenuSeparator] = []
    for m in entries:
        if m.get("separator"):
            result.append(MenuSeparator())
        else:
            result.append(MenuItem(label=m["label"], action=m["action"]))
    return result


def load_plugin_manifest(path: Path, *, resource_root: Path | None = None) -> PluginManifest:
    with path.open("rb") as f:
        data = tomllib.load(f)

    manifest_dir = resource_root if resource_root is not None else path.parent
    plugin   = data.get("plugin", {})
    plugin_id = plugin.get("id", manifest_dir.name)
    windows  = [_parse_window(w, manifest_dir) for w in data.get("window", [])]
    settings = [_parse_setting(s) for s in data.get("setting", [])]
    tabs = [_parse_tab(t, manifest_dir, plugin_id) for t in data.get("tab", [])]
    plugin_menu = []
    for pm in data.get("plugin_menu", []):
        plugin_menu.extend(_parse_menu_items(pm.get("items", [])))
    connector = data.get("connector", {})
    connector_service = data.get("connector_service", {})

    manifest = PluginManifest(
        plugin_id=plugin_id,
        plugin_type=plugin.get("type", "plugin"),
        version=plugin.get("version", ""),
        author=plugin.get("author", ""),
        description=plugin.get("description", ""),
        icon=plugin.get("icon", ""),
        requires=list(plugin.get("requires", [])),
        windows=windows,
        settings=settings,
        tabs=tabs,
        plugin_menu=plugin_menu,
        menu_label=plugin.get("menu"),
        connector_provides=list(connector.get("provides", [])),
        connector_service_module=connector_service.get("module"),
        connector_service_class=connector_service.get("class"),
    )
    _validate_plugin_manifest(manifest)
    return manifest


def _validate_plugin_manifest(manifest: PluginManifest) -> None:
    if manifest.plugin_type == "host" and not manifest.windows:
        raise ValueError(f"Host plugin must declare at least one window (plugin: {manifest.plugin_id})")


def _parse_window(entry: dict, manifest_dir: Path) -> AppManifest:
    chrome_data = entry.get("chrome", {})
    chrome_qml = chrome_data.get("custom_chrome")
    chrome = ChromePolicy(
        show_menu_button=chrome_data.get("show_menu_button", False),
        show_title_text=chrome_data.get("show_title_text", True),
        show_caption_buttons=chrome_data.get("show_caption_buttons", True),
        show_tab_bar=chrome_data.get("show_tab_bar", False),
        show_status_bar=chrome_data.get("show_status_bar", False),
        custom_chrome=(manifest_dir / chrome_qml).resolve() if chrome_qml else None,
    )
    menu = _parse_menu_items([m for m in entry.get("menu", [])])
    # Parse statusbar items for this window
    statusbar = [_parse_statusbar_item(sb) for sb in entry.get("statusbar", [])]

    return AppManifest(
        id=entry["id"],
        title=entry.get("title", ""),
        surface=(manifest_dir / entry["surface"]).resolve() if "surface" in entry else None,
        chrome=chrome,
        requires=list(entry.get("requires", [])),
        menu=menu,
        statusbar=statusbar,
    )


def _parse_setting(entry: dict) -> SettingDecl:
    return SettingDecl(
        key=entry["key"],
        label=entry.get("label", entry["key"]),
        default=entry["default"],
        type=entry["type"],
        choices=list(entry.get("choices", [])),
    )


def _parse_statusbar_item(entry: dict) -> StatusbarItemDecl:
    return StatusbarItemDecl(
        icon=entry.get("icon", ""),
        text=entry.get("text", ""),
        tooltip=entry.get("tooltip", ""),
        action=entry.get("action", ""),
        side=entry.get("side", "left"),
    )


def _parse_tab(entry: dict, manifest_dir: Path, plugin_id: str) -> TabDecl:
    return TabDecl(
        id=entry["id"],
        label=entry["label"],
        target=entry["target"],
        surface=(manifest_dir / entry["surface"]).resolve(),
        plugin_id=plugin_id,
    )
