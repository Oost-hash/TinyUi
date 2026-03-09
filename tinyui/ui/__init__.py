#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2026 TinyPedal developers, see contributors.md file
#
#  This file is part of TinyPedal.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Application UI
"""

from PySide2.QtWidgets import QApplication


class UIScaler:
    """UI font & size scaler - LAZY initialization for testing."""

    _initialized = False
    FONT_POINT = 10  # Default fallback
    FONT_DPI = 96
    FONT_DPI_SCALE = 1.0
    FONT_PIXEL_SCALED = 13.0  # 10 * 96 / 72 ≈ 13

    @classmethod
    def _ensure_initialized(cls):
        """Lazy init - only access QApplication when actually needed."""
        if not cls._initialized:
            app = QApplication.instance()
            if app is not None:
                cls.FONT_POINT = app.font().pointSize()
                cls.FONT_DPI = app.fontMetrics().fontDpi()
                cls.FONT_DPI_SCALE = cls.FONT_DPI / 96
                cls.FONT_PIXEL_SCALED = cls.FONT_POINT * cls.FONT_DPI / 72
            cls._initialized = True

    @classmethod
    def font(cls, scale: float) -> float:
        """Scale UI font size (points) by base font size (not counting dpi scale)"""
        cls._ensure_initialized()
        return cls.FONT_POINT * scale

    @classmethod
    def size(cls, scale: float) -> int:
        """Scale UI size (pixels) by base font size (scaled with dpi)"""
        cls._ensure_initialized()
        return round(cls.FONT_PIXEL_SCALED * scale)

    @classmethod
    def pixel(cls, pixel: int):
        """Scale pixel size by base font DPI scale"""
        cls._ensure_initialized()
        return round(cls.FONT_DPI_SCALE * pixel)
