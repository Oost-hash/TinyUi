#!/usr/bin/env python3
"""Generate logo.png and logo.ico from logo assets.

Usage:
    python scripts/build_icon.py
"""

import sys
from pathlib import Path

# Ensure we can import PySide6
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication

ASSET_DIR = Path(__file__).resolve().parent.parent / "src" / "app_assets" / "logo"
SVG_PATH = ASSET_DIR / "logo.svg"
PNG_PATH = ASSET_DIR / "logo.png"
ICO_PATH = ASSET_DIR / "logo.ico"

ICO_SIZES = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]


def main():
    if not SVG_PATH.exists():
        print(f"  SVG not found: {SVG_PATH}")
        return 1

    _app = QApplication(sys.argv)

    png_renderer = QSvgRenderer(str(SVG_PATH))
    if not png_renderer.isValid():
        print(f"  Invalid SVG: {SVG_PATH}")
        return 1

    # Render PNG at 256x256
    img = QImage(256, 256, QImage.Format.Format_ARGB32)
    img.fill(Qt.GlobalColor.transparent)
    painter = QPainter(img)
    png_renderer.render(painter)
    painter.end()
    img.save(str(PNG_PATH))
    print(f"  icon.png saved ({PNG_PATH})")

    # Generate ICO with multiple sizes
    try:
        from PIL import Image

        ico_img = QImage(256, 256, QImage.Format.Format_ARGB32)
        ico_img.fill(Qt.GlobalColor.transparent)
        ico_painter = QPainter(ico_img)
        png_renderer.render(ico_painter)
        ico_painter.end()
        ico_png_path = ASSET_DIR / "logo-ico.png"
        ico_img.save(str(ico_png_path))

        pil_img = Image.open(ico_png_path)
        pil_img.save(ICO_PATH, sizes=ICO_SIZES)
        print(f"  icon.ico saved ({ICO_PATH})")
    except ImportError:
        print("  Pillow not installed, skipping .ico generation")
        print("  Install with: pip install Pillow")

    return 0


if __name__ == "__main__":
    sys.exit(main())
