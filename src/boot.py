"""TinyUI entry point — Qt setup only, runtime orchestrates everything else."""

from __future__ import annotations

import sys

from app_api.host_actions import HostActions
from app_api.qt import create_application, create_engine
from app_api.theme import Theme
from app_api.window import open_window
from runtime.runtime import Runtime


def main() -> int:
    app = create_application()
    engine = create_engine()

    runtime = Runtime()
    runtime.boot()

    theme_name = runtime.settings.get("tinyui", "theme") or "dark"
    theme = Theme(theme_name)
    actions = HostActions()

    main_manifest = runtime.main_window_manifest()
    if main_manifest is None:
        print("No main window manifest found", file=sys.stderr)
        return 1

    # open main window
    main_handle = open_window(main_manifest, engine=engine, app=app, actions=actions, theme=theme)

    # set menu items from registry
    main_handle.qml_window.setProperty("menuItems", runtime.menu.to_qml("tinyui.main"))

    # wire actions: open:<app_id> → open dialog
    open_handles = []

    def make_open_handler(app_id: str):
        def handler():
            manifest = runtime.manifest_for(app_id)
            if manifest and manifest.window:
                h = open_window(manifest, engine=engine, app=app, actions=actions, theme=theme)
                open_handles.append(h)
        return handler

    for m in runtime.all_manifests():
        if m.window and m.window.kind == "dialog":
            actions.register(f"open:{m.app_id}", make_open_handler(m.app_id))

    actions.register("close", lambda: main_handle.qml_window.close())

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
