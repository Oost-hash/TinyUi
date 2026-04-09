"""QML-facing ui_api capabilities above runtimeV2."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QObject, Property, Signal, Slot

from shared_runtime_host.capabilities.ui_host import UIHostCapability
from shared_runtime_host.capabilities.window_host import WindowHostCapability
from shared_runtime_host.capabilities.widget_host import WidgetHostCapability
from runtimeV2.manifest.capabilities.manifest_read import ManifestRead
from runtimeV2.plugins.capabilities.active_read import PluginActiveRead
from runtimeV2.plugins.capabilities.active_write import PluginActiveWrite
from runtimeV2.plugins.capabilities.state_read import PluginStateRead
from runtimeV2.ui.capabilities.panel_state_read import PanelStateRead
from runtimeV2.ui.capabilities.panel_state_write import PanelStateWrite
from runtimeV2.widgets.capabilities.widget_visibility_read import WidgetVisibilityRead
from runtimeV2.widgets.capabilities.widget_visibility_write import WidgetVisibilityWrite


_QVARIANT_LIST: Any = "QVariantList"
_QVARIANT_MAP: Any = "QVariantMap"


class ManifestQmlCapability(QObject):
    """Expose manifest read models to QML."""

    pluginsChanged = Signal()

    def __init__(self, manifest_read: ManifestRead, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._manifest_read = manifest_read

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
                "iconUrl": manifest.icon,
                "requires": manifest.requires,
                "windowCount": len(manifest.ui.windows) if manifest.ui is not None else 0,
                "settingCount": len(manifest.settings),
                "state": "",
            }
            for manifest in self._manifest_read.all_manifests().values()
        ]


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
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._active_read = active_read
        self._active_write = active_write

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


class PluginStateQmlCapability(QObject):
    """Expose plugin lifecycle state reads to QML."""

    pluginStateChanged = Signal(str, str)

    def __init__(self, state_read: PluginStateRead, plugin_ids: list[str], parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._state_read = state_read
        self._plugin_ids = plugin_ids

    @Property(_QVARIANT_MAP, constant=True)
    def states(self) -> dict[str, str]:
        """Return plugin state map."""

        return {
            plugin_id: self._state_read.get_plugin_state(plugin_id).name.lower()
            for plugin_id in self._plugin_ids
        }

    @Property(_QVARIANT_MAP, constant=True)
    def errors(self) -> dict[str, str]:
        """Return plugin error map."""

        return {}

    @Property(_QVARIANT_MAP, constant=True)
    def histories(self) -> dict[str, list[dict[str, str]]]:
        """Return plugin state history map."""

        return {plugin_id: [] for plugin_id in self._plugin_ids}

    @Slot(str, result=str)
    def state(self, plugin_id: str) -> str:
        """Return one plugin state."""

        return self._state_read.get_plugin_state(plugin_id).name.lower()


class PanelStateQmlCapability(QObject):
    """Expose runtime-owned UI panel state to QML."""

    visibleChanged = Signal()

    def __init__(
        self,
        panel_state_read: PanelStateRead,
        panel_state_write: PanelStateWrite,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._panel_state_read = panel_state_read
        self._panel_state_write = panel_state_write

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
