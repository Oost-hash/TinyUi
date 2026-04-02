"""Opens a hosted window for an AppManifest."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlComponent, QQmlEngine
from PySide6.QtQuick import QQuickWindow

from app_api.host_actions import HostActions
from app_api.theme import Theme
from app_schema.manifest import AppManifest
from app_api.windowing import attach_windowing


_HOSTED_WINDOW_QML = Path(__file__).parent / "qml" / "HostedWindow.qml"


@dataclass
class WindowHandle:
    qml_window: QQuickWindow
    keepalive: tuple[object, ...]


def open_window(
    manifest: AppManifest,
    *,
    engine: QQmlEngine,
    app,
    actions: HostActions,
    theme: Theme,
    **extra_properties: object,
) -> WindowHandle:
    url = QUrl.fromLocalFile(str(_HOSTED_WINDOW_QML))
    component = QQmlComponent(engine, url)
    obj = component.create()
    assert obj is not None, component.errorString()

    obj.setProperty("hostActions", actions)
    obj.setProperty("theme", theme)
    obj.setProperty("windowTitle", manifest.title)
    obj.setProperty("showTabBar", manifest.chrome.show_tab_bar)
    obj.setProperty("showStatusBar", manifest.chrome.show_status_bar)
    obj.setProperty("chromePolicy", manifest.chrome.to_qml_dict())

    for key, value in extra_properties.items():
        obj.setProperty(key, value)

    surface_component = None
    if manifest.surface:
        surface_url = QUrl.fromLocalFile(str(manifest.surface))
        surface_component = QQmlComponent(engine, surface_url)
        obj.setProperty("surfaceComponent", surface_component)

    # Load plugin panel component for main window
    plugin_panel_component = None
    if manifest.window_type == "main":
        plugin_panel_path = Path(__file__).parent.parent / "plugins" / "tinyui" / "app_pluginsPanel" / "qml" / "surface.qml"
        if plugin_panel_path.exists():
            panel_url = QUrl.fromLocalFile(str(plugin_panel_path))
            plugin_panel_component = QQmlComponent(engine, panel_url)
            obj.setProperty("pluginPanelComponent", plugin_panel_component)

    attachment = attach_windowing(app=app, window=obj, theme=theme)
    if attachment.controller is not None:
        obj.setProperty("windowController", attachment.controller)

    keepalive = [component, *extra_properties.values(), *attachment.keepalive]
    if surface_component:
        keepalive.append(surface_component)
    if plugin_panel_component:
        keepalive.append(plugin_panel_component)
    return WindowHandle(qml_window=obj, keepalive=tuple(keepalive))
