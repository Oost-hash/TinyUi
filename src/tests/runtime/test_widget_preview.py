from __future__ import annotations

import importlib
from pathlib import Path
import re
import sys

from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlComponent
from PySide6.QtQuick import QQuickWindow

from runtime.app.paths import AppPaths
from runtime.connectors import register_connector_service
from runtime.runtime import Runtime
from runtime_schema import EventBus
from tests.conftest import create_test_runtime_with_paths
from runtime.widgets import WidgetRuntimeRecord, WidgetRuntimeStatus
from ui_api.qt import create_engine
from widget_api.preview import build_text_widget_preview_items, create_preview_window, project_overlay_preview_items
from widget_api.window_host import WidgetWindowHost


def _clear_preview_test_modules() -> None:
    for name in list(sys.modules):
        if name == "plugins" or name.startswith("plugins."):
            sys.modules.pop(name, None)
    importlib.invalidate_caches()


def test_text_widget_component_loads(qtbot) -> None:
    engine = create_engine()
    qml_path = Path(__file__).resolve().parents[2] / "widget_api" / "qml" / "TextWidget.qml"
    component = QQmlComponent(engine, QUrl.fromLocalFile(str(qml_path)))

    obj = component.createWithInitialProperties(
        {
            "widgetData": {
                "label": "Time Left",
                "source": "session.time_left",
                "displayText": "120s",
                "visible": True,
            }
        }
    )

    assert obj is not None, component.errorString()
    assert obj.property("labelText") == "Time Left"
    assert obj.property("displayText") == "120s"
    assert obj.property("sourceText") == "session.time_left"
    obj.deleteLater()


def test_widget_preview_host_window_loads(qtbot) -> None:
    window = create_preview_window(build_text_widget_preview_items())

    assert isinstance(window, QQuickWindow)
    assert window.property("widgetCount") == 2
    window.close()


def test_project_overlay_preview_items_reads_connector_snapshot(tmp_path: Path) -> None:
    _clear_preview_test_modules()
    source_root = tmp_path / "src"
    plugins_dir = source_root / "plugins"
    config_dir = tmp_path / "config"
    data_dir = tmp_path / "data"

    (plugins_dir / "tinyui").mkdir(parents=True)
    (plugins_dir / "__init__.py").write_text("", encoding="utf-8")
    (plugins_dir / "tinyui" / "plugin.py").write_text("def activate(ctx):\n    return None\n", encoding="utf-8")
    (plugins_dir / "tinyui" / "manifest.toml").write_text(
        "\n".join(
            [
                "[plugin]",
                'id = "tinyui"',
                'type = "host"',
                'version = "1.0.0"',
                'author = "Test"',
                'description = "host"',
                "",
                "[[window]]",
                'id = "tinyui.main"',
                'title = "TinyUi"',
                'surface = "app_main/qml/surface.qml"',
                "",
            ]
        ),
        encoding="utf-8",
    )

    (plugins_dir / "preview_connector").mkdir(parents=True)
    (plugins_dir / "preview_connector" / "__init__.py").write_text("", encoding="utf-8")
    (plugins_dir / "preview_connector" / "plugin.py").write_text(
        "\n".join(
            [
                "class PreviewConnector:",
                "    def __init__(self):",
                "        self._time_left = 98.0",
                "",
                "    def update(self):",
                "        self._time_left -= 1.0",
                "",
                "    def inspect_snapshot(self):",
                "        return [",
                "            (\"session.time_left\", f\"{self._time_left:.1f} s\"),",
                "            ('track.name', 'Spa'),",
                "        ]",
                "",
                "def activate(ctx):",
                "    return None",
                "",
                "def deactivate(ctx):",
                "    return None",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (plugins_dir / "preview_connector" / "manifest.toml").write_text(
        "\n".join(
            [
                "[plugin]",
                'id = "preview_connector"',
                'type = "connector"',
                'version = "1.0.0"',
                'author = "Test"',
                'description = "connector"',
                "",
                "[connector_service]",
                'module = "plugins.preview_connector.plugin"',
                'class = "PreviewConnector"',
                "",
            ]
        ),
        encoding="utf-8",
    )

    (plugins_dir / "demo_overlay").mkdir(parents=True)
    (plugins_dir / "demo_overlay" / "__init__.py").write_text("", encoding="utf-8")
    (plugins_dir / "demo_overlay" / "manifest.toml").write_text(
        "\n".join(
            [
                "[plugin]",
                'id = "demo_overlay"',
                'type = "overlay"',
                'version = "1.0.0"',
                'author = "Test"',
                'description = "overlay"',
                'requires = ["preview_connector"]',
                "",
                "[[widget]]",
                'id = "session_time_left"',
                'widget = "textWidget"',
                'label = "Time Left"',
                'bindings = { source = "session.time_left" }',
                "",
                "[[widget]]",
                'id = "track_name"',
                'widget = "textWidget"',
                'label = "Track"',
                'bindings = { source = "track.name" }',
                "",
            ]
        ),
        encoding="utf-8",
    )

    paths = AppPaths(
        app_root=source_root,
        config_dir=config_dir,
        host_dir=plugins_dir / "tinyui",
        plugins_dir=plugins_dir,
        data_dir=data_dir,
        source_root=source_root,
        frozen_root=None,
    )
    config_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    runtime = create_test_runtime_with_paths(paths)
    runtime._boot_runtime()
    runtime._apply_initial_runtime_state()
    if str(source_root) not in sys.path:
        sys.path.insert(0, str(source_root))
    importlib.invalidate_caches()
    register_connector_service(
        plugins=runtime._plugins,
        connector_services=runtime.connector_services,
        events=runtime.events,
        plugin_id="preview_connector",
    )

    items = project_overlay_preview_items(runtime, plugin_id="demo_overlay")
    updated_items = project_overlay_preview_items(runtime, plugin_id="demo_overlay")

    first_time_left = _extract_seconds(items[0]["displayText"])
    second_time_left = _extract_seconds(updated_items[0]["displayText"])

    assert first_time_left is not None
    assert second_time_left is not None
    assert first_time_left - second_time_left == 1.0
    assert items[1]["displayText"] == "Spa"
    assert updated_items[1]["displayText"] == "Spa"
    assert [item["source"] for item in items] == ["session.time_left", "track.name"]


def _extract_seconds(value: str) -> float | None:
    match = re.search(r"(\d+(?:\.\d+)?)", value)
    return float(match.group(1)) if match else None


def test_widget_window_host_opens_window_for_ready_record(qtbot) -> None:
    host = WidgetWindowHost()

    host.sync_records(
        [
            WidgetRuntimeRecord(
                overlay_id="demo_overlay",
                widget_id="session_time_left",
                widget_type="textWidget",
                label="Time Left",
                source="session.time_left",
                status=WidgetRuntimeStatus.READY,
                connector_ids=("LMU_RF2_Connector",),
            )
        ]
    )

    windows = host.windows()
    assert len(windows) == 1
    assert isinstance(windows[0], QQuickWindow)
    assert windows[0].property("widgetData")["widgetId"] == "session_time_left"
    host.close_all()


def test_widget_window_host_ignores_non_renderable_records(qtbot) -> None:
    host = WidgetWindowHost()

    host.sync_records(
        [
            WidgetRuntimeRecord(
                overlay_id="demo_overlay",
                widget_id="session_time_left",
                widget_type="textWidget",
                label="Time Left",
                source="session.time_left",
                status=WidgetRuntimeStatus.WAITING_FOR_CONNECTOR,
                connector_ids=("LMU_RF2_Connector",),
            )
        ]
    )

    assert host.windows() == ()
    host.close_all()
