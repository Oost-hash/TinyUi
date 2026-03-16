"""tinycore.config — generic config store and TOML loader infrastructure."""

from .store import ConfigStore
from .loader import LoaderRegistry, read_toml, write_toml

__all__ = ["ConfigStore", "LoaderRegistry", "read_toml", "write_toml"]
