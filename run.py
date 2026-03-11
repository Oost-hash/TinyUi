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


"""TinyUi - Entry point"""

import os
import sys

_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(_PROJECT_ROOT, "src")

# Voeg src/ toe aan path
sys.path.insert(0, SRC_DIR)

# CRUCIAL: Injecteer loader adapter VOORDAT we tinypedal importeren
# Dit breekt circular imports in hotkey_control -> loader -> hotkey_control
from src.tinyui.adapters.loader import Loader  # Geen src. prefix!

sys.modules["tinypedal.loader"] = Loader(None)  # Let op: geen sys. ervoor!

# Ga naar src/ als working directory
os.chdir(SRC_DIR)

from src.tinyui import main  # Geen src. prefix!

if __name__ == "__main__":
    sys.exit(main.run())
