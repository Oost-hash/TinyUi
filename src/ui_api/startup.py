"""Startup helpers for ui_api-owned window hosting."""

from __future__ import annotations

import sys
from typing import Any, Protocol, Sequence

from app_schema.ui import AppManifest
from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlComponent

from runtime.app.paths import AppPaths
from runtime_schema import StartupResult, startup_error, startup_ok
from ui_api.api.app_actions import AppActions
from ui_api.theme import Theme
from ui_api.ui_runtime_host import WindowHostController, attach_main_window_shutdown, attach_window_runtime_tracking
from ui_api.window import open_window


class WindowRuntimeLike(Protocol):
    """Minimal runtime surface needed by ui_api startup helpers."""

    def main_window(self) -> AppManifest | None: ...
    def window_for(self, window_id: str) -> AppManifest | None: ...
    def all_windows(self) -> Sequence[AppManifest]: ...
    def mark_window_opening(self, window_id: str) -> None: ...
    def mark_window_open(self, window_id: str) -> None: ...
    def mark_window_closed(self, window_id: str) -> None: ...
    def mark_window_error(self, window_id: str, message: str) -> None: ...
    def begin_shutdown(self, reason: str = "app_quit") -> None: ...
    @property
    def paths(self) -> AppPaths | None: ...


def resolve_plugin_panel(engine, runtime: WindowRuntimeLike) -> tuple[str, object | None]:
    """Resolve the optional plugin panel component exposed to host windows."""

    assert runtime.paths is not None
    plugin_panel_path = runtime.paths.host_dir / "app_pluginsPanel" / "qml" / "surface.qml"
    if not plugin_panel_path.exists():
        return "", None
    plugin_panel_url = QUrl.fromLocalFile(str(plugin_panel_path))
    return str(plugin_panel_path), QQmlComponent(engine, plugin_panel_url)


def open_main_runtime_window(
    *,
    app,
    engine,
    actions: AppActions,
    theme: Theme,
    runtime: WindowRuntimeLike,
    shared_capabilities,
    runtime_capabilities,
    build_window_capability_properties,
):
    """Open the main runtime window and return manifest plus live handle."""

    main_manifest = runtime.main_window()
    if main_manifest is None:
        return None, None, startup_error("No main window found")

    plugin_panel_url, plugin_panel_component = resolve_plugin_panel(engine, runtime)
    main_window_properties = build_window_capability_properties(
        main_manifest,
        shared_capabilities,
        runtime_capabilities,
        plugin_panel_url=plugin_panel_url,
        plugin_panel_component=plugin_panel_component,
    )
    runtime.mark_window_opening(main_manifest.id)
    try:
        handle = open_window(
            main_manifest,
            engine=engine,
            app=app,
            actions=actions,
            theme=theme,
            **main_window_properties,
        )
    except Exception as exc:
        runtime.mark_window_error(main_manifest.id, str(exc))
        return None, None, startup_error(f"ui_api main window startup failed: {exc}")
    runtime.mark_window_open(main_manifest.id)
    attach_window_runtime_tracking(runtime, main_manifest.id, handle.qml_window)
    attach_main_window_shutdown(runtime, handle.qml_window)
    return main_manifest, handle, startup_ok()


def register_runtime_window_actions(
    *,
    app,
    engine,
    actions: AppActions,
    theme: Theme,
    runtime: WindowRuntimeLike,
    shared_capabilities,
    runtime_capabilities,
    main_manifest,
    main_handle,
    window_host_controller: WindowHostController,
    build_window_capability_properties,
) -> StartupResult:
    """Register runtime-backed open and close actions for manifest windows."""

    main_handle.qml_window.destroyed.connect(app.quit)
    main_handle.qml_window.setProperty("showStatusBar", True)
    main_handle.qml_window.setProperty("showTabBar", True)
    window_host_controller.track(main_manifest.id, main_handle)

    open_handles: list[Any] = []

    def make_open_handler(window_id: str):
        def handler():
            manifest = runtime.window_for(window_id)
            if manifest is None:
                return
            kwargs = build_window_capability_properties(
                manifest,
                shared_capabilities,
                runtime_capabilities,
            )
            runtime.mark_window_opening(window_id)
            try:
                handle = open_window(manifest, engine=engine, app=app, actions=actions, theme=theme, **kwargs)
            except Exception as exc:
                runtime.mark_window_error(window_id, str(exc))
                raise
            runtime.mark_window_open(window_id)
            attach_window_runtime_tracking(runtime, window_id, handle.qml_window)
            window_host_controller.track(window_id, handle)
            open_handles.append(handle)

        return handler

    for window in runtime.all_windows():
        if window.id != main_manifest.id:
            actions.register(f"open:{window.id}", make_open_handler(window.id))

    def _close_main() -> None:
        runtime.begin_shutdown("main_window_close")
        main_handle.qml_window.close()

    actions.register("close", _close_main)
    return startup_ok()
