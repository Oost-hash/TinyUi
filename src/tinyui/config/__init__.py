"""TinyUI config — re-exports from tinycore + local loaders."""

from tinycore.config import ConfigStore, ConfigLoader, LoaderRegistry, read_json, write_json

__all__ = ["ConfigStore", "ConfigLoader", "LoaderRegistry", "read_json", "write_json"]
