"""Host-specific runtime policy."""

from __future__ import annotations

from app_schema.manifest import AppManifest, PluginManifest


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
        if manifest.plugin_type == "host" and manifest.windows:
            return manifest.windows[0]
    return None
