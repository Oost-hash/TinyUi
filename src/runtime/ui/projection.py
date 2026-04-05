"""Window runtime record projection."""

from __future__ import annotations

from app_schema.plugin import PluginManifest
from app_schema.ui import AppManifest
from runtime.host import main_window_for
from runtime.ui.contracts import WindowRuntimeRecord, WindowRuntimeStatus


def project_window_records(
    plugins: dict[str, PluginManifest],
    *,
    window_states: dict[str, WindowRuntimeStatus],
    window_errors: dict[str, str],
) -> list[WindowRuntimeRecord]:
    """Project manifest-declared windows to runtime-owned records."""

    main_window = main_window_for(plugins)
    records: list[WindowRuntimeRecord] = []
    for plugin_id, manifest in plugins.items():
        windows = [] if manifest.ui is None else manifest.ui.windows
        for window in windows:
            status = window_states.get(window.id, WindowRuntimeStatus.IDLE)
            records.append(
                WindowRuntimeRecord(
                    window_id=window.id,
                    plugin_id=plugin_id,
                    window_role=_window_role(window, main_window),
                    status=status,
                    visible=status in {WindowRuntimeStatus.OPEN, WindowRuntimeStatus.OPENING},
                    surface="" if window.surface is None else str(window.surface),
                    error_message=window_errors.get(window.id, ""),
                )
            )
    return records


def _window_role(window: AppManifest, main_window: AppManifest | None) -> str:
    if main_window is not None and window.id == main_window.id:
        return "main"
    if window.id.endswith(".dialog"):
        return "dialog"
    return "window"
