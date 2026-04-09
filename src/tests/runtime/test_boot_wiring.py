"""Regression tests for runtime V2 boot and startup wiring."""

from __future__ import annotations

from runtimeV2.capabilities.runtime_globals import RuntimeGlobals
from runtimeV2.capabilities.runtime_shutdown import RuntimeShutdown
from runtimeV2.connectors.capabilities.connector_read import ConnectorRead
from runtimeV2.connectors.capabilities.connector_write import ConnectorWrite
from runtimeV2.plugins.capabilities.active_read import PluginActiveRead
from runtimeV2.plugins.capabilities.active_write import PluginActiveWrite
from runtimeV2.register_capabilities import register_runtime_capabilities
from runtimeV2.register_domains import register_default_domains
from runtimeV2.register_globals import register_runtime_globals
from runtimeV2.runtime import RuntimeV2
from runtimeV2.startup import get_runtime_v2_result, startup_runtime_v2


def test_register_default_domains_uses_runtime_v2_order() -> None:
    """The default runtime V2 domains should stay in the visible startup order."""

    runtime = RuntimeV2()
    register_runtime_capabilities(runtime)
    register_runtime_globals(runtime)
    register_default_domains(runtime)

    assert runtime.domain_names() == [
        "events",
        "paths",
        "manifest",
        "plugins",
        "host",
        "persistence",
        "scheduler",
        "connectors",
        "widgets",
        "ui",
    ]


def test_runtime_v2_has_no_separate_plugin_lifecycle_domain() -> None:
    """Plugin lifecycle should stay inside the plugins domain instead of a separate domain."""

    runtime = RuntimeV2()
    register_runtime_capabilities(runtime)
    register_runtime_globals(runtime)
    register_default_domains(runtime)

    assert "plugins_lifecycle" not in runtime.domain_names()


def test_startup_runtime_v2_exposes_shutdown_plugin_and_connector_globals() -> None:
    """A booted runtime V2 should expose runtime, plugin, and connector globals through RuntimeGlobals."""

    result = startup_runtime_v2()

    assert result.ok

    runtime_result = get_runtime_v2_result()
    assert runtime_result is not None

    runtime = runtime_result.runtime
    globals_capability = runtime.capability("globals", RuntimeGlobals)

    assert globals_capability.read_global("shutdown", RuntimeShutdown) is runtime.capability("shutdown", RuntimeShutdown)
    assert globals_capability.read_global("active_plugin", PluginActiveRead) is runtime.capability(
        "plugin_active_read",
        PluginActiveRead,
    )
    assert globals_capability.write_global("active_plugin", PluginActiveWrite) is runtime.capability(
        "plugin_active_write",
        PluginActiveWrite,
    )
    assert globals_capability.read_global("connector_runtime", ConnectorRead) is runtime.capability(
        "connector_read",
        ConnectorRead,
    )
    assert globals_capability.write_global("connector_runtime", ConnectorWrite) is runtime.capability(
        "connector_write",
        ConnectorWrite,
    )
    assert runtime.capability("plugin_active_read", object) is not None
    assert runtime.capability("plugin_state_read", object) is not None
    assert runtime.domain_names() == [
        "events",
        "paths",
        "manifest",
        "plugins",
        "host",
        "persistence",
        "scheduler",
        "connectors",
        "widgets",
        "ui",
    ]
