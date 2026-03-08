#!/usr/bin/env python3
#
#  TinyUi - Custom UI layer for TinyPedal
#  Copyright (C) 2026 Oost-hash
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#

"""TinyUi - Entry point"""

import os
import subprocess
import sys

_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Generate adapter files FIRST (before any tinypedal/tinyui imports)
_gen_script = os.path.join(_PROJECT_ROOT, "tinyui", "backend", "generate_adapters.py")
_result = subprocess.run([sys.executable, _gen_script])
if _result.returncode != 0:
    sys.exit(1)

# Add tinypedal submodule to path
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "tinypedal"))

# chdir naar tinypedal/ zodat TinyPedal's relatieve paden daar worden aangemaakt
os.chdir(os.path.join(_PROJECT_ROOT, "tinypedal"))

from tinyui import main

if __name__ == "__main__":
    sys.exit(main.run())
