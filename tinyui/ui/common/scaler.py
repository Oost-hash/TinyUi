# tinyui/ui/common/scaler.py
from PySide2.QtWidgets import QApplication


class UIScaler:
    """UI font & size scaler - LAZY initialization for testing."""

    _initialized = False
    FONT_POINT = 10
    FONT_DPI = 96
    FONT_DPI_SCALE = 1.0
    FONT_PIXEL_SCALED = 13.0

    @classmethod
    def _ensure_initialized(cls):
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
        cls._ensure_initialized()
        return cls.FONT_POINT * scale

    @classmethod
    def size(cls, scale: float) -> int:
        cls._ensure_initialized()
        return round(cls.FONT_PIXEL_SCALED * scale)

    @classmethod
    def pixel(cls, pixel: int):
        cls._ensure_initialized()
        return round(cls.FONT_DPI_SCALE * pixel)
