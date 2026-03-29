from __future__ import annotations

from collections.abc import Callable, Mapping

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from tinyqt.manifests import TinyQtButtonManifest


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

    def create_toolbar(self) -> tuple[QFrame, QHBoxLayout]:
        frame = QFrame()
        frame.setObjectName("DevToolsToolbar")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)
        return frame, layout

    def create_compact_toolbar(self) -> tuple[QFrame, QHBoxLayout]:
        frame = QFrame()
        frame.setObjectName("DevToolsToolbar")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(6)
        return frame, layout

    def create_footer_label(self) -> QLabel:
        label = QLabel("")
        label.setObjectName("RuntimeTasksLabel")
        label.setVisible(False)
        return label

    def create_footer_frame(self, *widgets: QWidget) -> tuple[QFrame, QHBoxLayout]:
        frame = QFrame()
        frame.setObjectName("FooterFrame")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch(1)
        for widget in widgets:
            layout.addWidget(widget)
        return frame, layout

    def create_button_bar(
        self,
        button_manifests: tuple[TinyQtButtonManifest, ...],
    ) -> tuple[QFrame, QHBoxLayout, dict[str, QPushButton]]:
        buttons: dict[str, QPushButton] = {}
        ordered_widgets: list[QPushButton] = []
        for button_manifest in button_manifests:
            button = QPushButton(button_manifest.label)
            button.setObjectName(
                "PrimaryButton" if button_manifest.role == "primary" else "SecondaryButton"
            )
            buttons[button_manifest.button_id] = button
            ordered_widgets.append(button)
        frame, layout = self.create_footer_frame(*ordered_widgets)
        return frame, layout, buttons

    def wire_button_actions(
        self,
        buttons: Mapping[str, QPushButton],
        actions: Mapping[str, Callable[[], object]],
    ) -> None:
        for button_id, button in buttons.items():
            action = actions.get(button_id)
            if action is not None:
                button.clicked.connect(action)

    def create_filter_button(self, label: str) -> QPushButton:
        button = QPushButton(label)
        button.setObjectName("RuntimeFilterButton")
        button.setCheckable(True)
        return button

    def create_section_frame(self) -> tuple[QFrame, QVBoxLayout]:
        frame = QFrame()
        frame.setObjectName("SectionFrame")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        return frame, layout

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

    def apply_shared_toolbar_styles(self) -> str:
        return f"""
            QFrame#DevToolsToolbar {{
                background-color: {self._theme.surfaceAlt};
                border: 1px solid {self._theme.border};
                border-radius: 3px;
            }}
            QLabel#RuntimeTasksLabel {{
                color: {self._theme.textMuted};
                font-size: 10px;
                padding: 6px 10px;
                border-top: 1px solid {self._theme.border};
                background-color: {self._theme.surfaceAlt};
            }}
        """

    def apply_shared_panel_styles(self) -> str:
        return f"""
            QLabel#SummaryTitle {{
                color: {self._theme.text};
                font-size: {self._theme.fontSizeTitle}px;
                font-weight: 600;
            }}
            QLabel#SummaryText {{
                color: {self._theme.textMuted};
                font-size: {self._theme.fontSizeSmall}px;
            }}
            QLabel#SectionLabel {{
                color: {self._theme.textSecondary};
                font-size: {self._theme.fontSizeSmall}px;
                font-weight: 600;
            }}
            QFrame#SectionFrame {{
                background-color: {self._theme.surfaceAlt};
                border: 1px solid {self._theme.border};
                border-radius: 6px;
            }}
            QFrame#FooterFrame {{
                background-color: transparent;
                border-top: 1px solid {self._theme.border};
                padding-top: 12px;
            }}
        """

    def apply_shared_interactive_styles(self, *, include_checkboxes: bool = False) -> str:
        check_icon = "C:/Users/rroet/Documents/TinyUi/src/assets/icons/check-small.svg"
        checkbox_styles = ""
        if include_checkboxes:
            checkbox_styles = f"""
                QCheckBox {{
                    color: {self._theme.textSecondary};
                    spacing: 6px;
                }}
                QCheckBox::indicator {{
                    width: 14px;
                    height: 14px;
                }}
                QCheckBox::indicator:unchecked {{
                    background-color: {self._theme.surfaceFloating};
                    border: 1px solid {self._theme.border};
                }}
                QCheckBox::indicator:checked {{
                    background-color: {self._theme.accent};
                    border: 1px solid {self._theme.accent};
                    image: url({check_icon});
                }}
            """
        return f"""
            QPushButton {{
                background-color: {self._theme.surfaceRaised};
                border: 1px solid {self._theme.border};
                color: {self._theme.text};
                border-radius: 5px;
                padding: 7px 12px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {self._theme.surfaceFloating};
                color: {self._theme.text};
            }}
            QPushButton:disabled {{
                color: {self._theme.textMuted};
                background-color: {self._theme.surfaceRaised};
            }}
            QPushButton#PrimaryButton {{
                background-color: {self._theme.accent};
                border-color: {self._theme.accent};
                color: {self._theme.accentText};
                font-weight: 500;
            }}
            QPushButton#PrimaryButton:hover {{
                background-color: {self._theme.accentHover};
                border-color: {self._theme.accentHover};
            }}
            QPushButton#PrimaryButton:disabled {{
                background-color: {self._theme.surfaceRaised};
                border-color: {self._theme.border};
                color: {self._theme.textMuted};
            }}
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
                background-color: {self._theme.surfaceFloating};
                border: 1px solid {self._theme.border};
                border-radius: 4px;
                padding: 4px 8px;
                min-height: 28px;
            }}
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
                border-color: {self._theme.accent};
            }}
            {checkbox_styles}
        """
