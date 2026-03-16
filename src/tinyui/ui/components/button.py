#  TinyUI - A mod for TinyPedal
#  Copyright (C) 2026 Oost-hash
#
#  This file is part of TinyUI.
#
#  TinyUI is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  TinyUI is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  TinyUI builds on TinyPedal by s-victor (https://github.com/s-victor/TinyPedal),
#  licensed under GPLv3. TinyPedal is included as a submodule.

"""
TinyUI Button Component
Een veelzijdige button met theming, icons, states en animations.
"""

import os
from typing import Callable, Optional, Union

from PySide6.QtCore import Property, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPalette, QPixmap
from PySide6.QtWidgets import QPushButton, QSizePolicy


class Button(QPushButton):
    """
    TinyUI Button component.

    Features:
    - Theming support (via TinyUI theme system)
    - Icon support (links of rechts)
    - Meerdere varianten: default, primary, secondary, danger, ghost
    - States: normal, hover, pressed, disabled, loading
    - Sizes: small, medium, large
    - Toggle mode (aan/uit switch)
    - Loading state met spinner
    - Volledige toetsenbord support (Space, Enter)
    """

    # Custom signals
    clicked_safe = Signal()  # Alleen als niet disabled/loading

    # Varianten
    DEFAULT = "default"
    PRIMARY = "primary"
    SECONDARY = "secondary"
    DANGER = "danger"
    GHOST = "ghost"
    SUCCESS = "success"

    # Groottes
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"

    def __init__(
        self,
        text: str = "",
        parent=None,
        variant: str = DEFAULT,
        size: str = MEDIUM,
        icon: Optional[QIcon] = None,
        icon_right: bool = False,
        toggle: bool = False,
        checkable: bool = False,
        flat: bool = False,
        loading: bool = False,
        on_click: Optional[Callable] = None,
        shortcut: Optional[str] = None,
    ):
        super().__init__(text, parent)

        # Interne state
        self._variant = variant
        self._size = size
        self._icon_right = icon_right
        self._loading = loading
        self._original_text = text
        self._spinner_timer: Optional[QTimer] = None
        self._spinner_frame = 0

        # Basis setup
        self.setCheckable(checkable or toggle)
        self.setFlat(flat)

        # Size policy
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        # Icon setup
        if icon:
            self.setIcon(icon)

        # Shortcut
        if shortcut:
            self.setShortcut(shortcut)

        # Connecties
        if on_click:
            self.clicked_safe.connect(on_click)

        # Native clicked alleen doorgeven als we enabled en niet loading zijn
        self.clicked.connect(self._on_clicked)

        # Styling toepassen
        self._apply_styling()

    def _on_clicked(self):
        """Interne handler voor click events."""
        if not self._loading and self.isEnabled():
            self.clicked_safe.emit()

    def _apply_styling(self):
        """Pas alle styling toe gebaseerd op variant en size."""
        self._apply_size()
        self._apply_variant()
        self._update_icon_position()

    def _apply_size(self):
        """Pas grootte-specificaties toe."""
        sizes = {
            self.SMALL: {"padding": "4px 12px", "font": "11px", "min_height": "24px"},
            self.MEDIUM: {"padding": "8px 16px", "font": "13px", "min_height": "32px"},
            self.LARGE: {"padding": "12px 24px", "font": "15px", "min_height": "40px"},
        }

        size_config = sizes.get(self._size, sizes[self.MEDIUM])

        # Base stylesheet
        self.setStyleSheet(f"""
            QPushButton {{
                padding: {size_config["padding"]};
                font-size: {size_config["font"]};
                min-height: {size_config["min_height"]};
                border-radius: 4px;
                font-weight: 500;
                outline: none;
            }}
        """)

    def _apply_variant(self):
        """Pas kleuren en states toe gebaseerd op variant."""
        # Kleuren per variant (normaal, hover, pressed, disabled)
        colors = {
            self.PRIMARY: {
                "bg": "#1890ff",
                "hover": "#40a9ff",
                "pressed": "#096dd9",
                "disabled": "#d9d9d9",
                "text": "#ffffff",
                "text_disabled": "#999999",
            },
            self.SECONDARY: {
                "bg": "#f0f0f0",
                "hover": "#e0e0e0",
                "pressed": "#d0d0d0",
                "disabled": "#f5f5f5",
                "text": "#333333",
                "text_disabled": "#999999",
            },
            self.DANGER: {
                "bg": "#ff4d4f",
                "hover": "#ff7875",
                "pressed": "#d9363e",
                "disabled": "#d9d9d9",
                "text": "#ffffff",
                "text_disabled": "#999999",
            },
            self.GHOST: {
                "bg": "transparent",
                "hover": "#f0f0f0",
                "pressed": "#e0e0e0",
                "disabled": "transparent",
                "text": "#333333",
                "text_disabled": "#999999",
                "border": "#d9d9d9",
            },
            self.SUCCESS: {
                "bg": "#52c41a",
                "hover": "#73d13d",
                "pressed": "#389e0d",
                "disabled": "#d9d9d9",
                "text": "#ffffff",
                "text_disabled": "#999999",
            },
            self.DEFAULT: {
                "bg": "#ffffff",
                "hover": "#f0f0f0",
                "pressed": "#e0e0e0",
                "disabled": "#f5f5f5",
                "text": "#333333",
                "text_disabled": "#999999",
                "border": "#d9d9d9",
            },
        }

        c = colors.get(self._variant, colors[self.DEFAULT])

        # Bouw stylesheet
        base = f"""
            QPushButton {{
                background-color: {c["bg"]};
                color: {c["text"]};
                border: 1px solid {c.get("border", c["bg"])};
            }}
            QPushButton:hover {{
                background-color: {c["hover"]};
                border-color: {c.get("border", c["hover"])};
            }}
            QPushButton:pressed {{
                background-color: {c["pressed"]};
                border-color: {c.get("border", c["pressed"])};
            }}
            QPushButton:disabled {{
                background-color: {c["disabled"]};
                color: {c["text_disabled"]};
                border-color: {c.get("border", c["disabled"])};
            }}
        """

        # Extra voor checked state (toggle buttons)
        if self.isCheckable():
            base += f"""
                QPushButton:checked {{
                    background-color: {c["pressed"]};
                    border-color: {c.get("border", c["pressed"])};
                }}
            """

        self.setStyleSheet(self.styleSheet() + base)

    def _update_icon_position(self):
        """Update icon positie (links of rechts)."""
        if self._icon_right:
            # Icon rechts: layoutDirection + custom style
            self.setLayoutDirection(Qt.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LeftToRight)

    def _start_spinner(self):
        """Start loading spinner animation."""
        if not self._spinner_timer:
            self._spinner_timer = QTimer(self)
            self._spinner_timer.timeout.connect(self._update_spinner)

        self._spinner_timer.start(100)  # Update elke 100ms
        self._spinner_frame = 0
        self.setEnabled(False)  # Disable tijdens loading

    def _stop_spinner(self):
        """Stop loading spinner."""
        if self._spinner_timer:
            self._spinner_timer.stop()
        self.setEnabled(True)
        self.setText(self._original_text)

    def _update_spinner(self):
        """Update spinner animatie frame."""
        spinners = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
        self._spinner_frame = (self._spinner_frame + 1) % len(spinners)
        self.setText(f"{spinners[self._spinner_frame]} {self._original_text}")

    # Public API

    def set_loading(self, loading: bool):
        """Set loading state."""
        self._loading = loading
        if loading:
            self._start_spinner()
        else:
            self._stop_spinner()

    def is_loading(self) -> bool:
        """Check if button is in loading state."""
        return self._loading

    def set_variant(self, variant: str):
        """Change button variant."""
        self._variant = variant
        self._apply_variant()

    def set_size(self, size: str):
        """Change button size."""
        self._size = size
        self._apply_size()

    def set_icon_right(self, right: bool):
        """Set icon position to right (True) or left (False)."""
        self._icon_right = right
        self._update_icon_position()

    # Properties voor QSS theming support

    @Property(str)
    def variant(self):
        return self._variant

    @variant.setter
    def variant(self, value):
        self.set_variant(value)

    @Property(str)
    def button_size(self):  # 'size' is reserved in Qt
        return self._size

    @button_size.setter
    def button_size(self, value):
        self.set_size(value)

    @Property(bool)
    def loading(self):
        return self._loading

    @loading.setter
    def loading(self, value):
        self.set_loading(value)


# Convenience factory functions voor snel gebruik


def create_primary_button(text: str, on_click=None, parent=None) -> Button:
    """Snel een primary button maken."""
    return Button(text, parent, variant=Button.PRIMARY, on_click=on_click)


def create_danger_button(text: str, on_click=None, parent=None) -> Button:
    """Snel een danger/delete button maken."""
    return Button(text, parent, variant=Button.DANGER, on_click=on_click)


def create_icon_button(
    icon: QIcon, tooltip: str = "", on_click=None, parent=None
) -> Button:
    """Snel een icon-only button maken."""
    btn = Button("", parent, variant=Button.GHOST, icon=icon, on_click=on_click)
    btn.setToolTip(tooltip)
    btn.setFixedSize(32, 32)
    return btn


def create_toggle_button(text: str, on_click=None, parent=None) -> Button:
    """Snel een toggle (aan/uit) button maken."""
    return Button(text, parent, toggle=True, checkable=True, on_click=on_click)
