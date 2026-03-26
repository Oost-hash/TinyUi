#!/usr/bin/env python3
"""Generate icon.png and icon.ico from icon.svg.

Usage:
    python scripts/build_icon.py
"""

import sys
import os

# Ensure we can import PySide6
from PySide6.QtWidgets import QApplication
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtGui import QImage, QPainter
from PySide6.QtCore import Qt

IMAGES_DIR = os.path.join(os.path.dirname(__file__), "..", "src", "tinyui", "images")
SVG_PATH = os.path.join(IMAGES_DIR, "src", "icon.svg")
PNG_PATH = os.path.join(IMAGES_DIR, "icon.png")
ICO_PATH = os.path.join(IMAGES_DIR, "icon.ico")

ICO_SIZES = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]


def main():
    if not os.path.exists(SVG_PATH):
        print(f"  SVG not found: {SVG_PATH}")
        return 1

    _app = QApplication(sys.argv)

    renderer = QSvgRenderer(SVG_PATH)
    if not renderer.isValid():
        print(f"  Invalid SVG: {SVG_PATH}")
        return 1

    # Render PNG at 256x256
    img = QImage(256, 256, QImage.Format.Format_ARGB32)
    img.fill(Qt.GlobalColor.transparent)
    painter = QPainter(img)
    renderer.render(painter)
    painter.end()
    img.save(PNG_PATH)
    print(f"  icon.png saved ({PNG_PATH})")

    # Generate ICO with multiple sizes
    try:
        from PIL import Image

        pil_img = Image.open(PNG_PATH)
        pil_img.save(ICO_PATH, sizes=ICO_SIZES)
        print(f"  icon.ico saved ({ICO_PATH})")
    except ImportError:
        print("  Pillow not installed, skipping .ico generation")
        print("  Install with: pip install Pillow")

    return 0


if __name__ == "__main__":
    sys.exit(main())
