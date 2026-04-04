"""Opens a hosted window for an AppManifest."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import cast

from PySide6.QtCore import QObject, QUrl
from PySide6.QtQml import QQmlComponent, QQmlEngine
from PySide6.QtQuick import QQuickWindow

from ui_api.api.app_actions import AppActions
from ui_api.theme import Theme
from app_schema.manifest import AppManifest
from ui_api.windowing import attach_windowing


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
    actions: AppActions,
    theme: Theme,
    **extra_properties: object,
) -> WindowHandle:
    url = QUrl.fromLocalFile(str(_HOSTED_WINDOW_QML))
    component = QQmlComponent(engine, url)
    obj = component.create()
    assert obj is not None, component.errorString()
    assert isinstance(obj, QQuickWindow), component.errorString()
    window = cast(QQuickWindow, obj)

    # Extract chrome component override first (before iterating extra_properties)
    chrome_component = extra_properties.pop("chromeComponent", None)
    
    window.setProperty("appActions", actions)
    window.setProperty("theme", theme)
    window.setProperty("windowTitle", manifest.title)
    window.setProperty("showTabBar", manifest.chrome.show_tab_bar)
    window.setProperty("showStatusBar", manifest.chrome.show_status_bar)
    window.setProperty("chromePolicy", manifest.chrome.to_qml_dict())

    for key, value in extra_properties.items():
        window.setProperty(key, value)

    surface_component = None
    if manifest.surface:
        surface_url = QUrl.fromLocalFile(str(manifest.surface))
        surface_component = QQmlComponent(engine, surface_url)
        window.setProperty("surfaceComponent", surface_component)

    # Load custom chrome from manifest if specified and no override provided
    if chrome_component is None and manifest.chrome.custom_chrome:
        chrome_url = QUrl.fromLocalFile(str(manifest.chrome.custom_chrome))
        chrome_component = QQmlComponent(engine, chrome_url)
    
    # Apply custom chrome component if specified
    if chrome_component is not None:
        window.setProperty("chromeComponent", chrome_component)

    attachment = attach_windowing(app=app, window=window, theme=theme)
    if attachment.controller is not None:
        window.setProperty("windowController", attachment.controller)

    keepalive = [component, *extra_properties.values(), *attachment.keepalive]
    if surface_component:
        keepalive.append(surface_component)
    if chrome_component:
        keepalive.append(chrome_component)
    return WindowHandle(qml_window=window, keepalive=tuple(keepalive))

