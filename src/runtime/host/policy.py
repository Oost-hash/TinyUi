"""Host-specific runtime policy."""

from __future__ import annotations

from app_schema.plugin import PluginManifest
from app_schema.ui import AppManifest


def active_host_ids(plugins: dict[str, PluginManifest]) -> set[str]:
    """Return host plugin ids that form the baseline runtime shell."""
    return {
        plugin_id
        for plugin_id, manifest in plugins.items()
        if manifest.plugin_type == "host"
    }


def main_window_for(plugins: dict[str, PluginManifest]) -> AppManifest | None:
    """Return the primary host window when available."""
    for manifest in plugins.values():
        if manifest.plugin_type == "host" and manifest.ui and manifest.ui.windows:
            return manifest.ui.windows[0]
    return None
