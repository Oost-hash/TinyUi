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

"""Runtime V2 path detection."""

from __future__ import annotations

import sys
from pathlib import Path

from runtimeV2.paths.contracts import RuntimePaths
from runtimeV2.paths.qml_source import QmlSource


def _core_qml_sources(source_root: Path | None) -> dict[str, QmlSource]:
    """Register core QML sources that support both dev and QRC modes.
    
    In dev mode: loads from filesystem for hot-reload.
    In frozen mode: loads from QRC (requires resources_rc import).
    """
    sources: dict[str, QmlSource] = {}
    
    # Core UI QML files
    if source_root is not None:
        ui_api_qml = source_root / "ui_api" / "qml"
        widget_api_qml = source_root / "widget_api" / "qml"
        
        sources["ui_api.HostedWindow"] = QmlSource.dual(
            ui_api_qml / "HostedWindow.qml",
            "/ui_api/qml/HostedWindow.qml",
        )
        sources["widget_api.WidgetWindow"] = QmlSource.dual(
            widget_api_qml / "WidgetWindow.qml",
            "/widget_api/qml/WidgetWindow.qml",
        )
        sources["widget_api.WidgetHost"] = QmlSource.dual(
            widget_api_qml / "WidgetHost.qml",
            "/widget_api/qml/WidgetHost.qml",
        )
        sources["widget_api.TextWidget"] = QmlSource.dual(
            widget_api_qml / "TextWidget.qml",
            "/widget_api/qml/TextWidget.qml",
        )
    else:
        # Frozen mode: only QRC paths available
        sources["ui_api.HostedWindow"] = QmlSource.qrc("/ui_api/qml/HostedWindow.qml")
        sources["widget_api.WidgetWindow"] = QmlSource.qrc("/widget_api/qml/WidgetWindow.qml")
        sources["widget_api.WidgetHost"] = QmlSource.qrc("/widget_api/qml/WidgetHost.qml")
        sources["widget_api.TextWidget"] = QmlSource.qrc("/widget_api/qml/TextWidget.qml")
    
    return sources


def detect_runtime_paths() -> RuntimePaths:
    """Detect runtime V2 app/resource paths."""

    if getattr(sys, "frozen", False):
        app_root = Path(sys.executable).resolve().parent
        meipass = getattr(sys, "_MEIPASS", None)
        frozen_root = Path(meipass).resolve() if isinstance(meipass, str) else app_root / "tinyui"
        runtime_paths = RuntimePaths(
            app_root=app_root,
            host_dir=frozen_root / "plugins" / "tinyui",
            plugins_dir=app_root / "plugins",
            source_root=None,
            frozen_root=frozen_root,
            qml_sources=_core_qml_sources(None),
        )
    else:
        source_root = Path(__file__).resolve().parents[2]
        runtime_paths = RuntimePaths(
            app_root=source_root,
            host_dir=source_root / "plugins" / "tinyui",
            plugins_dir=source_root / "plugins",
            source_root=source_root,
            frozen_root=None,
            qml_sources=_core_qml_sources(source_root),
        )

    return runtime_paths
