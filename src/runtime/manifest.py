"""Parser for plugin manifest.toml files."""

from __future__ import annotations

import tomllib
from pathlib import Path

from app_schema.connector import ConnectorGameDecl, ConnectorManifest, ConnectorServiceDecl
from app_schema.overlay import OverlayManifest, OverlayWidgetDecl
from app_schema.plugin import PluginManifest
from app_schema.ui import (
    AppManifest,
    ChromePolicy,
    MenuItem,
    MenuSeparator,
    SettingDecl,
    StatusbarItemDecl,
    TabDecl,
    UiManifest,
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
    ui_manifest = _parse_ui_manifest(
        windows=windows,
        tabs=tabs,
        plugin_menu=plugin_menu,
        menu_label=plugin.get("menu"),
    )
    connector_manifest = _parse_connector_manifest(data)
    overlay_manifest = _parse_overlay_manifest(data, plugin)

    manifest = PluginManifest(
        plugin_id=plugin_id,
        plugin_type=plugin.get("type", "plugin"),
        version=plugin.get("version", ""),
        author=plugin.get("author", ""),
        description=plugin.get("description", ""),
        icon=plugin.get("icon", ""),
        requires=list(plugin.get("requires", [])),
        settings=settings,
        ui=ui_manifest,
        connector=connector_manifest,
        overlay=overlay_manifest,
    )
    _validate_plugin_manifest(manifest)
    return manifest


def _validate_plugin_manifest(manifest: PluginManifest) -> None:
    windows = [] if manifest.ui is None else manifest.ui.windows
    tabs = [] if manifest.ui is None else manifest.ui.tabs
    plugin_menu = [] if manifest.ui is None else manifest.ui.plugin_menu
    if manifest.plugin_type == "host" and not windows:
        raise ValueError(f"Host plugin must declare at least one window (plugin: {manifest.plugin_id})")
    if manifest.plugin_type == "overlay":
        if windows or tabs or plugin_menu:
            raise ValueError(
                f"Overlay plugin cannot declare windows, tabs, or plugin menus (plugin: {manifest.plugin_id})"
            )
        if manifest.overlay is None or not manifest.overlay.widgets:
            raise ValueError(f"Overlay plugin must declare at least one widget (plugin: {manifest.plugin_id})")
        for widget in manifest.overlay.widgets:
            if not widget.widget:
                raise ValueError(f"Overlay widget must declare a widget type (plugin: {manifest.plugin_id}, widget: {widget.id})")


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


def _parse_ui_manifest(
    *,
    windows: list[AppManifest],
    tabs: list[TabDecl],
    plugin_menu: list[MenuItem | MenuSeparator],
    menu_label: str | None,
) -> UiManifest | None:
    if not windows and not tabs and not plugin_menu and menu_label is None:
        return None
    return UiManifest(
        windows=windows,
        tabs=tabs,
        plugin_menu=plugin_menu,
        menu_label=menu_label,
    )


def _parse_overlay_manifest(data: dict, plugin: dict) -> OverlayManifest | None:
    widget_entries = data.get("widget", [])
    connectors = list(plugin.get("overlay_connectors", data.get("overlay_connectors", [])))
    modules = list(plugin.get("overlay_modules", data.get("overlay_modules", [])))
    if not widget_entries and not connectors and not modules:
        return None
    return OverlayManifest(
        connectors=connectors,
        modules=modules,
        widgets=[
            OverlayWidgetDecl(
                id=entry["id"],
                widget=entry["widget"],
                label=entry.get("label", ""),
                bindings=dict(entry.get("bindings", {})),
            )
            for entry in widget_entries
        ],
    )


def _parse_connector_manifest(data: dict) -> ConnectorManifest | None:
    connector = data.get("connector", {})
    connector_service = data.get("connector_service", {})
    provides = list(connector.get("provides", []))
    games = _parse_connector_games(connector)
    service = _parse_connector_service(connector_service)
    if not provides and not games and service is None:
        return None
    return ConnectorManifest(
        provides=provides,
        games=games,
        service=service,
    )


def _parse_connector_games(connector: dict) -> list[ConnectorGameDecl]:
    game_entries = connector.get("game", [])
    return [
        ConnectorGameDecl(
            id=entry["id"],
            detect_names=list(entry.get("detect_names", [])),
        )
        for entry in game_entries
    ]


def _parse_connector_service(connector_service: dict) -> ConnectorServiceDecl | None:
    module = connector_service.get("module")
    class_name = connector_service.get("class")
    if not module or not class_name:
        return None
    return ConnectorServiceDecl(module=module, class_name=class_name)
