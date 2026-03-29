#!/usr/bin/env python3
"""Render UI SVG icons to DPI-aware PNGs.

Leest SVGs uit src/tinyqt_main/images/src/ en schrijft PNGs naar:
    src/tinyqt_main/images/16/   —  16×16  (100% DPI)
    src/tinyqt_main/images/20/   —  20×20  (125% DPI)
    src/tinyqt_main/images/24/   —  24×24  (150% DPI)

Usage:
    python scripts/build_ui_icons.py
"""

import os
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication

IMAGES_DIR = os.path.join(
    os.path.dirname(__file__), "..", "src", "tinyqt_main", "images"
)
SRC_DIR = os.path.join(IMAGES_DIR, "src")
SIZES = [16, 20, 24]


def render_svg(svg_path: str, size: int) -> QImage:
    """Render SVG als wit-op-transparant PNG.

    SVGs hebben zwarte stroke. We renderen eerst naar zwart-op-transparant,
    dan vullen we een wit canvas en gebruiken de SVG als alpha-masker zodat
    het resultaat wit-op-transparant is. MultiEffect kan wit pixels dan
    kleuriseren naar elke gewenste kleur.
    """
    renderer = QSvgRenderer(svg_path)

    # Stap 1: render SVG (zwart op transparant)
    mask = QImage(size, size, QImage.Format.Format_ARGB32)
    mask.fill(Qt.GlobalColor.transparent)
    painter = QPainter(mask)
    renderer.render(painter)
    painter.end()

    # Stap 2: wit canvas, gebruik SVG als alpha-masker
    result = QImage(size, size, QImage.Format.Format_ARGB32)
    result.fill(Qt.GlobalColor.white)
    painter = QPainter(result)
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
    painter.drawImage(0, 0, mask)
    painter.end()

    return result


def main():
    _app = QApplication(sys.argv)

    svgs = sorted(f for f in os.listdir(SRC_DIR) if f.endswith(".svg"))
    if not svgs:
        print(f"Geen SVG bestanden gevonden in {SRC_DIR}")
        return 1

    for size in SIZES:
        os.makedirs(os.path.join(IMAGES_DIR, str(size)), exist_ok=True)

    for svg_name in svgs:
        svg_path = os.path.join(SRC_DIR, svg_name)
        stem = os.path.splitext(svg_name)[0]

        for size in SIZES:
            img = render_svg(svg_path, size)
            out_path = os.path.join(IMAGES_DIR, str(size), f"{stem}.png")
            img.save(out_path)
            print(f"  {size}/{stem}.png  ({size}×{size})")

    print(f"\n{len(svgs)} icons verwerkt.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
