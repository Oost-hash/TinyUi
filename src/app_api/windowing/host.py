"""Shared helpers for attaching platform windowing to a Qt host window."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import Callable, Protocol, cast

from PySide6.QtCore import QObject
from PySide6.QtQuick import QQuickWindow

from app_api.windowing.controller_api import WindowControllerApi


@dataclass(frozen=True)
class WindowingAttachment:
    keepalive: tuple[object, ...]
    controller: object | None = None


def attach_windowing(
    *,
    app,
    window: QQuickWindow,
    theme: QObject,
) -> WindowingAttachment:
    """Attach platform-specific windowing and return keepalive + controller."""
    dpr = app.devicePixelRatio()

    if sys.platform == "win32":
        from app_api.windowing.win_window import (
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
            left_button_width=round(cast(float, theme.property("leftButtonWidth")) * dpr),
            right_button_width=round(cast(float, theme.property("rightButtonWidth")) * dpr),
        )
        set_left_width = cast(Callable[[int], None], set_left)
        apply_dwm_frame(hwnd)
        controller = window_controller_cls(
            hwnd, dpr=dpr, set_left_button_width=set_left_width
        )
        chrome_helper = chrome_helper_cls(dpr=dpr)
        return WindowingAttachment(
            keepalive=(wnd_proc, controller, chrome_helper),
            controller=controller,
        )

    if sys.platform.startswith("linux") or sys.platform == "darwin":
        from app_api.windowing.unix_window import WindowController
        window_controller_cls = cast(type, WindowController)

        controller = window_controller_cls(window)
        return WindowingAttachment(
            keepalive=(controller,),
            controller=controller,
        )

    return WindowingAttachment(keepalive=())
