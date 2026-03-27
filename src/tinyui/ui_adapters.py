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

#  TinyUI
"""TinyUI-owned UI adapter helpers."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol, cast

from PySide6.QtCore import QObject
from PySide6.QtQml import QQmlApplicationEngine

if TYPE_CHECKING:
    from tinydevtools.host import DevToolsUiAttachment


class _WindowGeometryLike(Protocol):
    def setX(self, value: int, /) -> None: ...
    def setY(self, value: int, /) -> None: ...
    def setWidth(self, value: int, /) -> None: ...
    def setHeight(self, value: int, /) -> None: ...
    def x(self) -> int: ...
    def y(self) -> int: ...
    def width(self) -> int: ...
    def height(self) -> int: ...


class _ThemeLike(Protocol):
    def load(self, name: str, /) -> None: ...


def _maybe_int(value: object) -> int | None:
    return int(value) if isinstance(value, int | float | str) else None


def bind_statusbar_plugin_switching(core, statusbar_view_model: object) -> None:
    """Drive plugin lifecycle activation from the status bar selection surface."""
    if not isinstance(statusbar_view_model, QObject):
        return

    plugin_names = [plugin.name for plugin in core.runtime.plugins.plugins]
    if not plugin_names:
        return

    def _on_plugin_switch() -> None:
        index = _maybe_int(statusbar_view_model.property("activePluginIndex"))
        if index is None:
            return
        if 0 <= index < len(plugin_names):
            core.lifecycle.activate(plugin_names[index])

    active_changed = cast(Any, getattr(statusbar_view_model, "activePluginIndexChanged", None))
    if active_changed is not None:
        active_changed.connect(_on_plugin_switch)


def bind_theme_settings(
    core,
    core_view_model: object,
    settings_panel_view_model: object,
    theme: _ThemeLike,
) -> None:
    """Apply and persist TinyUI theme/settings wiring through host persistence."""
    if not isinstance(core_view_model, QObject) or not isinstance(
        settings_panel_view_model, QObject
    ):
        return

    def _apply_tinyui_settings() -> None:
        theme_name = core.host.persistence.get_setting("TinyUI", "theme")
        if theme_name:
            theme.load(str(theme_name))

    def _save_setting(plugin_name: str) -> None:
        core.host.persistence.save_settings(plugin_name)

    settings_changed = cast(Any, getattr(core_view_model, "settingsChanged", None))
    setting_value_changed = cast(
        Any, getattr(core_view_model, "settingValueChanged", None)
    )
    setting_change_requested = cast(
        Any, getattr(settings_panel_view_model, "settingChangeRequested", None)
    )
    set_setting_value = cast(Any, getattr(core_view_model, "setSettingValue", None))

    if settings_changed is not None:
        settings_changed.connect(_apply_tinyui_settings)
    if setting_value_changed is not None:
        setting_value_changed.connect(_save_setting)
    if setting_change_requested is not None and callable(set_setting_value):
        setting_change_requested.connect(set_setting_value)

    _apply_tinyui_settings()


def restore_main_window_state(core, window: _WindowGeometryLike) -> None:
    """Restore persisted TinyUI window position and size onto the Qt main window."""
    remember_position = core.host.persistence.get_setting("TinyUI", "remember_position")
    if remember_position:
        x_pos = _maybe_int(core.host.persistence.get_setting("TinyUI", "_position_x"))
        y_pos = _maybe_int(core.host.persistence.get_setting("TinyUI", "_position_y"))
        if x_pos is not None and y_pos is not None:
            window.setX(x_pos)
            window.setY(y_pos)

    remember_size = core.host.persistence.get_setting("TinyUI", "remember_size")
    if remember_size:
        width = _maybe_int(core.host.persistence.get_setting("TinyUI", "_window_width"))
        height = _maybe_int(core.host.persistence.get_setting("TinyUI", "_window_height"))
        if width is not None and height is not None:
            window.setWidth(width)
            window.setHeight(height)


def save_main_window_state(core, window: _WindowGeometryLike) -> None:
    """Persist the TinyUI main window position and size through host persistence."""
    if core.host.persistence.get_setting("TinyUI", "remember_position"):
        core.host.persistence.set_setting("TinyUI", "_position_x", window.x())
        core.host.persistence.set_setting("TinyUI", "_position_y", window.y())
    if core.host.persistence.get_setting("TinyUI", "remember_size"):
        core.host.persistence.set_setting("TinyUI", "_window_width", window.width())
        core.host.persistence.set_setting("TinyUI", "_window_height", window.height())
    core.host.persistence.save_settings("TinyUI")


def wire_app_shutdown(
    app: QObject,
    core,
    *,
    window: _WindowGeometryLike,
    log_inspector,
    engine: QObject,
    devtools_ui: object | None = None,
) -> None:
    """Attach TinyUI shutdown and persistence behavior to the Qt app lifecycle."""
    about_to_quit = cast(Any, getattr(app, "aboutToQuit", None))
    if about_to_quit is None:
        return

    about_to_quit.connect(lambda: save_main_window_state(core, window))
    about_to_quit.connect(log_inspector.shutdown)
    about_to_quit.connect(engine.deleteLater)
    about_to_quit.connect(core.shutdown)
    if devtools_ui is not None:
        log_view_model = getattr(devtools_ui, "log_view_model", None)
        shutdown = getattr(log_view_model, "shutdown", None)
        if callable(shutdown):
            about_to_quit.connect(shutdown)


def attach_optional_devtools_ui(
    core, engine: QQmlApplicationEngine, log_inspector
) -> "DevToolsUiAttachment | None":
    """Attach optional devtools UI viewmodels through the TinyUI adapter seam."""
    try:
        from tinydevtools.host import attach_ui
    except ImportError:
        return None

    qml_path = Path(core.paths.qml_dir("tinydevtools")) / "DevToolsWindow.qml"
    return attach_ui(
        engine,
        log_inspector,
        qml_path=qml_path,
    )


def wire_devtools_monitor(core, window: object) -> None:
    """Run the devtools monitor only while the Dev Tools window is visible."""
    loader = getattr(window, "findChild", None)
    if not callable(loader):
        return

    devtools_loader = cast(QObject | None, loader(QObject, "devToolsLoader"))
    if devtools_loader is None:
        return

    devtools_window = devtools_loader.property("item")
    if not isinstance(devtools_window, QObject):
        return

    def _sync_visibility() -> None:
        visible = bool(devtools_window.property("visible"))
        if visible:
            core.activate_host_unit("devtools.monitor")
            return
        try:
            core.deactivate_host_unit("devtools.monitor")
        except RuntimeError:
            pass

    visible_changed = cast(Any, getattr(devtools_window, "visibleChanged", None))
    if visible_changed is not None:
        visible_changed.connect(_sync_visibility)
    _sync_visibility()
