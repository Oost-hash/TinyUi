"""tinycore.config — generic config store and JSON loader infrastructure."""

from .store import ConfigStore
from .loader import LoaderRegistry, read_json, write_json

__all__ = ["ConfigStore", "LoaderRegistry", "read_json", "write_json"]
