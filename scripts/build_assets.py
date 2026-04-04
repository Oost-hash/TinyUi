#!/usr/bin/env python3
"""Generate host assets from repo-root assets and sync them into the tinyui host plugin.

Usage:
    python scripts/build_assets.py
"""

from __future__ import annotations

import shutil
import os
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtGui import QGuiApplication

ROOT = Path(__file__).resolve().parent.parent
ASSET_ROOT = ROOT / "assets"
HOST_ASSET_DIR = ROOT / "src" / "plugins" / "tinyui" / "assets"

LOGO_DIR = ASSET_ROOT / "images" / "logo"
SVG_PATH = LOGO_DIR / "logo.svg"
PNG_PATH = LOGO_DIR / "logo.png"
ICO_PATH = LOGO_DIR / "logo.ico"

ICO_SIZES = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]


def _ensure_headless_qt_env() -> None:
    """Make Qt asset rendering work in headless CI environments."""
    if sys.platform.startswith("linux"):
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        os.environ.setdefault("QT_QUICK_BACKEND", "software")
        os.environ.setdefault("QSG_RHI_BACKEND", "software")


def _build_icons() -> int:
    if not SVG_PATH.exists():
        print(f"  SVG not found: {SVG_PATH}")
        return 1

    _ensure_headless_qt_env()
    _app = QGuiApplication.instance() or QGuiApplication(sys.argv)

    renderer = QSvgRenderer(str(SVG_PATH))
    if not renderer.isValid():
        print(f"  Invalid SVG: {SVG_PATH}")
        return 1

    image = QImage(256, 256, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    renderer.render(painter)
    painter.end()
    image.save(str(PNG_PATH))
    print(f"  icon.png saved ({PNG_PATH})")

    try:
        from PIL import Image

        temp_png_path = LOGO_DIR / "logo-ico.png"
        try:
            image.save(str(temp_png_path))
            pil_img = Image.open(temp_png_path)
            pil_img.save(ICO_PATH, sizes=ICO_SIZES)
            print(f"  icon.ico saved ({ICO_PATH})")
        finally:
            if temp_png_path.exists():
                temp_png_path.unlink()
    except ImportError:
        print("  Pillow not installed, skipping .ico generation")
        print("  Install with: pip install Pillow")

    return 0


def _sync_host_assets() -> None:
    if HOST_ASSET_DIR.exists():
        shutil.rmtree(HOST_ASSET_DIR)
    shutil.copytree(ASSET_ROOT, HOST_ASSET_DIR)
    print(f"  host assets synced ({HOST_ASSET_DIR})")


def main() -> int:
    result = _build_icons()
    if result != 0:
        return result
    _sync_host_assets()
    return 0


if __name__ == "__main__":
    sys.exit(main())
