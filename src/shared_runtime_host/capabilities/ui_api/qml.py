"""QML-facing ui_api capabilities above runtimeV2."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QObject, Property, Signal, Slot

from shared_runtime_host.capabilities.ui_host import UIHostCapability
from shared_runtime_host.capabilities.window_host import WindowHostCapability
from shared_runtime_host.capabilities.widget_host import WidgetHostCapability
from runtimeV2.connectors.capabilities.connector_read import ConnectorRead
from runtimeV2.connectors.capabilities.connector_write import ConnectorWrite
from runtimeV2.connectors.contracts import ConnectorInspectionSnapshot
from runtimeV2.events.contracts import EventType
from runtimeV2.events.startup_shutdown.startup import EventsStartupResult
from runtimeV2.manifest.capabilities.manifest_read import ManifestRead
from runtimeV2.persistence.capabilities.settings_read import SettingsRead
from runtimeV2.persistence.capabilities.settings_write import SettingsWrite
from runtimeV2.persistence.capabilities.widget_config_read import WidgetConfigRead
from runtimeV2.persistence.capabilities.widget_config_write import WidgetConfigWrite
from runtimeV2.plugins.capabilities.active_read import PluginActiveRead
from runtimeV2.plugins.capabilities.active_write import PluginActiveWrite
from runtimeV2.plugins.capabilities.icon import PluginIconCapability
from runtimeV2.plugins.capabilities.state_read import PluginStateRead
from runtimeV2.ui.capabilities.render_status_read import RenderStatusRead
from runtimeV2.ui.capabilities.panel_state_read import PanelStateRead
from runtimeV2.ui.capabilities.panel_state_write import PanelStateWrite
from runtimeV2.widgets.capabilities.widget_visibility_read import WidgetVisibilityRead
from runtimeV2.widgets.capabilities.widget_visibility_write import WidgetVisibilityWrite


_QVARIANT_LIST: Any = "QVariantList"
_QVARIANT_MAP: Any = "QVariantMap"


class ManifestQmlCapability(QObject):
    """Expose manifest read models to QML."""

    pluginsChanged = Signal()

    def __init__(
        self,
        manifest_read: ManifestRead,
        plugin_icon: PluginIconCapability,
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

    def __init__(self, settings_read: SettingsRead, parent: QObject | None = None) -> None:
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
                        "type": spec.type,
                        "currentValue": str(values.get(spec.key, spec.default)),
                    }
                )
        return items


class SettingsWriteQmlCapability(QObject):
    """Expose settings write actions to QML."""

    def __init__(self, settings_write: SettingsWrite, parent: QObject | None = None) -> None:
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

    def __init__(self, connector_read: ConnectorRead, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._connector_read = connector_read

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
        return [{"key": key, "value": value} for key, value in snapshot]


class ConnectorWriteQmlCapability(QObject):
    """Expose connector write actions to QML."""

    def __init__(self, connector_write: ConnectorWrite, parent: QObject | None = None) -> None:
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

    def __init__(self, widget_config_read: WidgetConfigRead, parent: QObject | None = None) -> None:
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

    def __init__(self, widget_config_write: WidgetConfigWrite, parent: QObject | None = None) -> None:
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

    def __init__(self, widget_host: WidgetHostCapability, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._widget_host = widget_host

    @Property(_QVARIANT_LIST, notify=widgetsChanged)
    def widgets(self) -> list[dict[str, object]]:
        """Return widget records as a QML model."""

        return self._widget_host.panel_records()


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
        visibility_read: WidgetVisibilityRead,
        visibility_write: WidgetVisibilityWrite,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._visibility_read = visibility_read
        self._visibility_write = visibility_write

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


class PluginActiveQmlCapability(QObject):
    """Expose active plugin reads and writes to QML."""

    activePluginChanged = Signal(str)

    def __init__(
        self,
        active_read: PluginActiveRead,
        active_write: PluginActiveWrite,
        events: EventsStartupResult,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._active_read = active_read
        self._active_write = active_write
        events.bus.on(EventType.PLUGIN_ACTIVATED, self._on_plugin_activity_changed)
        events.bus.on(EventType.PLUGIN_DEACTIVATED, self._on_plugin_activity_changed)

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
        state_read: PluginStateRead,
        plugin_ids: list[str],
        events: EventsStartupResult,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._state_read = state_read
        self._plugin_ids = plugin_ids
        events.bus.on(EventType.PLUGIN_STATE_CHANGED, self._on_state_changed)
        events.bus.on(EventType.PLUGIN_ERROR, self._on_state_changed)
        events.bus.on(EventType.PLUGIN_ACTIVATED, self._on_state_changed)
        events.bus.on(EventType.PLUGIN_DEACTIVATED, self._on_state_changed)

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
        panel_state_read: PanelStateRead,
        panel_state_write: PanelStateWrite,
        events: EventsStartupResult,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._panel_state_read = panel_state_read
        self._panel_state_write = panel_state_write
        events.bus.on(EventType.UI_PANEL_VISIBILITY_CHANGED, self._on_panel_visibility_changed)

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
