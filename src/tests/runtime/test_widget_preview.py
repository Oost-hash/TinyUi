from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlComponent
from PySide6.QtQuick import QQuickWindow

from runtime_host.capabilities.widget_host import WidgetHostCapability
from runtimeV2.widgets.capabilities.widget_records_read import WidgetRecordsRead
from runtimeV2.widgets.contracts import WidgetRecord, WidgetStatus
from runtimeV2.widgets.store import WidgetRecordsStore
from ui_api.qt import create_engine
from widget_api.preview import build_text_widget_preview_items, create_preview_window
from widget_api.window_host import WidgetWindowHost


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


def test_widget_window_host_opens_window_for_ready_record(qtbot) -> None:
    from types import SimpleNamespace
    store = WidgetRecordsStore()
    host = WidgetWindowHost(WidgetHostCapability(WidgetRecordsRead(store)), SimpleNamespace())

    host.sync_records([
        WidgetRecord(
            overlay_id="demo_overlay",
            widget_id="session_time_left",
            widget_type="textWidget",
            label="Time Left",
            source="session.time_left",
            bindings={"source": "session.time_left"},
            status=WidgetStatus.READY,
            connector_ids=("LMU_RF2_Connector",),
        )
    ])

    windows = host.windows()
    assert len(windows) == 1
    assert isinstance(windows[0], QQuickWindow)
    assert windows[0].property("widgetData")["widgetId"] == "session_time_left"
    host.close_all()


def test_widget_window_host_opens_window_for_waiting_connector_record(qtbot) -> None:
    from types import SimpleNamespace
    store = WidgetRecordsStore()
    host = WidgetWindowHost(WidgetHostCapability(WidgetRecordsRead(store)), SimpleNamespace())

    host.sync_records([
        WidgetRecord(
            overlay_id="demo_overlay",
            widget_id="session_time_left",
            widget_type="textWidget",
            label="Time Left",
            source="session.time_left",
            bindings={"source": "session.time_left"},
            status=WidgetStatus.WAITING_FOR_CONNECTOR,
            connector_ids=("LMU_RF2_Connector",),
        )
    ])

    windows = host.windows()
    assert len(windows) == 1
    assert isinstance(windows[0], QQuickWindow)
    assert windows[0].property("widgetData")["displayText"] == "Waiting for connector"
    host.close_all()
