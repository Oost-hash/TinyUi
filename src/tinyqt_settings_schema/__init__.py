"""Settings-facing schema contracts."""

from tinyruntime.schema_registry import SchemaDescriptor, SchemaRegistry

from .settings import SettingsSpec

SCHEMA_DESCRIPTOR = SchemaDescriptor(
    schema_id="tinyqt_settings.schema",
    package="tinyqt_settings_schema",
    owner="tinyqt_settings",
    summary="Settings dialog field and persistence schema contracts.",
    exports=("SettingsSpec",),
    tags=("settings", "persistence"),
)


def register_schema(registry: SchemaRegistry) -> None:
    """Register the settings schema with the runtime registry."""
    registry.register_schema(SCHEMA_DESCRIPTOR)


__all__ = ["SCHEMA_DESCRIPTOR", "SettingsSpec", "register_schema"]
