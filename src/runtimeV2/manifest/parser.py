#  TinyUI
#  Copyright (C) 2026 Oost-hash
#
#  This file is part of TinyUI.
#
#  TinyUI is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  TinyUI is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  TinyUI builds on TinyPedal by s-victor (https://github.com/s-victor/TinyPedal),
#  licensed under GPLv3.

"""Parser for runtime V2 plugin manifest.toml files."""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import cast

from runtimeV2.connectors.schemas.manifest import (
    ConnectorGameDecl,
    ConnectorManifest,
    ConnectorRuntimeDecl,
    ConnectorServiceDecl,
)
from runtimeV2.persistence.manifest.settings import SettingDecl
from runtimeV2.plugins.schemas.manifest import ImageDecl, PluginManifest
from runtimeV2.ui.schemas.manifest import (
    AppManifest,
    ChromePolicy,
    MenuItem,
    MenuSeparator,
    StatusbarItemDecl,
    TabDecl,
    UiManifest,
)
from runtimeV2.widgets.schemas.manifest import OverlayManifest, OverlayWidgetDecl, WidgetDefaults


TomlTable = dict[str, object]


def _table(value: object) -> TomlTable:
    return cast(TomlTable, value) if isinstance(value, dict) else {}


def _tables(value: object) -> list[TomlTable]:
    if not isinstance(value, list):
        return []
    items = cast(list[object], value)
    return [cast(TomlTable, item) for item in items if isinstance(item, dict)]


def _string(value: object, default: str = "") -> str:
    return value if isinstance(value, str) else default


def _strings(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    items = cast(list[object], value)
    return [item for item in items if isinstance(item, str)]


def _bool(value: object, default: bool = False) -> bool:
    return value if isinstance(value, bool) else default


def _int(value: object, default: int = 0) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return default
    return default


def _object_map(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        return {}
    items = cast(TomlTable, value)
    return {str(key): item for key, item in items.items()}


def _string_map(value: object) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    items = cast(TomlTable, value)
    return {str(key): item for key, item in items.items() if isinstance(item, str)}


def _position(value: object) -> tuple[int, int]:
    if not isinstance(value, list):
        return (0, 0)
    items = cast(list[object], value)
    if len(items) < 2:
        return (0, 0)
    return (_int(items[0]), _int(items[1]))


def _resolve_path(manifest_dir: Path, value: object) -> Path | None:
    path = _string(value)
    return (manifest_dir / path).resolve() if path else None


def _parse_menu_items(entries: list[TomlTable]) -> list[MenuItem | MenuSeparator]:
    result: list[MenuItem | MenuSeparator] = []
    for item in entries:
        if _bool(item.get("separator")):
            result.append(MenuSeparator())
        else:
            result.append(MenuItem(label=_string(item.get("label")), action=_string(item.get("action"))))
    return result


def load_plugin_manifest(path: Path, *, resource_root: Path | None = None) -> PluginManifest:
    """Load a runtime V2 plugin manifest."""

    with path.open("rb") as file:
        data = cast(TomlTable, tomllib.load(file))

    manifest_dir = resource_root if resource_root is not None else path.parent
    plugin = _table(data.get("plugin"))
    plugin_id = _string(plugin.get("id"), manifest_dir.name)
    windows = [_parse_window(window, manifest_dir) for window in _tables(data.get("window"))]
    settings = [_parse_setting(setting) for setting in _tables(data.get("setting"))]
    tabs = [_parse_tab(tab, manifest_dir, plugin_id) for tab in _tables(data.get("tab"))]
    plugin_menu: list[MenuItem | MenuSeparator] = []
    for menu in _tables(data.get("plugin_menu")):
        plugin_menu.extend(_parse_menu_items(_tables(menu.get("items"))))
    ui_manifest = _parse_ui_manifest(
        windows=windows,
        tabs=tabs,
        plugin_menu=plugin_menu,
        menu_label=_string(plugin.get("menu")) or None,
    )
    images = [_parse_image(image) for image in _tables(data.get("image"))]
    manifest = PluginManifest(
        plugin_id=plugin_id,
        plugin_type=_string(plugin.get("type"), "plugin"),
        version=_string(plugin.get("version")),
        author=_string(plugin.get("author")),
        description=_string(plugin.get("description")),
        icon=_string(plugin.get("icon")),
        requires=_strings(plugin.get("requires")),
        url=_string(plugin.get("url")),
        sponsor=_string(plugin.get("sponsor"), _string(plugin.get("sponser"))),
        settings=settings,
        images=images,
        ui=ui_manifest,
        connector=_parse_connector_manifest(data),
        overlay=_parse_overlay_manifest(data, plugin, manifest_dir),
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
                raise ValueError(
                    f"Overlay widget must declare a widget type (plugin: {manifest.plugin_id}, widget: {widget.id})"
                )


def _parse_window(entry: TomlTable, manifest_dir: Path) -> AppManifest:
    chrome_data = _table(entry.get("chrome"))
    chrome = ChromePolicy(
        show_menu_button=_bool(chrome_data.get("show_menu_button"), False),
        show_title_text=_bool(chrome_data.get("show_title_text"), True),
        show_caption_buttons=_bool(chrome_data.get("show_caption_buttons"), True),
        show_tab_bar=_bool(chrome_data.get("show_tab_bar"), False),
        show_status_bar=_bool(chrome_data.get("show_status_bar"), False),
        custom_chrome=_resolve_path(manifest_dir, chrome_data.get("custom_chrome")),
    )
    return AppManifest(
        id=_string(entry.get("id")),
        title=_string(entry.get("title")),
        surface=_resolve_path(manifest_dir, entry.get("surface")),
        chrome=chrome,
        requires=_strings(entry.get("requires")),
        menu=_parse_menu_items(_tables(entry.get("menu"))),
        statusbar=[_parse_statusbar_item(item) for item in _tables(entry.get("statusbar"))],
    )


def _parse_setting(entry: TomlTable) -> SettingDecl:
    key = _string(entry.get("key"))
    return SettingDecl(
        key=key,
        label=_string(entry.get("label"), key),
        default=entry.get("default"),
        type=_string(entry.get("type")),
        choices=_strings(entry.get("choices")),
    )


def _parse_statusbar_item(entry: TomlTable) -> StatusbarItemDecl:
    return StatusbarItemDecl(
        icon=_string(entry.get("icon")),
        text=_string(entry.get("text")),
        tooltip=_string(entry.get("tooltip")),
        action=_string(entry.get("action")),
        side=_string(entry.get("side"), "left"),
    )


def _parse_tab(entry: TomlTable, manifest_dir: Path, plugin_id: str) -> TabDecl:
    return TabDecl(
        id=_string(entry.get("id")),
        label=_string(entry.get("label")),
        target=_string(entry.get("target")),
        surface=(manifest_dir / _string(entry.get("surface"))).resolve(),
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


def _parse_overlay_manifest(data: TomlTable, plugin: TomlTable, manifest_dir: Path) -> OverlayManifest | None:
    overlay_section = _table(data.get("overlay"))
    connectors = _strings(
        overlay_section.get(
            "connectors",
            plugin.get("overlay_connectors", data.get("overlay_connectors", [])),
        )
    )
    modules = _strings(
        overlay_section.get(
            "modules",
            plugin.get("overlay_modules", data.get("overlay_modules", [])),
        )
    )
    widgets_dir_name = _string(overlay_section.get("widgets_dir"))
    if widgets_dir_name:
        widgets = _load_widgets_from_dir(manifest_dir / widgets_dir_name)
    else:
        widgets = [
            OverlayWidgetDecl(
                id=_string(entry.get("id")),
                widget=_string(entry.get("widget")),
                label=_string(entry.get("label")),
                bindings=_string_map(entry.get("bindings")),
                values=_object_map(entry.get("values")),
            )
            for entry in _tables(data.get("widget"))
        ]

    if not widgets and not connectors and not modules:
        return None
    return OverlayManifest(
        connectors=connectors,
        modules=modules,
        widgets=widgets,
    )


def _load_widgets_from_dir(widgets_dir: Path) -> list[OverlayWidgetDecl]:
    if not widgets_dir.is_dir():
        return []
    declarations: list[OverlayWidgetDecl] = []
    for toml_file in sorted(widgets_dir.glob("*.toml")):
        with toml_file.open("rb") as file:
            data = cast(TomlTable, tomllib.load(file))
        widget = _table(data.get("widget"))
        defaults_data = _table(data.get("defaults"))
        values = _object_map(data.get("values"))
        if "format" in widget:
            values.setdefault("format", widget.get("format"))
        if "title" in widget:
            values.setdefault("title", widget.get("title"))
        if "description" in widget:
            values.setdefault("description", widget.get("description"))
        if "thresholds" in data:
            values.setdefault("thresholds", data.get("thresholds"))
        declarations.append(OverlayWidgetDecl(
            id=_string(widget.get("id")),
            widget=_string(widget.get("widget")),
            label=_string(widget.get("label")),
            bindings=_string_map(data.get("bindings")),
            values=values,
            defaults=WidgetDefaults(
                enabled=_bool(defaults_data.get("enabled"), True),
                visible=_bool(defaults_data.get("visible"), True),
                position=_position(defaults_data.get("position")),
            ),
        ))
    return declarations


def _parse_image(entry: TomlTable) -> ImageDecl:
    return ImageDecl(
        id=_string(entry.get("id")),
        path=_string(entry.get("path")),
    )


def _parse_connector_manifest(data: TomlTable) -> ConnectorManifest | None:
    connector = _table(data.get("connector"))
    connector_service = _table(data.get("connector_service"))
    connector_runtime = _table(data.get("connector_runtime"))
    provides = _strings(connector.get("provides"))
    games = _parse_connector_games(connector)
    service = _parse_connector_service(connector_service)
    runtime = _parse_connector_runtime(connector_runtime)
    if not provides and not games and service is None and runtime is None:
        return None
    return ConnectorManifest(
        provides=provides,
        games=games,
        service=service,
        runtime=runtime,
    )


def _parse_connector_games(connector: TomlTable) -> list[ConnectorGameDecl]:
    return [
        ConnectorGameDecl(
            id=_string(entry.get("id")),
            detect_names=_strings(entry.get("detect_names")),
        )
        for entry in _tables(connector.get("game"))
    ]


def _parse_connector_service(connector_service: TomlTable) -> ConnectorServiceDecl | None:
    module = _string(connector_service.get("module"))
    class_name = _string(connector_service.get("class"))
    if not module or not class_name:
        return None
    return ConnectorServiceDecl(module=module, class_name=class_name)


def _parse_connector_runtime(connector_runtime: TomlTable) -> ConnectorRuntimeDecl | None:
    game_state_hook = connector_runtime.get("game_state_hook")
    mock_source = connector_runtime.get("mock_source")
    if not game_state_hook and not mock_source:
        return None
    return ConnectorRuntimeDecl(
        game_state_hook=str(game_state_hook or ""),
        mock_source=str(mock_source or ""),
    )
