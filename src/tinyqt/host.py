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
"""Shared Qt host helpers used by UI-facing feature packages."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Protocol, cast

from PySide6.QtCore import QObject, QUrl, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, QQmlComponent
from PySide6.QtQuick import QQuickItem, QQuickWindow

from tinyqt.devtools_support import DevToolsUiAttachment, attach_devtools_ui
from tinyqt.engine import create_engine
from tinyqt.apps.devtools import build_tinydevtools_manifest
from tinyqt.manifests import (
    TinyQtAppManifest,
    manifest_eager_panel_indexes,
    manifest_has_optional_feature,
    manifest_menu_items,
    manifest_panel_labels,
    validate_required_singletons,
)
from tinyqt.registration import (
    RegistrationMap,
    SingletonRegistration,
    register_context_map,
    register_singletons,
)
from tinyqt.windowing import WindowingAttachment, attach_windowing

class WindowGeometryLike(Protocol):
    def setX(self, value: int, /) -> None: ...
    def setY(self, value: int, /) -> None: ...
    def setWidth(self, value: int, /) -> None: ...
    def setHeight(self, value: int, /) -> None: ...
    def x(self) -> int: ...
    def y(self) -> int: ...
    def width(self) -> int: ...
    def height(self) -> int: ...


class NativeToolWindowLike(Protocol):
    def toggle(self) -> None: ...


NativeWindowFactory = Callable[[TinyQtAppManifest], NativeToolWindowLike]


class LazyNativeWindowController(QObject):
    """Open one manifest-backed native secondary window on demand."""

    def __init__(
        self,
        *,
        app,
        manifest: TinyQtAppManifest,
        build_window: NativeWindowFactory,
    ) -> None:
        super().__init__(cast(QObject | None, app))
        self._manifest = manifest
        self._build_window = build_window
        self._window: NativeToolWindowLike | None = None

    @Slot()
    def toggle(self) -> None:
        if self._window is None:
            self._window = self._build_window(self._manifest)
        self._window.toggle()


def apply_manifest_shell_state(window: QObject, manifest: TinyQtAppManifest) -> None:
    """Push manifest-defined shell state onto the loaded root object when supported."""
    shell = manifest.shell
    property_values: dict[str, object] = {
        "windowTitle": manifest.title,
        "menuItems": manifest_menu_items(manifest),
        "tabLabels": manifest_panel_labels(manifest),
        "currentTab": 0,
        "showTabBar": shell.use_tab_bar,
        "showStatusBar": shell.use_status_bar,
        "lazyPanelLoading": shell.lazy_panel_loading,
        "eagerPanelIndexes": manifest_eager_panel_indexes(manifest),
    }
    for name, value in property_values.items():
        window.setProperty(name, value)


@dataclass(frozen=True)
class QtWindowHost:
    engine: QQmlApplicationEngine
    window: QQuickWindow
    devtools_ui: DevToolsUiAttachment | None
    devtools_controller: LazyNativeWindowController | None
    windowing: WindowingAttachment


def build_native_window_controller(
    *,
    app,
    manifest: TinyQtAppManifest,
    build_window: NativeWindowFactory,
) -> LazyNativeWindowController:
    """Create a manifest-backed native secondary-window controller."""
    if manifest.window.presentation != "native":
        raise ValueError(
            f"TinyQt manifest '{manifest.app_id}' does not declare a native presentation"
        )
    return LazyNativeWindowController(
        app=app,
        manifest=manifest,
        build_window=build_window,
    )


def _maybe_int(value: object) -> int | None:
    return int(value) if isinstance(value, int | float | str) else None


def restore_window_state(core, window: WindowGeometryLike, *, scope: str) -> None:
    """Restore persisted window position and size onto a Qt window."""
    remember_position = core.host.persistence.get_setting(scope, "remember_position")
    if remember_position:
        x_pos = _maybe_int(core.host.persistence.get_setting(scope, "_position_x"))
        y_pos = _maybe_int(core.host.persistence.get_setting(scope, "_position_y"))
        if x_pos is not None and y_pos is not None:
            window.setX(x_pos)
            window.setY(y_pos)

    remember_size = core.host.persistence.get_setting(scope, "remember_size")
    if remember_size:
        width = _maybe_int(core.host.persistence.get_setting(scope, "_window_width"))
        height = _maybe_int(core.host.persistence.get_setting(scope, "_window_height"))
        if width is not None and height is not None:
            window.setWidth(width)
            window.setHeight(height)


def save_window_state(core, window: WindowGeometryLike, *, scope: str) -> None:
    """Persist window position and size through host persistence."""
    if core.host.persistence.get_setting(scope, "remember_position"):
        core.host.persistence.set_setting(scope, "_position_x", window.x())
        core.host.persistence.set_setting(scope, "_position_y", window.y())
    if core.host.persistence.get_setting(scope, "remember_size"):
        core.host.persistence.set_setting(scope, "_window_width", window.width())
        core.host.persistence.set_setting(scope, "_window_height", window.height())
    core.host.persistence.save_settings(scope)


def wire_app_shutdown(
    app: QObject,
    core,
    *,
    window: WindowGeometryLike,
    scope: str,
    log_inspector,
    engine: QObject,
    devtools_ui: object | None = None,
) -> None:
    """Attach shutdown and persistence behavior to the Qt app lifecycle."""
    about_to_quit = cast(Any, getattr(app, "aboutToQuit", None))
    if about_to_quit is None:
        return

    about_to_quit.connect(lambda: save_window_state(core, window, scope=scope))
    about_to_quit.connect(log_inspector.shutdown)
    about_to_quit.connect(engine.deleteLater)
    about_to_quit.connect(core.shutdown)
    if devtools_ui is not None:
        log_view_model = getattr(devtools_ui, "log_view_model", None)
        shutdown = getattr(log_view_model, "shutdown", None)
        if callable(shutdown):
            about_to_quit.connect(shutdown)


def attach_optional_devtools_ui(
    core,
    engine: QQmlApplicationEngine,
    log_inspector,
    *,
    host_manifest: TinyQtAppManifest | None = None,
) -> "DevToolsUiAttachment | None":
    """Attach optional devtools UI viewmodels through the shared Qt host seam."""
    if host_manifest is not None and not manifest_has_optional_feature(host_manifest, "devtools_ui"):
        return None

    devtools_manifest = build_tinydevtools_manifest(core.paths)
    qml_path = devtools_manifest.root_qml
    if qml_path is None:
        return None
    return attach_devtools_ui(
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


def load_root_window(
    engine: QQmlApplicationEngine,
    qml_path: Path,
) -> QQuickWindow | None:
    """Load a QML file and return the root QQuickWindow when successful."""
    engine.load(QUrl.fromLocalFile(str(qml_path)))
    if not engine.rootObjects():
        return None

    window_obj = engine.rootObjects()[0]
    if not isinstance(window_obj, QQuickWindow):
        return None
    return window_obj


def attach_window_content(
    engine: QQmlApplicationEngine,
    window: QQuickWindow,
    qml_path: Path,
) -> bool:
    """Attach an Item-based content root into an already loaded host window."""
    component = QQmlComponent(engine)
    component.loadUrl(QUrl.fromLocalFile(str(qml_path)))
    if component.isError():
        for error in component.errors():
            print(error.toString())
        return False
    content_item = component.create()
    if component.isError():
        for error in component.errors():
            print(error.toString())
        return False
    if not isinstance(content_item, QQuickItem):
        return False
    content_item.setParent(window)
    content_item.setParentItem(window.contentItem())
    content_item.setWidth(window.width())
    content_item.setHeight(window.height())
    width_changed = cast(Any, getattr(window, "widthChanged", None))
    height_changed = cast(Any, getattr(window, "heightChanged", None))
    if width_changed is not None:
        width_changed.connect(lambda: content_item.setWidth(window.width()))
    if height_changed is not None:
        height_changed.connect(lambda: content_item.setHeight(window.height()))
    return True


def create_settings_controller(
    *,
    app,
    core,
    theme: object,
    build_registrations: Callable[[object | None], list[SingletonRegistration]],
) -> LazyNativeWindowController:
    """Create the shared TinyUI settings controller from its manifest."""
    from tinyqt.apps.tinyui import build_tinyui_settings_manifest

    manifest = build_tinyui_settings_manifest(core.paths)

    def _build_window(window_manifest: TinyQtAppManifest) -> NativeToolWindowLike:
        from tinyqt_native.native_settings_window import NativeSettingsWindow

        registrations = build_registrations(None)
        settings_vm = next(
            registration.instance
            for registration in registrations
            if registration.name == "SettingsPanelViewModel"
        )
        return NativeSettingsWindow(
            core=core,
            theme=theme,
            settings_view_model=settings_vm,
            manifest=window_manifest,
        )

    return build_native_window_controller(
        app=app,
        manifest=manifest,
        build_window=_build_window,
    )


def create_devtools_controller(
    *,
    app,
    core,
    theme: object,
    log_inspector: object,
) -> LazyNativeWindowController:
    """Create the shared TinyUI devtools controller from its manifest."""
    manifest = build_tinydevtools_manifest(core.paths)

    def _build_window(window_manifest: TinyQtAppManifest) -> NativeToolWindowLike:
        from tinyqt_native.native_devtools_window import NativeDevToolsWindow

        return NativeDevToolsWindow(
            core=core,
            theme=theme,
            log_inspector=log_inspector,
            manifest=window_manifest,
        )

    return build_native_window_controller(
        app=app,
        manifest=manifest,
        build_window=_build_window,
    )


def create_window_host(
    core,
    *,
    app,
    qml_path: Path,
    app_manifest: TinyQtAppManifest,
    theme,
    log_inspector,
    build_registrations: Callable[[DevToolsUiAttachment | None], list[SingletonRegistration]],
    extra_context: RegistrationMap | None = None,
    module: str = "TinyUI",
) -> QtWindowHost | None:
    """Create the shared Qt window host and attach common runtime surfaces."""
    engine = create_engine()

    devtools_ui = None
    initial_registrations = build_registrations(devtools_ui)
    register_singletons(initial_registrations)
    if extra_context:
        register_context_map(extra_context)

    window = load_root_window(engine, qml_path)
    if window is None:
        return None
    window.setProperty("theme", theme)
    apply_manifest_shell_state(window, app_manifest)
    devtools_controller = None
    if manifest_has_optional_feature(app_manifest, "devtools_ui"):
        devtools_controller = create_devtools_controller(
            app=app,
            core=core,
            theme=theme,
            log_inspector=log_inspector,
        )
        window.setProperty("devToolsController", devtools_controller)
        window.setProperty("devToolsAvailable", True)
    else:
        window.setProperty("devToolsAvailable", devtools_ui is not None)
    window.setProperty("devToolsQmlPath", "" if devtools_ui is None else devtools_ui.qml_url)

    wire_devtools_monitor(core, window)
    windowing = attach_windowing(app=app, window=window, theme=theme, module=module)
    if windowing.registrations:
        register_singletons(list(windowing.registrations))

    available_singletons = {registration.name for registration in initial_registrations}
    available_singletons.update(registration.name for registration in windowing.registrations)
    if extra_context:
        available_singletons.update(extra_context.keys())
    missing_singletons = validate_required_singletons(app_manifest, available_singletons)
    if missing_singletons:
        raise RuntimeError(
            "TinyQt manifest contract violation for "
            f"'{app_manifest.app_id}': missing required singletons: {', '.join(missing_singletons)}"
        )

    return QtWindowHost(
        engine=engine,
        window=window,
        devtools_ui=devtools_ui,
        devtools_controller=devtools_controller,
        windowing=windowing,
    )
