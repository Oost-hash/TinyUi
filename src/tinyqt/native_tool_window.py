from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget


def with_alpha(color: str, alpha: float) -> str:
    tint = QColor(color)
    tint.setAlphaF(max(0.0, min(1.0, alpha)))
    return tint.name(QColor.NameFormat.HexArgb)


class NativeToolWindowBase(QWidget):
    """Shared native shell for TinyUI secondary tool windows."""

    def __init__(
        self,
        *,
        title: str,
        eyebrow: str,
        subtitle: str,
        theme,
        object_name: str,
        width: int | None,
        height: int | None,
        min_width: int | None,
        min_height: int | None,
    ) -> None:
        super().__init__(None, Qt.WindowType.Window)
        self._theme = theme

        self.setWindowTitle(title)
        self.resize(width or 960, height or 640)
        self.setMinimumSize(min_width or 640, min_height or 420)
        self.setObjectName(object_name)

        self._eyebrow_label = QLabel(eyebrow)
        self._eyebrow_label.setObjectName("EyebrowLabel")
        self._title_label = QLabel(title)
        self._title_label.setObjectName("WindowTitle")
        self._subtitle_label = QLabel(subtitle)
        self._subtitle_label.setObjectName("WindowSubtitle")
        self._subtitle_label.setWordWrap(True)

        self._summary_card = QFrame()
        self._summary_card.setObjectName("SummaryCard")
        self._summary_layout = QVBoxLayout(self._summary_card)
        self._summary_layout.setContentsMargins(14, 12, 14, 12)
        self._summary_layout.setSpacing(4)
        self._summary_layout.addWidget(self._eyebrow_label)
        self._summary_layout.addWidget(self._title_label)
        self._summary_layout.addWidget(self._subtitle_label)

        self._root_layout = QVBoxLayout(self)
        self._root_layout.setContentsMargins(14, 14, 14, 14)
        self._root_layout.setSpacing(10)
        self._root_layout.addWidget(self._summary_card)

    def set_subtitle(self, text: str) -> None:
        self._subtitle_label.setText(text)

    def add_body_widget(self, widget: QWidget, *, stretch: int = 0) -> None:
        self._root_layout.addWidget(widget, stretch)

    def apply_shared_chrome_styles(self) -> str:
        return f"""
            QWidget#{self.objectName()} {{
                background-color: {self._theme.surface};
                color: {self._theme.text};
                font-family: "{self._theme.fontFamily}";
                font-size: {self._theme.fontSizeBase}px;
            }}
            QFrame#SummaryCard {{
                background-color: {self._theme.surfaceAlt};
                border: 1px solid {self._theme.border};
                border-radius: 4px;
            }}
            QLabel#EyebrowLabel {{
                color: {self._theme.accent};
                font-size: {self._theme.fontSizeSmall}px;
                font-weight: 700;
                letter-spacing: 1px;
            }}
            QLabel#WindowTitle {{
                color: {self._theme.text};
                font-size: {self._theme.fontSizeTitle - 1}px;
                font-weight: 600;
            }}
            QLabel#WindowSubtitle {{
                color: {self._theme.textMuted};
                font-size: {self._theme.fontSizeSmall}px;
            }}
        """
