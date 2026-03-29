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

"""
Win32/DWM custom window chrome for PySide6 on Windows.

Approach based on the Microsoft DWM Custom Frame documentation and
FramelessHelper/QWindowKit reference implementations:

  - WM_NCCALCSIZE: remove left/right/bottom NC borders, keep top intact
    for DWM caption -> client area covers the title bar visually, DWM
    reserves space for caption buttons.
  - WM_NCHITTEST: call DwmDefWindowProc FIRST - DWM recognizes button
    zones itself, draws hover/pressed states and triggers the Win11
    snap-layout popup. Then apply own hit-test for resize and drag zone.
  - WM_NCLBUTTONUP: click handling for caption buttons via ShowWindow
    (native animations).

Provides:
  - Aero snap + native maximize/restore/minimize animations
  - Native caption buttons (close/max/min) with DWM hover effect and
    Windows 11 snap-layout popup
  - Resize via Windows native hit-testing
  - Alt+Tab thumbnails / taskbar preview
"""

import ctypes
import ctypes.wintypes

from PySide6.QtCore import QObject, Slot
from PySide6.QtGui import QWindow
from PySide6.QtQml import QmlElement, QmlSingleton

from tinyqt.windowing.controller_api import WindowControllerApi

QML_IMPORT_NAME = "TinyUI"
QML_IMPORT_MAJOR_VERSION = 1

# -- Win32 constants ----------------------------------------------------------

GWL_STYLE        = -16
GWLP_WNDPROC     = -4
WS_CAPTION       = 0x00C00000
WS_SYSMENU       = 0x00080000
WS_MINIMIZEBOX   = 0x00020000
WS_MAXIMIZEBOX   = 0x00010000
WS_THICKFRAME    = 0x00040000
SWP_NOMOVE       = 0x0002
SWP_NOSIZE       = 0x0001
SWP_NOZORDER     = 0x0004
SWP_FRAMECHANGED = 0x0020
SWP_NOACTIVATE   = 0x0010

SM_CXFRAME        = 32
SM_CYFRAME        = 33
SM_CXPADDEDBORDER = 92

DWMWA_USE_IMMERSIVE_DARK_MODE  = 20
DWMWA_WINDOW_CORNER_PREFERENCE = 33
DWMWCP_ROUND                   = 2

WM_CLOSE           = 0x0010
WM_NCCALCSIZE      = 0x0083
WM_NCHITTEST       = 0x0084
WM_NCLBUTTONUP     = 0x00A2
WM_NCLBUTTONDBLCLK = 0x00A3

SW_MAXIMIZE = 3
SW_MINIMIZE = 6
SW_RESTORE  = 9

HTCLIENT      = 1
HTCAPTION     = 2
HTLEFT        = 10
HTRIGHT       = 11
HTTOP         = 12
HTTOPLEFT     = 13
HTTOPRIGHT    = 14
HTBOTTOM      = 15
HTBOTTOMLEFT  = 16
HTBOTTOMRIGHT = 17
HTMINBUTTON   = 8
HTMAXBUTTON   = 9
HTCLOSE       = 20


class MARGINS(ctypes.Structure):
    _fields_ = [
        ("cxLeftWidth",    ctypes.c_int),
        ("cxRightWidth",   ctypes.c_int),
        ("cyTopHeight",    ctypes.c_int),
        ("cyBottomHeight", ctypes.c_int),
    ]


class RECT(ctypes.Structure):
    _fields_ = [
        ("left",   ctypes.c_long),
        ("top",    ctypes.c_long),
        ("right",  ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]


class NCCALCSIZE_PARAMS(ctypes.Structure):
    _fields_ = [
        ("rgrc",  RECT * 3),
        ("lppos", ctypes.c_void_p),
    ]


_WndProcType = ctypes.WINFUNCTYPE(
    ctypes.c_ssize_t,
    ctypes.c_size_t,
    ctypes.c_uint,
    ctypes.c_size_t,
    ctypes.c_ssize_t,
)


def apply_dwm_frame(hwnd: int) -> None:
    """
    Add window styles so Windows handles native resize, snap and shadow.
    WndProc must be installed before this call so that WM_NCCALCSIZE
    (triggered by SWP_FRAMECHANGED) is intercepted immediately.
    """
    user32 = ctypes.windll.user32
    dwmapi = ctypes.windll.dwmapi

    style = user32.GetWindowLongW(hwnd, GWL_STYLE)
    style |= WS_CAPTION | WS_SYSMENU | WS_MINIMIZEBOX | WS_MAXIMIZEBOX | WS_THICKFRAME
    user32.SetWindowLongW(hwnd, GWL_STYLE, style)

    user32.SetWindowPos(
        hwnd, None, 0, 0, 0, 0,
        SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED | SWP_NOACTIVATE,
    )

    attr = ctypes.c_int(DWMWCP_ROUND)
    dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_WINDOW_CORNER_PREFERENCE, ctypes.byref(attr), ctypes.sizeof(attr))


def install_wnd_proc(
    hwnd: int,
    *,
    title_bar_height:   int = 32,
    resize_border:      int = 8,
    resize_corner:      int = 20,
    left_button_width:  int = 44,
    right_button_width: int = 142,
):
    """
    Subclass the WndProc for WM_NCCALCSIZE, WM_NCHITTEST and WM_NCLBUTTONDBLCLK.

    Returns (wnd_proc, set_left_button_width):
      - wnd_proc               : MUST be kept alive, otherwise garbage collected -> crash
      - set_left_button_width  : callable(pixels: int) to update the left zone at runtime

    Parameters (physical pixels, i.e. DPI-scaled):
      title_bar_height   : height of the title bar
      resize_border      : width of resize edge along the borders
      resize_corner      : size of resize zone at corners
      left_button_width  : initial width of left zone (hamburger + title + menu -> HTCLIENT)
      right_button_width : width of right zone (QML buttons -> HTCLIENT)
    """
    user32  = ctypes.windll.user32
    dwmapi  = ctypes.windll.dwmapi

    dwmapi.DwmDefWindowProc.restype  = ctypes.c_bool
    dwmapi.DwmDefWindowProc.argtypes = [
        ctypes.c_size_t,
        ctypes.c_uint,
        ctypes.c_size_t,
        ctypes.c_ssize_t,
        ctypes.POINTER(ctypes.c_ssize_t),
    ]

    user32.GetWindowLongPtrW.restype  = ctypes.c_ssize_t
    user32.GetWindowLongPtrW.argtypes = [ctypes.c_size_t, ctypes.c_int]

    user32.SetWindowLongPtrW.restype  = ctypes.c_ssize_t
    user32.SetWindowLongPtrW.argtypes = [ctypes.c_size_t, ctypes.c_int, ctypes.c_ssize_t]

    user32.CallWindowProcW.restype  = ctypes.c_ssize_t
    user32.CallWindowProcW.argtypes = [
        ctypes.c_ssize_t,
        ctypes.c_size_t,
        ctypes.c_uint,
        ctypes.c_size_t,
        ctypes.c_ssize_t,
    ]

    old_proc = user32.GetWindowLongPtrW(hwnd, GWLP_WNDPROC)
    _left = [left_button_width]

    def set_left_button_width(pixels: int) -> None:
        _left[0] = pixels

    def _hit_test(h: int, lparam: int) -> int | None:
        """Resize borders and title bar. Caption buttons are handled by DwmDefWindowProc."""
        x = ctypes.c_short(lparam & 0xFFFF).value
        y = ctypes.c_short((lparam >> 16) & 0xFFFF).value

        rect = RECT()
        user32.GetWindowRect(h, ctypes.byref(rect))

        rx = x - rect.left
        ry = y - rect.top
        w  = rect.right  - rect.left
        h_ = rect.bottom - rect.top

        if ry < title_bar_height:
            if rx < _left[0]:
                return HTCLIENT
            if rx > w - right_button_width:
                return HTCLIENT
            return HTCAPTION

        if user32.IsZoomed(h):
            return None

        rb = resize_border
        rc = resize_corner

        if rx < rc and ry < rc:
            return HTTOPLEFT
        if rx > w - rc and ry < rc:
            return HTTOPRIGHT
        if rx < rc and ry > h_ - rc:
            return HTBOTTOMLEFT
        if rx > w - rc and ry > h_ - rc:
            return HTBOTTOMRIGHT

        if ry < rb:
            return HTTOP
        if ry > h_ - rb:
            return HTBOTTOM
        if rx < rb:
            return HTLEFT
        if rx > w - rb:
            return HTRIGHT

        return None

    @_WndProcType
    def wnd_proc(h: int, msg: int, wparam: int, lparam: int) -> int:
        dwm_result = ctypes.c_ssize_t(0)
        if dwmapi.DwmDefWindowProc(h, msg, wparam, lparam, ctypes.byref(dwm_result)):
            return dwm_result.value

        if msg == WM_NCCALCSIZE and wparam:
            if user32.IsZoomed(h):
                nccsp    = ctypes.cast(lparam, ctypes.POINTER(NCCALCSIZE_PARAMS))
                padding  = user32.GetSystemMetrics(SM_CXPADDEDBORDER)
                border_x = user32.GetSystemMetrics(SM_CXFRAME) + padding
                border_y = user32.GetSystemMetrics(SM_CYFRAME) + padding
                nccsp.contents.rgrc[0].left   += border_x
                nccsp.contents.rgrc[0].right  -= border_x
                nccsp.contents.rgrc[0].top    += border_y
                nccsp.contents.rgrc[0].bottom -= border_y
            return 0

        elif msg == WM_NCHITTEST:
            hit = _hit_test(h, lparam)
            if hit is not None:
                return hit

        elif msg == WM_NCLBUTTONDBLCLK and wparam == HTCAPTION:
            user32.ShowWindow(h, SW_RESTORE if user32.IsZoomed(h) else SW_MAXIMIZE)
            return 0

        return user32.CallWindowProcW(old_proc, h, msg, wparam, lparam)

    wnd_proc_ptr = ctypes.cast(wnd_proc, ctypes.c_void_p).value
    result = user32.SetWindowLongPtrW(hwnd, GWLP_WNDPROC, wnd_proc_ptr)
    if result == 0:
        print(f"[win32] ERROR: SetWindowLongPtrW failed! LastError={ctypes.windll.kernel32.GetLastError()}")
    return wnd_proc, set_left_button_width


@QmlElement
@QmlSingleton
class WindowChromeHelper(QObject):
    """Apply Win32 DWM chrome to secondary windows (dialogs)."""

    def __init__(self, dpr: float, parent=None):
        super().__init__(parent)
        self._dpr        = dpr
        self._applied:   set[int]  = set()
        self._wnd_procs: list      = []

    def _apply(self, hwnd: int) -> None:
        if hwnd in self._applied:
            return
        self._applied.add(hwnd)
        wnd_proc, _ = install_wnd_proc(
            hwnd,
            title_bar_height=round(36 * self._dpr),
            resize_border=round(6 * self._dpr),
            resize_corner=round(12 * self._dpr),
            left_button_width=0,
            right_button_width=round(138 * self._dpr),
        )
        apply_dwm_frame(hwnd)
        self._wnd_procs.append(wnd_proc)

    @Slot(QWindow)
    def applyToWindow(self, window: QWindow) -> None:
        """Called from QML: windowChromeHelper.applyToWindow(someWindow)."""
        self._apply(int(window.winId()))

    @Slot(int)
    def applyTo(self, win_id: int) -> None:
        """Called from Python with a known HWND."""
        self._apply(int(win_id))


class WindowController(WindowControllerApi):
    """Programmatic window control via ShowWindow (native animations)."""

    def __init__(self, hwnd: int, dpr: float, set_left_button_width, parent=None):
        super().__init__(parent)
        self._hwnd   = hwnd
        self._user32 = ctypes.windll.user32
        self._dpr    = dpr
        self._set_left = set_left_button_width

    @Slot(float)
    def setLeftButtonWidth(self, logical_width: float) -> None:
        """Called from QML when the left title bar zone changes width."""
        self._set_left(round(logical_width * self._dpr))

    @Slot()
    def toggleMaximize(self):
        sw = SW_RESTORE if self._user32.IsZoomed(self._hwnd) else SW_MAXIMIZE
        self._user32.ShowWindow(self._hwnd, sw)

    @Slot()
    def minimize(self):
        self._user32.ShowWindow(self._hwnd, SW_MINIMIZE)
