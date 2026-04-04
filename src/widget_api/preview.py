"""Preview helpers for rendering widget_api widgets with static or connector-backed data."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import QTimer, QUrl
from PySide6.QtQml import QQmlComponent
from PySide6.QtQuick import QQuickWindow

from runtime.app.paths import AppPaths
from runtime.connectors.policy import required_connector_ids
from runtime.persistence import SettingsRegistry
from runtime.runtime import Runtime
from runtime_schema import EventBus
from ui_api.qt import create_engine

_QML_DIR = Path(__file__).resolve().parent / "qml"


def build_text_widget_preview_items() -> list[dict[str, Any]]:
    """Return simple preview widget data for the first renderer phase."""

    return [
        {
            "widgetId": "session_time_left",
            "label": "Time Left",
            "source": "session.time_left",
            "displayText": "120s",
            "textColor": "#E0E0E0",
            "backgroundColor": "#CC000000",
            "visible": True,
        },
        {
            "widgetId": "track_name",
            "label": "Track",
            "source": "track.name",
            "displayText": "Le Mans",
            "textColor": "#E0E0E0",
            "backgroundColor": "#CC000000",
            "visible": True,
        },
    ]


def project_overlay_preview_items(
    runtime: Runtime,
    *,
    plugin_id: str = "demo_overlay",
    connector_id: str | None = None,
) -> list[dict[str, Any]]:
    """Project overlay widget declarations into renderable preview items."""

    manifest = runtime.plugin_manifest(plugin_id)
    if manifest is None or manifest.overlay is None:
        raise ValueError(f"Overlay manifest '{plugin_id}' is unavailable")

    candidate_connector_ids = [connector_id] if connector_id else sorted(required_connector_ids(runtime._plugins, plugin_id))
    snapshot_map: dict[str, str] = {}
    resolved_connector_id: str | None = None
    for candidate in candidate_connector_ids:
        if candidate is None or not runtime.connector_services.has(candidate):
            continue
        runtime.connector_services.update(candidate)
        snapshot_map = dict(runtime.connector_services.inspect(candidate))
        resolved_connector_id = candidate
        break

    if resolved_connector_id is None:
        raise ValueError(f"No active connector service is available for overlay '{plugin_id}'")

    projected: list[dict[str, Any]] = []
    for widget in manifest.overlay.widgets:
        source = widget.bindings.get("source", "")
        projected.append(
            {
                "widgetId": widget.id,
                "label": widget.label or widget.id,
                "source": source,
                "displayText": snapshot_map.get(source, "<missing>"),
                "textColor": "#E0E0E0",
                "backgroundColor": "#CC000000",
                "visible": True,
                "connectorId": resolved_connector_id,
            }
        )
    return projected


def create_runtime_for_preview() -> Runtime:
    """Create a runtime booted far enough to drive connector-backed widget previews."""

    runtime = Runtime(EventBus())
    runtime.paths = AppPaths.detect()
    runtime.settings = SettingsRegistry(runtime.paths.config_dir)
    runtime._boot_runtime()
    runtime._apply_initial_runtime_state()
    return runtime


def create_preview_window(widgets: list[dict[str, Any]] | None = None) -> QQuickWindow:
    """Create a preview host window for widget_api rendering experiments."""

    engine = create_engine()
    component = QQmlComponent(engine, QUrl.fromLocalFile(str(_QML_DIR / "WidgetHost.qml")))
    obj = component.createWithInitialProperties(
        {
            "widgets": widgets if widgets is not None else build_text_widget_preview_items(),
        }
    )
    assert obj is not None, component.errorString()
    assert isinstance(obj, QQuickWindow), component.errorString()
    window = obj
    window.setProperty("_widgetApiKeepalive", (engine, component))
    return window


def create_connector_preview_window(
    *,
    plugin_id: str = "demo_overlay",
    connector_id: str | None = None,
    auto_refresh_ms: int = 250,
) -> QQuickWindow:
    """Create a preview host window backed by active connector snapshot data."""

    runtime = create_runtime_for_preview()
    runtime.set_active_plugin(plugin_id)
    widgets = project_overlay_preview_items(runtime, plugin_id=plugin_id, connector_id=connector_id)
    window = create_preview_window(widgets)

    timer = QTimer(window)
    timer.setInterval(auto_refresh_ms)

    def _refresh_widgets() -> None:
        window.setProperty(
            "widgets",
            project_overlay_preview_items(runtime, plugin_id=plugin_id, connector_id=connector_id),
        )

    timer.timeout.connect(_refresh_widgets)
    timer.start()

    keepalive = window.property("_widgetApiKeepalive")
    window.setProperty("_widgetApiKeepalive", (runtime, timer, keepalive))
    return window
