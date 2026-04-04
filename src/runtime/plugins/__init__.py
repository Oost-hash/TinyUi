"""Plugin runtime helpers and lifecycle primitives."""

from runtime.plugins.plugin_context import PluginContext
from runtime.plugins.plugin_lifecycle import (
    NoOpPluginLifecycle,
    PluginLifecycle,
    PythonModulePluginLifecycle,
    resolve_plugin_lifecycle,
)
from runtime.plugins.plugin_state import PluginStateMachine, StateTransition

__all__ = [
    "NoOpPluginLifecycle",
    "PluginContext",
    "PluginLifecycle",
    "PluginStateMachine",
    "PythonModulePluginLifecycle",
    "StateTransition",
    "resolve_plugin_lifecycle",
]
