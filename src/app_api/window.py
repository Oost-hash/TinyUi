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

    # Extract chrome component override first (before iterating extra_properties)
    chrome_component = extra_properties.pop("chromeComponent", None)
    
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

    # Load custom chrome from manifest if specified and no override provided
    if chrome_component is None and manifest.chrome.custom_chrome:
        chrome_url = QUrl.fromLocalFile(str(manifest.chrome.custom_chrome))
        chrome_component = QQmlComponent(engine, chrome_url)
    
    # Apply custom chrome component if specified
    if chrome_component is not None:
        obj.setProperty("chromeComponent", chrome_component)

    attachment = attach_windowing(app=app, window=obj, theme=theme)
    if attachment.controller is not None:
        obj.setProperty("windowController", attachment.controller)

    keepalive = [component, *extra_properties.values(), *attachment.keepalive]
    if surface_component:
        keepalive.append(surface_component)
    if chrome_component:
        keepalive.append(chrome_component)
    return WindowHandle(qml_window=obj, keepalive=tuple(keepalive))

