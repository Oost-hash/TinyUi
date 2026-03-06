#!/usr/bin/env python3
#
#  TinyUi - Custom UI layer for TinyPedal
#  Copyright (C) 2025 Oost-hash
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#

"""TinyUi - Entry point"""

import os
import sys

_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Add tinypedal submodule to path
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "tinypedal"))

# chdir naar tinypedal/ zodat TinyPedal's relatieve paden (settings/, brandlogo/,
# deltabest/, etc.) daar worden aangemaakt i.p.v. in de project root.
os.chdir(os.path.join(_PROJECT_ROOT, "tinypedal"))

from tinyui import main

if __name__ == "__main__":
    sys.exit(main.run())
