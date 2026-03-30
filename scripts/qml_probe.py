"""Legacy compatibility wrapper for the internal QML probe runner."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.internal.qml_probe import main


if __name__ == "__main__":
    raise SystemExit(main())
