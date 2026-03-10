"""Lazy-loaded TinyPedal module imports.

All imports here are lazy - no actual import happens until you access
the attribute. This prevents circular imports and speeds up startup.
"""

from ..lazy import LazyCallable, LazyModule

# Core API
api = LazyModule("tinypedal_repo.tinypedal.api_control", "api")

# Info modules
info = LazyModule("tinypedal_repo.tinypedal.module_info", "minfo")
state = LazyModule("tinypedal_repo.tinypedal.realtime_state")
calc = LazyModule("tinypedal_repo.tinypedal.calculation")
units = LazyModule("tinypedal_repo.tinypedal.units")

# Signals
signal = LazyModule("tinypedal_repo.tinypedal.app_signal")

# Submodules (for organized imports)
from . import app, files, log, main, settings

__all__ = [
    "api",
    "info",
    "state",
    "calc",
    "units",
    "signal",
    "app",
    "files",
    "settings",
    "main",
    "log",
]
