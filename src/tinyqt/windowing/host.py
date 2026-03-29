#  TinyUI
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
#  licensed under GPLv3.
"""Shared helpers for attaching platform windowing to a Qt host window."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Callable, Protocol, cast

from PySide6.QtQuick import QQuickWindow

from tinyqt.registration import SingletonRegistration
from tinyqt.windowing.controller_api import WindowControllerApi


class _ThemeLike(Protocol):
    def property(self, name: str) -> object: ...


@dataclass(frozen=True)
class WindowingAttachment:
    keepalive: tuple[object, ...]
    registrations: tuple[SingletonRegistration, ...]


def attach_windowing(
    *,
    app,
    window: QQuickWindow,
    theme: _ThemeLike,
    module: str = "TinyUI",
) -> WindowingAttachment:
    """Attach platform-specific windowing and return keepalive + singleton registrations."""
    dpr = app.devicePixelRatio()

    if sys.platform == "win32":
        from tinyqt.windowing.win_window import (
            WindowChromeHelper,
            WindowController,
            apply_dwm_frame,
            install_wnd_proc,
        )
        window_controller_cls = cast(type, WindowController)
        chrome_helper_cls = cast(type, WindowChromeHelper)

        hwnd = int(window.winId())
        wnd_proc, set_left = install_wnd_proc(
            hwnd,
            title_bar_height=round(cast(float, theme.property("titleBarHeight")) * dpr),
            resize_border=round(cast(float, theme.property("resizeBorder")) * dpr),
            resize_corner=round(cast(float, theme.property("resizeCorner")) * dpr),
            left_button_width=round(
                cast(float, theme.property("leftButtonWidth")) * dpr
            ),
            right_button_width=round(
                cast(float, theme.property("rightButtonWidth")) * dpr
            ),
        )
        set_left_width = cast(Callable[[int], None], set_left)
        apply_dwm_frame(hwnd)
        controller = window_controller_cls(
            hwnd, dpr=dpr, set_left_button_width=set_left_width
        )
        chrome_helper = chrome_helper_cls(dpr=dpr)
        return WindowingAttachment(
            keepalive=(wnd_proc, controller, chrome_helper),
            registrations=(
                SingletonRegistration(
                    chrome_helper_cls,
                    module,
                    "WindowChromeHelper",
                    chrome_helper,
                ),
                SingletonRegistration(
                    WindowControllerApi,
                    module,
                    "WindowController",
                    controller,
                ),
            ),
        )

    if sys.platform.startswith("linux") or sys.platform == "darwin":
        from tinyqt.windowing.unix_window import WindowController
        window_controller_cls = cast(type, WindowController)

        controller = window_controller_cls(window)
        return WindowingAttachment(
            keepalive=(controller,),
            registrations=(
                SingletonRegistration(
                    WindowControllerApi,
                    module,
                    "WindowController",
                    controller,
                ),
            ),
        )

    return WindowingAttachment(keepalive=(), registrations=())
