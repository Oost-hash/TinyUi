#  TinyUI - A mod for TinyPedal
#  Copyright (C) 2026 Oost-hash
#
#  This file is part of TinyUI.
#
#  TinyUI is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  TinyUI is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  TinyUI builds on TinyPedal by s-victor (https://github.com/s-victor/TinyPedal),
#  licensed under GPLv3. TinyPedal is included as a submodule.

"""Lazy-loaded TinyPedal module imports.

All imports here are lazy - no actual import happens until you access
the attribute. This prevents circular imports and speeds up startup.
"""

from ..lazy import LazyCallable, LazyModule

# Core API
api = LazyModule("tinypedal.api_control", "api")

# Info modules
info = LazyModule("tinypedal.module_info", "minfo")
state = LazyModule("tinypedal.realtime_state")
calc = LazyModule("tinypedal.calculation")
units = LazyModule("tinypedal.units")

# Signals
signal = LazyModule("tinypedal.app_signal")

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
