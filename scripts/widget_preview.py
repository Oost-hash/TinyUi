"""Manual preview entry point for the first widget_api renderer phase."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ui_api.qt import create_application
from widget_api.preview import create_connector_preview_window, create_preview_window


def main() -> int:
    app = create_application()
    use_static_preview = "--static" in sys.argv
    window = create_preview_window() if use_static_preview else create_connector_preview_window()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
