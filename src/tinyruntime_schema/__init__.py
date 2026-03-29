"""Runtime-owned observability schemas and listener primitives."""

from tinyruntime.schema_registry import SchemaDescriptor, SchemaRegistry

from .log_records import LogInspector, LogRecordEntry
from .logging import (
    ALL_CATEGORIES,
    DiagnosticsLogger,
    configure_diagnostics,
    diagnostics_enabled,
    get_category_states,
    get_dev_mode,
    get_logger,
    set_category_enabled,
    set_dev_mode,
)
from .runtime_state import InspectionEntry, InspectionSourceInfo, RuntimeInspector
from .snapshot_protocols import InspectionSnapshot, InspectionSnapshotProvider

SCHEMA_DESCRIPTOR = SchemaDescriptor(
    schema_id="tinyruntime.schema",
    package="tinyruntime_schema",
    owner="tinyruntime",
    summary="Runtime observability schemas, log capture, and inspection listeners.",
    exports=(
        "ALL_CATEGORIES",
        "DiagnosticsLogger",
        "InspectionEntry",
        "InspectionSnapshot",
        "InspectionSnapshotProvider",
        "InspectionSourceInfo",
        "LogInspector",
        "LogRecordEntry",
        "RuntimeInspector",
    ),
    tags=("runtime", "observability", "logging"),
)


def register_schema(registry: SchemaRegistry) -> None:
    """Register the runtime schema with the runtime registry."""
    registry.register_schema(SCHEMA_DESCRIPTOR)

__all__ = [
    "ALL_CATEGORIES",
    "DiagnosticsLogger",
    "SCHEMA_DESCRIPTOR",
    "InspectionEntry",
    "InspectionSnapshot",
    "InspectionSnapshotProvider",
    "InspectionSourceInfo",
    "LogInspector",
    "LogRecordEntry",
    "RuntimeInspector",
    "configure_diagnostics",
    "diagnostics_enabled",
    "get_category_states",
    "get_dev_mode",
    "get_logger",
    "register_schema",
    "set_category_enabled",
    "set_dev_mode",
]
