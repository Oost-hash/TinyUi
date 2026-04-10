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

"""QML-facing ui_api capabilities above runtimeV2."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QObject, Property, Signal, Slot

from shared_runtime_host.capabilities.ui_host import UIHostCapability
from shared_runtime_host.capabilities.window_host import WindowHostCapability
from shared_runtime_host.capabilities.widget_host import WidgetHostCapability
from shared_runtime_host.events import SharedRuntimeHostEvents
from runtimeV2.contracts import (
    ConnectorInspectionSnapshot,
    ConnectorReader,
    ConnectorWriter,
    ManifestReader,
    PanelStateReader,
    PanelStateWriter,
    PluginActiveReader,
    PluginActiveWriter,
    PluginIconResolver,
    PluginStateReader,
    SettingsReader,
    SettingsWriter,
    WidgetConfigReader,
    WidgetConfigWriter,
    WidgetVisibilityReader,
    WidgetVisibilityWriter,
)
from runtimeV2.events.contracts import EventType
from runtimeV2.ui.capabilities.render_status_read import RenderStatusRead
_QVARIANT_LIST: Any = "QVariantList"
_QVARIANT_MAP: Any = "QVariantMap"


class ManifestQmlCapability(QObject):
    """Expose manifest read models to QML."""

    pluginsChanged = Signal()

    def __init__(
        self,
        manifest_read: ManifestReader,
        plugin_icon: PluginIconResolver,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._manifest_read = manifest_read
        self._plugin_icon = plugin_icon

    @Property(_QVARIANT_LIST, notify=pluginsChanged)
    def plugins(self) -> list[dict[str, object]]:
        """Return plugin manifests as a QML model."""

        return [
            {
                "id": manifest.plugin_id,
                "type": manifest.plugin_type,
                "version": manifest.version,
                "author": manifest.author,
                "description": manifest.description,
                "iconUrl": self._plugin_icon.get_icon_url(manifest.plugin_id),
                "requires": manifest.requires,
                "windows": [window.id for window in manifest.ui.windows] if manifest.ui is not None else [],
                "windowCount": len(manifest.ui.windows) if manifest.ui is not None else 0,
                "settingCount": len(manifest.settings),
                "state": "",
            }
            for manifest in self._manifest_read.all_manifests().values()
        ]


class SettingsQmlCapability(QObject):
    """Expose persistence settings to QML."""

    settingsChanged = Signal()

    def __init__(self, settings_read: SettingsReader, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._settings_read = settings_read

    @Property(_QVARIANT_LIST, notify=settingsChanged)
    def settings(self) -> list[dict[str, object]]:
        """Return settings as a QML model."""

        items: list[dict[str, object]] = []
        for namespace, specs in self._settings_read.by_namespace().items():
            values = self._settings_read.namespace_values(namespace)
            for spec in specs:
                items.append(
                    {
                        "namespace": namespace,
                        "key": spec.key,
                        "label": spec.label,
                        "type": spec.type,
                        "defaultValue": spec.default,
                        "currentValue": str(values.get(spec.key, spec.default)),
                        "choices": list(spec.choices),
                    }
                )
        return items


class SettingsWriteQmlCapability(QObject):
    """Expose settings write actions to QML."""

    def __init__(self, settings_write: SettingsWriter, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._settings_write = settings_write

    @Slot(str, str, "QVariant")
    def setValue(self, namespace: str, key: str, value: object) -> None:
        """Set one setting value."""

        self._settings_write.set(namespace, key, value)

    @Slot(str)
    def save(self, namespace: str) -> None:
        """Save one namespace."""

        self._settings_write.save(namespace)

    @Slot()
    def saveAll(self) -> None:
        """Save all namespaces."""

        self._settings_write.save_all()


class ConnectorReadQmlCapability(QObject):
    """Expose connector registry reads to QML."""

    servicesChanged = Signal()
    connectorDataChanged = Signal(str)

    def __init__(
        self,
        connector_read: ConnectorReader,
        events: SharedRuntimeHostEvents | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._connector_read = connector_read
        if events is not None:
            events.subscribe(owner_domain="ui_api", event_type=EventType.CONNECTOR_SERVICE_REGISTERED, callback=self._on_services_changed)
            events.subscribe(owner_domain="ui_api", event_type=EventType.CONNECTOR_SERVICE_UNREGISTERED, callback=self._on_services_changed)
            events.subscribe(owner_domain="ui_api", event_type=EventType.CONNECTOR_SERVICE_UPDATED, callback=self._on_connector_runtime_changed)
            events.subscribe(owner_domain="ui_api", event_type=EventType.CONNECTOR_GAME_DETECTED, callback=self._on_connector_runtime_changed)
            events.subscribe(owner_domain="ui_api", event_type=EventType.CONNECTOR_GAME_LOST, callback=self._on_connector_runtime_changed)

    @Property(_QVARIANT_LIST, notify=servicesChanged)
    def services(self) -> list[dict[str, object]]:
        """Return connector services as a QML model."""

        return [
            {
                "id": service.connector_id,
                "pluginId": service.plugin_id,
                "label": service.display_name,
            }
            for service in self._connector_read.services()
        ]

    @Slot(str, result=_QVARIANT_LIST)
    def inspectionRows(self, connector_id: str) -> list[dict[str, str]]:
        """Return connector inspection rows as a QML model."""

        snapshot: ConnectorInspectionSnapshot = self._connector_read.inspection_rows(connector_id)
        rows = [{"key": key, "value": value} for key, value in snapshot]
        detected_game = self._connector_read.detected_game(connector_id)
        detected_process = self._connector_read.detected_process_name(connector_id)
        if detected_game is not None:
            rows.append({"key": "connector.detected_game", "value": detected_game})
        if detected_process is not None:
            rows.append({"key": "connector.detected_process", "value": detected_process})
        return rows

    def _on_services_changed(self, _event: object) -> None:
        """Mirror connector service registry changes into QML."""

        self.servicesChanged.emit()

    def _on_connector_runtime_changed(self, event: object) -> None:
        """Mirror connector runtime changes into QML."""

        connector_id = getattr(getattr(event, "data", None), "connector_id", "")
        if isinstance(connector_id, str) and connector_id:
            self.connectorDataChanged.emit(connector_id)
        self.servicesChanged.emit()


class ConnectorWriteQmlCapability(QObject):
    """Expose connector write actions to QML."""

    def __init__(self, connector_write: ConnectorWriter, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._connector_write = connector_write

    @Slot(str, result=bool)
    def updateConnector(self, connector_id: str) -> bool:
        """Update one connector service."""

        return self._connector_write.update(connector_id)

    @Slot(result=_QVARIANT_LIST)
    def updateAll(self) -> list[str]:
        """Update all connector services."""

        return self._connector_write.update_all()

    @Slot(str, str, str, result=bool)
    def requestSource(self, connector_id: str, owner: str, source_name: str) -> bool:
        """Request a connector source claim."""

        return self._connector_write.request_source(connector_id, owner, source_name)

    @Slot(str, str, result=bool)
    def releaseSource(self, connector_id: str, owner: str) -> bool:
        """Release a connector source claim."""

        return self._connector_write.release_source(connector_id, owner)


class WidgetConfigReadQmlCapability(QObject):
    """Expose widget config reads to QML."""

    def __init__(self, widget_config_read: WidgetConfigReader, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._widget_config_read = widget_config_read

    @Slot(str, str, result=_QVARIANT_MAP)
    def widgetValues(self, overlay_id: str, widget_id: str) -> dict[str, object]:
        """Return one widget value map."""

        return self._widget_config_read.widget_values(overlay_id, widget_id)

    @Slot(str, str, result=bool)
    def isWidgetEnabled(self, overlay_id: str, widget_id: str) -> bool:
        """Return whether one widget is enabled."""

        widget = self._widget_config_read.get_widget(overlay_id, widget_id)
        return True if widget is None else widget.enabled


class WidgetConfigWriteQmlCapability(QObject):
    """Expose widget config writes to QML."""

    def __init__(self, widget_config_write: WidgetConfigWriter, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._widget_config_write = widget_config_write

    @Slot(str, str, bool, result=bool)
    def setWidgetEnabled(self, overlay_id: str, widget_id: str, enabled: bool) -> bool:
        """Set widget enabled state."""

        return self._widget_config_write.set_widget_enabled(overlay_id, widget_id, enabled)

    @Slot(str, str, int, int, result=bool)
    def setWidgetPosition(self, overlay_id: str, widget_id: str, x: int, y: int) -> bool:
        """Set widget position."""

        return self._widget_config_write.set_widget_position(overlay_id, widget_id, x, y)

    @Slot(str, str, _QVARIANT_MAP, result=bool)
    def setWidgetValues(self, overlay_id: str, widget_id: str, values: dict[str, object]) -> bool:
        """Set widget value map."""

        return self._widget_config_write.set_widget_values(overlay_id, widget_id, values)

    @Slot(str, str, result=bool)
    def resetWidgetValues(self, overlay_id: str, widget_id: str) -> bool:
        """Reset widget value map."""

        return self._widget_config_write.reset_widget_values(overlay_id, widget_id)


class RenderStatusQmlCapability(QObject):
    """Expose UI render status to QML."""

    def __init__(self, render_status_read: RenderStatusRead, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._render_status_read = render_status_read

    @Property(bool, constant=True)
    def renderReady(self) -> bool:
        """Return whether UI render is ready."""

        return self._render_status_read.is_render_ready()

    @Property(str, constant=True)
    def renderBlocker(self) -> str:
        """Return the current render blocker."""

        return self._render_status_read.render_blocker()

    @Property(str, constant=True)
    def mainWindowId(self) -> str:
        """Return the main window id."""

        return self._render_status_read.main_window_id()


class WidgetRecordsQmlCapability(QObject):
    """Expose widget records to QML."""

    widgetsChanged = Signal()

    def __init__(
        self,
        widget_host: WidgetHostCapability,
        events: SharedRuntimeHostEvents,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._widget_host = widget_host
        events.subscribe(owner_domain="ui_api", event_type=EventType.WIDGET_RUNTIME_UPDATED, callback=self._on_widgets_changed)

    @Property(_QVARIANT_LIST, notify=widgetsChanged)
    def widgets(self) -> list[dict[str, object]]:
        """Return widget records as a QML model."""

        return self._widget_host.panel_records()

    def _on_widgets_changed(self, _event: object) -> None:
        """Mirror widget runtime refreshes into QML."""

        self.widgetsChanged.emit()


class WindowRecordsQmlCapability(QObject):
    """Expose UI window records to QML."""

    windowsChanged = Signal()

    def __init__(self, window_host: WindowHostCapability, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._window_host = window_host

    @Property(_QVARIANT_LIST, notify=windowsChanged)
    def windows(self) -> list[dict[str, object]]:
        """Return UI window records as a QML model."""

        return self._window_host.windows()


class WidgetVisibilityQmlCapability(QObject):
    """Expose widget visibility capabilities to QML."""

    globalVisibleChanged = Signal()

    def __init__(
        self,
        visibility_read: WidgetVisibilityReader,
        visibility_write: WidgetVisibilityWriter,
        events: SharedRuntimeHostEvents,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._visibility_read = visibility_read
        self._visibility_write = visibility_write
        events.subscribe(owner_domain="ui_api", event_type=EventType.WIDGET_VISIBILITY_CHANGED, callback=self._on_visibility_changed)

    @Property(bool, notify=globalVisibleChanged)
    def globalVisible(self) -> bool:
        """Return global widget visibility."""

        return self._visibility_read.global_visible()

    @Slot(bool)
    def setGlobalVisible(self, visible: bool) -> None:
        """Set global widget visibility."""

        if self._visibility_read.global_visible() == visible:
            return
        self._visibility_write.set_global_visible(visible)
        self.globalVisibleChanged.emit()

    @Slot(str, str, result=bool)
    def isWidgetEnabled(self, overlay_id: str, widget_id: str) -> bool:
        """Return whether one widget is enabled."""

        return self._visibility_read.is_widget_enabled(overlay_id, widget_id)

    def _on_visibility_changed(self, _event: object) -> None:
        """Mirror widget visibility changes into QML."""

        self.globalVisibleChanged.emit()


class PluginActiveQmlCapability(QObject):
    """Expose active plugin reads and writes to QML."""

    activePluginChanged = Signal(str)

    def __init__(
        self,
        active_read: PluginActiveReader,
        active_write: PluginActiveWriter,
        events: SharedRuntimeHostEvents,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._active_read = active_read
        self._active_write = active_write
        events.subscribe(owner_domain="ui_api", event_type=EventType.PLUGIN_ACTIVATED, callback=self._on_plugin_activity_changed)
        events.subscribe(owner_domain="ui_api", event_type=EventType.PLUGIN_DEACTIVATED, callback=self._on_plugin_activity_changed)

    @Slot(str, result=bool)
    def setActivePlugin(self, plugin_id: str) -> bool:
        """Set the active plugin."""

        changed = self._active_write.set_active_plugin(plugin_id)
        if changed:
            self.activePluginChanged.emit(self._active_read.get_active_plugin() or "")
        return changed

    @Property(str, notify=activePluginChanged)
    def activePlugin(self) -> str:
        """Return the active plugin id."""

        return self._active_read.get_active_plugin() or ""

    def _on_plugin_activity_changed(self, _event: object) -> None:
        """Mirror runtime active plugin changes into QML."""

        self.activePluginChanged.emit(self._active_read.get_active_plugin() or "")


class PluginStateQmlCapability(QObject):
    """Expose plugin lifecycle state reads to QML."""

    stateDataChanged = Signal()

    def __init__(
        self,
        state_read: PluginStateReader,
        plugin_ids: list[str],
        events: SharedRuntimeHostEvents,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._state_read = state_read
        self._plugin_ids = plugin_ids
        events.subscribe(owner_domain="ui_api", event_type=EventType.PLUGIN_STATE_CHANGED, callback=self._on_state_changed)
        events.subscribe(owner_domain="ui_api", event_type=EventType.PLUGIN_ERROR, callback=self._on_state_changed)
        events.subscribe(owner_domain="ui_api", event_type=EventType.PLUGIN_ACTIVATED, callback=self._on_state_changed)
        events.subscribe(owner_domain="ui_api", event_type=EventType.PLUGIN_DEACTIVATED, callback=self._on_state_changed)

    @Property(_QVARIANT_MAP, notify=stateDataChanged)
    def states(self) -> dict[str, str]:
        """Return plugin state map."""

        return {
            plugin_id: self._state_read.get_plugin_state(plugin_id).name.lower()
            for plugin_id in self._plugin_ids
        }

    @Property(_QVARIANT_MAP, notify=stateDataChanged)
    def errors(self) -> dict[str, str]:
        """Return plugin error map."""

        return {}

    @Property(_QVARIANT_MAP, notify=stateDataChanged)
    def histories(self) -> dict[str, list[dict[str, str]]]:
        """Return plugin state history map."""

        return {plugin_id: [] for plugin_id in self._plugin_ids}

    @Slot(str, result=str)
    def state(self, plugin_id: str) -> str:
        """Return one plugin state."""

        return self._state_read.get_plugin_state(plugin_id).name.lower()

    def _on_state_changed(self, _event: object) -> None:
        """Mirror runtime state changes into QML."""

        self.stateDataChanged.emit()


class PanelStateQmlCapability(QObject):
    """Expose runtime-owned UI panel state to QML."""

    visibleChanged = Signal()

    def __init__(
        self,
        panel_state_read: PanelStateReader,
        panel_state_write: PanelStateWriter,
        events: SharedRuntimeHostEvents,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._panel_state_read = panel_state_read
        self._panel_state_write = panel_state_write
        events.subscribe(owner_domain="ui_api", event_type=EventType.UI_PANEL_VISIBILITY_CHANGED, callback=self._on_panel_visibility_changed)

    @Property(bool, notify=visibleChanged)
    def visible(self) -> bool:
        """Return whether the runtime plugin panel is visible."""

        return self._panel_state_read.plugin_panel_visible()

    @Slot(bool, result=bool)
    def setVisible(self, visible: bool) -> bool:
        """Set runtime-owned plugin panel visibility."""

        changed = self._panel_state_write.set_plugin_panel_visible(visible)
        if changed:
            self.visibleChanged.emit()
        return changed

    @Slot(result=bool)
    def toggle(self) -> bool:
        """Toggle runtime-owned plugin panel visibility."""

        changed = self._panel_state_write.toggle_plugin_panel()
        if changed:
            self.visibleChanged.emit()
        return changed

    def _on_panel_visibility_changed(self, _event: object) -> None:
        """Mirror runtime panel visibility changes into QML."""

        self.visibleChanged.emit()


class UIChromeQmlCapability(QObject):
    """Expose UI chrome model data to QML."""

    tabModelChanged = Signal()
    menuItemsChanged = Signal()
    pluginMenuItemsChanged = Signal()
    statusbarItemsChanged = Signal()

    def __init__(self, ui_host: UIHostCapability, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._ui_host = ui_host

    @Property(_QVARIANT_LIST, notify=tabModelChanged)
    def tabModel(self) -> list[dict[str, str]]:
        """Return QML tab model."""

        return self._ui_host.tab_model()

    @Property(_QVARIANT_LIST, notify=menuItemsChanged)
    def menuItems(self) -> list[dict[str, object]]:
        """Return QML menu model."""

        return self._ui_host.menu_items()

    @Property(_QVARIANT_LIST, notify=pluginMenuItemsChanged)
    def pluginMenuItems(self) -> list[dict[str, object]]:
        """Return QML plugin menu model."""

        return self._ui_host.plugin_menu_items()

    @Property(str, notify=pluginMenuItemsChanged)
    def pluginMenuLabel(self) -> str:
        """Return QML plugin menu label."""

        return self._ui_host.plugin_menu_label()

    @Property(_QVARIANT_LIST, notify=statusbarItemsChanged)
    def leftItems(self) -> list[dict[str, str]]:
        """Return QML statusbar model."""

        return self._ui_host.left_status_items()

    @Property(_QVARIANT_LIST, notify=statusbarItemsChanged)
    def rightItems(self) -> list[dict[str, str]]:
        """Return right-side QML statusbar model."""

        return self._ui_host.right_status_items()

    @Property(_QVARIANT_LIST, notify=statusbarItemsChanged)
    def statusItems(self) -> list[dict[str, str]]:
        """Return all QML statusbar items."""

        return self._ui_host.status_items()

    @Property(str, constant=True)
    def activePluginId(self) -> str:
        """Return the active plugin id."""

        return self._ui_host.active_plugin_id()

    @Property(str, constant=True)
    def statusActiveLabel(self) -> str:
        """Return the active status label."""

        return self._ui_host.status_active_label()
