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

"""Opens a hosted window for an AppManifest."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import cast

from PySide6.QtCore import QObject, QUrl
from PySide6.QtQml import QQmlComponent, QQmlEngine
from PySide6.QtQuick import QQuickWindow

from ui_api.api.app_actions import AppActions
from ui_api.startup_logging import log_startup_step
from ui_api.theme import Theme
from runtimeV2.ui.schemas.manifest import AppManifest
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
    log_startup_step(f"opening hosted window: {manifest.id}")
    url = QUrl.fromLocalFile(str(_HOSTED_WINDOW_QML))
    component = QQmlComponent(engine, url)
    obj = component.create()
    if obj is None:
        error_message = component.errorString()
        log_startup_step(
            f"hosted window root failed for {manifest.id}: {error_message}",
            level=40,
        )
        raise RuntimeError(error_message)
    if not isinstance(obj, QQuickWindow):
        error_message = component.errorString() or f"Expected QQuickWindow, got {type(obj).__name__}"
        log_startup_step(
            f"hosted window type failed for {manifest.id}: {error_message}",
            level=40,
        )
        raise TypeError(error_message)
    window = cast(QQuickWindow, obj)

    # Extract chrome component override first (before iterating extra_properties)
    chrome_component = extra_properties.pop("chromeComponent", None)
    
    window.setProperty("appActions", actions)
    window.setProperty("theme", theme)
    window.setProperty("windowId", manifest.id)
    window.setProperty("windowTitle", manifest.title)
    window.setProperty("showTabBar", manifest.chrome.show_tab_bar)
    window.setProperty("showStatusBar", manifest.chrome.show_status_bar)
    window.setProperty("chromePolicy", manifest.chrome.to_qml_dict())

    for key, value in extra_properties.items():
        window.setProperty(key, value)

    surface_component = None
    if manifest.surface:
        surface_url = QUrl.fromLocalFile(str(manifest.surface))
        log_startup_step(f"loading surface for {manifest.id}: {manifest.surface}")
        surface_component = QQmlComponent(engine, surface_url)
        window.setProperty("surfaceComponent", surface_component)

    # Load custom chrome from manifest if specified and no override provided
    if chrome_component is None and manifest.chrome.custom_chrome:
        chrome_url = QUrl.fromLocalFile(str(manifest.chrome.custom_chrome))
        log_startup_step(f"loading custom chrome for {manifest.id}: {manifest.chrome.custom_chrome}")
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
    log_startup_step(f"hosted window ready: {manifest.id}")
    return WindowHandle(qml_window=window, keepalive=tuple(keepalive))

