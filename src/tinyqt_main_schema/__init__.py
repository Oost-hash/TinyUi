"""Main-surface schema contracts."""

from tinyruntime.schema_registry import SchemaDescriptor, SchemaRegistry

from .editors import ColumnDef, EditorRegistry, EditorSpec, load_editors_toml

SCHEMA_DESCRIPTOR = SchemaDescriptor(
    schema_id="tinyqt_main.schema",
    package="tinyqt_main_schema",
    owner="tinyqt_main",
    summary="Main-surface editor and widget schema contracts.",
    exports=("ColumnDef", "EditorRegistry", "EditorSpec", "load_editors_toml"),
    tags=("main", "editor", "widget"),
)


def register_schema(registry: SchemaRegistry) -> None:
    """Register the main-surface schema with the runtime registry."""
    registry.register_schema(SCHEMA_DESCRIPTOR)

__all__ = [
    "ColumnDef",
    "EditorRegistry",
    "EditorSpec",
    "SCHEMA_DESCRIPTOR",
    "load_editors_toml",
    "register_schema",
]
