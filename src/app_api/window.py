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

    surface_url = QUrl.fromLocalFile(str(manifest.surface))
    surface_component = QQmlComponent(engine, surface_url)
    obj.setProperty("surfaceComponent", surface_component)

    attachment = attach_windowing(app=app, window=obj, theme=theme)
    if attachment.controller is not None:
        obj.setProperty("windowController", attachment.controller)

    return WindowHandle(qml_window=obj, keepalive=(component, surface_component, *attachment.keepalive))
