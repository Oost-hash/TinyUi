"""Plugin lifecycle adapters for Python-backed and manifest-only plugins."""

from __future__ import annotations

import importlib
import importlib.util
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from runtime.plugins.contracts import PluginContext


class PluginLifecycle(Protocol):
    """Common lifecycle surface for all plugin activation models."""

    def activate(self, ctx: PluginContext) -> None:
        """Activate plugin resources for the given context."""

    def deactivate(self, ctx: PluginContext) -> None:
        """Release plugin resources for the given context."""


@dataclass(frozen=True)
class NoOpPluginLifecycle:
    """Lifecycle for manifest-only plugins without Python hooks."""

    plugin_id: str

    def activate(self, ctx: PluginContext) -> None:
        """Manifest-driven plugins need no Python activation step."""

    def deactivate(self, ctx: PluginContext) -> None:
        """Manifest-driven plugins need no Python deactivation step."""


@dataclass(frozen=True)
class PythonModulePluginLifecycle:
    """Lifecycle backed by a plugin.py module."""

    plugin_id: str

    @property
    def module_name(self) -> str:
        return f"plugins.{self.plugin_id}.plugin"

    def activate(self, ctx: PluginContext) -> None:
        """Import plugin module and call activate if provided."""
        mod = importlib.import_module(self.module_name)
        if hasattr(mod, "activate"):
            mod.activate(ctx)

    def deactivate(self, ctx: PluginContext) -> None:
        """Import plugin module and call deactivate if provided."""
        mod = importlib.import_module(self.module_name)
        if hasattr(mod, "deactivate"):
            mod.deactivate(ctx)


def resolve_plugin_lifecycle(
    plugin_id: str,
    plugin_type: str,
    plugins_dir: Path,
) -> PluginLifecycle:
    """Resolve the lifecycle adapter for a plugin."""
    module_path = plugins_dir / plugin_id / "plugin.py"
    module_name = f"plugins.{plugin_id}.plugin"
    has_module = module_path.exists() or importlib.util.find_spec(module_name) is not None
    if plugin_type == "plugin" and not has_module:
        return NoOpPluginLifecycle(plugin_id)
    return PythonModulePluginLifecycle(plugin_id)
