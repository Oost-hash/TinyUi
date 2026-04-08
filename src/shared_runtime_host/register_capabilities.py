"""Register shared runtime host projection capabilities."""

from __future__ import annotations

from runtimeV2.widgets.capabilities.widget_records_read import WidgetRecordsRead

from shared_runtime_host.capabilities.widget_host import WidgetHostCapability
from shared_runtime_host.registry import SharedRuntimeHostRegistry


def register_shared_runtime_host_capabilities(registry: SharedRuntimeHostRegistry) -> None:
    """Register the shared runtime host projections."""

    runtime = registry.runtime
    registry.register_capability(
        "widget_host",
        WidgetHostCapability(runtime.capability("widget_records_read", WidgetRecordsRead)),
    )
