"""TinyUI entry point — Qt setup only, runtime orchestrates everything else."""

from __future__ import annotations

import sys

from app_api.host_actions import HostActions
from app_api.inspector import RuntimeInspector
from app_api.qt import create_application, create_engine
from app_api.theme import Theme
from app_api.window import open_window
from app_api.windowing import win_window  # eager import: registers QML singletons before engine
from runtime.runtime import Runtime


def main() -> int:
    app = create_application()
    engine = create_engine()

    runtime = Runtime()
    runtime.boot()

    theme_name = runtime.settings.get("tinyui", "theme") or "dark"
    theme = Theme(theme_name)
    actions = HostActions()

    main_manifest = runtime.main_window()
    if main_manifest is None:
        print("No main window found", file=sys.stderr)
        return 1

    main_handle = open_window(main_manifest, engine=engine, app=app, actions=actions, theme=theme)
    main_handle.qml_window.setProperty("menuItems", runtime.menu.to_qml_host(main_manifest.id))
    main_handle.qml_window.setProperty("pluginMenuItems", runtime.menu.to_qml_plugins(main_manifest.id))

    open_handles = []

    def make_open_handler(window_id: str, requires: list[str]):
        def handler():
            manifest = runtime.window_for(window_id)
            if manifest:
                h = open_window(manifest, engine=engine, app=app, actions=actions, theme=theme)
                if "inspector" in requires:
                    h.qml_window.setProperty("inspector", RuntimeInspector(runtime.devtools_data()))
                open_handles.append(h)
        return handler

    for w in runtime.all_windows():
        if w.window_type == "dialog":
            actions.register(f"open:{w.id}", make_open_handler(w.id, w.requires))

    actions.register("close", lambda: main_handle.qml_window.close())

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
