#!/usr/bin/env python3
#
#  TinyUi - Custom UI layer for TinyPedal
#  Copyright (C) 2026 Oost-hash
#

"""TinyUi - Entry point"""

import os
import subprocess
import sys

_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Voeg de root van tinypedal_repo toe aan sys.path (zodat pyLMUSharedMemory gevonden wordt)
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "tinypedal_repo"))

# Ga naar de TinyPedal package map voor configuratiebestanden
os.chdir(os.path.join(_PROJECT_ROOT, "tinypedal_repo", "tinypedal"))

from tinyui import main

if __name__ == "__main__":
    sys.exit(main.run())
