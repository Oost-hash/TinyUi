"""tinycore.config — generic config store and loader infrastructure."""

from .store import ConfigStore
from .loader import ConfigLoader, LoaderRegistry, read_json, write_json

__all__ = ["ConfigStore", "ConfigLoader", "LoaderRegistry", "read_json", "write_json"]
