"""UI manifest read capability for runtime V2."""

from runtimeV2.manifest.registry import ManifestRegistry
from runtimeV2.ui.schemas.manifest import AppManifest, MenuItem, MenuSeparator, StatusbarItemDecl, TabDecl


class ManifestUiRead:
    """Read UI declarations from plugin manifests."""

    def __init__(self, registry: ManifestRegistry) -> None:
        self._registry = registry

    def windows(self) -> dict[str, list[AppManifest]]:
        """Return manifest windows by plugin id."""

        return {
            plugin_id: [] if manifest.ui is None else list(manifest.ui.windows)
            for plugin_id, manifest in self._registry.all_manifests().items()
        }

    def tabs(self) -> dict[str, list[TabDecl]]:
        """Return manifest tabs by plugin id."""

        return {
            plugin_id: [] if manifest.ui is None else list(manifest.ui.tabs)
            for plugin_id, manifest in self._registry.all_manifests().items()
        }

    def menus(self) -> dict[str, list[MenuItem | MenuSeparator]]:
        """Return plugin menu declarations by plugin id."""

        return {
            plugin_id: [] if manifest.ui is None else list(manifest.ui.plugin_menu)
            for plugin_id, manifest in self._registry.all_manifests().items()
        }

    def statusbar_items(self) -> dict[str, list[StatusbarItemDecl]]:
        """Return statusbar item declarations by window id."""

        items: dict[str, list[StatusbarItemDecl]] = {}
        for manifest in self._registry.all_manifests().values():
            if manifest.ui is None:
                continue
            for window in manifest.ui.windows:
                items[window.id] = list(window.statusbar)
        return items
