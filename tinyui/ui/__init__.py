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
    """UI font & size scaler"""
    # Global base font size in point (not counting dpi scale)
    FONT_POINT = QApplication.font().pointSize()
    FONT_DPI = QApplication.fontMetrics().fontDpi()
    # Global base font size in pixel (dpi scaled)
    # dpi scale = font dpi / 96
    # px = (pt * dpi scale) * 96 / 72
    # px = pt * font dpi / 72
    FONT_DPI_SCALE = FONT_DPI / 96
    FONT_PIXEL_SCALED = FONT_POINT * FONT_DPI / 72

    @classmethod
    def font(cls, scale: float) -> float:
        """Scale UI font size (points) by base font size (not counting dpi scale)"""
        return cls.FONT_POINT * scale

    @classmethod
    def size(cls, scale: float) -> int:
        """Scale UI size (pixels) by base font size (scaled with dpi)"""
        return round(cls.FONT_PIXEL_SCALED * scale)

    @classmethod
    def pixel(cls, pixel: int):
        """Scale pixel size by base font DPI scale"""
        return round(cls.FONT_DPI_SCALE * pixel)
