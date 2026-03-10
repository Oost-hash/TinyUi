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

"""TinyPedal adapter layer for TinyUi.

Provides a clean interface to TinyPedal core functionality without
tight coupling to the original UI or circular import issues.
"""

import sys
from pathlib import Path

# Add tinypedal_repo to path if needed (adjust based on your setup)
# This assumes tinypedal_repo is a sibling of tinyui or installed
try:
    import tinypedal_repo
except ImportError:
    # Fallback: add parent of tinyui to path
    _tinyui_root = Path(__file__).parent.parent.parent
    _tinypedal_path = _tinyui_root / "tinypedal_repo"
    if _tinypedal_path.exists():
        sys.path.insert(0, str(_tinypedal_path.parent))

# Core adapters - direct imports
# Lazy-loaded TinyPedal modules via tinypedal subpackage
from . import tinypedal
from .config import Config
from .hotkey import Hotkey
from .lifecycle import Lifecycle
from .loader import Loader

# Convenience exports
cfg = Config()  # Singleton instance
lifecycle = Lifecycle()  # Singleton instance
loader = Loader(cfg)  # Needs config
hotkey = Hotkey()

# Legacy compatibility: inject loader into sys.modules for tinypedal imports
sys.modules["tinypedal_repo.tinypedal.loader"] = loader

__all__ = [
    "cfg",
    "lifecycle",
    "loader",
    "hotkey",
    "tinypedal",
    "Config",
    "Lifecycle",
    "Loader",
    "Hotkey",
]
