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
Win32/DWM custom window chrome voor PySide6 op Windows.

Aanpak gebaseerd op de Microsoft DWM Custom Frame documentatie en
FramelessHelper/QWindowKit referentie-implementaties:

  - WM_NCCALCSIZE: verwijder left/right/bottom NC-borders maar laat top
    intact → client-area bedekt de titelbalk visueel, DWM behoudt ruimte
    voor caption-knoppen.
  - WM_NCHITTEST: roep DwmDefWindowProc EERST aan — DWM herkent de knop-
    zones zelf, tekent hover/pressed states en triggert de Win11 snap-layout
    popup. Pas daarna eigen hit-test voor resize en drag-zone.
  - WM_NCLBUTTONUP: klik-afhandeling voor caption-knoppen via ShowWindow
    (native animaties).

Geeft:
  - Aero snap + native maximize/restore/minimize animaties
  - Native caption buttons (close/max/min) met DWM hover-effect en
    Windows 11 snap-layout popup
  - Resize via Windows native hit-testing
  - Alt+Tab thumbnails / taskbalk preview
"""

import ctypes
import ctypes.wintypes

from PySide6.QtCore import QObject, Slot

# ── Win32 constanten ──────────────────────────────────────────────────────────

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


# ── ctypes structuren ─────────────────────────────────────────────────────────

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


# WndProc function type: LRESULT CALLBACK(HWND, UINT, WPARAM, LPARAM)
_WndProcType = ctypes.WINFUNCTYPE(
    ctypes.c_ssize_t,
    ctypes.c_size_t,
    ctypes.c_uint,
    ctypes.c_size_t,
    ctypes.c_ssize_t,
)


# ── Publieke API ──────────────────────────────────────────────────────────────

def apply_dwm_frame(hwnd: int) -> None:
    """
    Voeg window-stijlen toe zodat Windows native resize, snap en shadow regelt.
    WndProc moet al geïnstalleerd zijn vóór deze aanroep zodat
    WM_NCCALCSIZE (getriggerd door SWP_FRAMECHANGED) direct onderschept wordt.
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

    # Afgeronde hoeken (Windows 11+, genegeerd op Win10)
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
    Subclasst de WndProc voor WM_NCCALCSIZE, WM_NCHITTEST en WM_NCLBUTTONDBLCLK.

    Geeft (wnd_proc, set_left_button_width) terug:
      - wnd_proc               : MOET bewaard blijven, anders garbage collected → crash
      - set_left_button_width  : callable(pixels: int) om de linker zone live bij te werken

    Parameters (fysieke pixels, dus DPI-geschaald):
      title_bar_height   : hoogte van de titelbalk
      resize_border      : breedte resize-rand langs randen
      resize_corner      : grootte resize-zone in hoeken
      left_button_width  : initiële breedte linker zone (hamburger + titel + menu → HTCLIENT)
      right_button_width : breedte rechter zone (QML-knoppen → HTCLIENT)
    """
    user32  = ctypes.windll.user32
    dwmapi  = ctypes.windll.dwmapi

    # DwmDefWindowProc signatuur
    dwmapi.DwmDefWindowProc.restype  = ctypes.c_bool
    dwmapi.DwmDefWindowProc.argtypes = [
        ctypes.c_size_t,                      # HWND
        ctypes.c_uint,                        # UINT
        ctypes.c_size_t,                      # WPARAM
        ctypes.c_ssize_t,                     # LPARAM
        ctypes.POINTER(ctypes.c_ssize_t),     # LRESULT*
    ]

    # Expliciete 64-bit signaturen voor SetWindowLongPtrW / CallWindowProcW
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

    # Mutable container zodat de linker zone live bijgewerkt kan worden vanuit QML
    _left = [left_button_width]

    def set_left_button_width(pixels: int) -> None:
        _left[0] = pixels

    def _hit_test(h: int, lparam: int) -> int | None:
        """Resize-borders en titelbalk. Caption-knoppen worden door DwmDefWindowProc afgehandeld."""
        x = ctypes.c_short(lparam & 0xFFFF).value
        y = ctypes.c_short((lparam >> 16) & 0xFFFF).value

        rect = RECT()
        user32.GetWindowRect(h, ctypes.byref(rect))

        rx = x - rect.left
        ry = y - rect.top
        w  = rect.right  - rect.left
        h_ = rect.bottom - rect.top

        # Titelbalk-zone
        if ry < title_bar_height:
            if rx < _left[0]:                 return HTCLIENT   # linker knoppen
            if rx > w - right_button_width:   return HTCLIENT   # QML-knoppen
            return HTCAPTION                                    # drag zone

        if user32.IsZoomed(h):
            return None            # geen resize als gemaximaliseerd

        rb = resize_border
        rc = resize_corner

        if rx < rc  and ry < rc:           return HTTOPLEFT
        if rx > w-rc and ry < rc:          return HTTOPRIGHT
        if rx < rc  and ry > h_-rc:        return HTBOTTOMLEFT
        if rx > w-rc and ry > h_-rc:       return HTBOTTOMRIGHT

        if ry < rb:        return HTTOP
        if ry > h_ - rb:   return HTBOTTOM
        if rx < rb:        return HTLEFT
        if rx > w  - rb:   return HTRIGHT

        return None

    @_WndProcType
    def wnd_proc(h: int, msg: int, wparam: int, lparam: int) -> int:
        # ── DwmDefWindowProc eerst ────────────────────────────────────────────
        # Vereist voor caption-knop hover, pressed-states en snap-layout popup.
        dwm_result = ctypes.c_ssize_t(0)
        if dwmapi.DwmDefWindowProc(h, msg, wparam, lparam, ctypes.byref(dwm_result)):
            return dwm_result.value

        # ── Eigen afhandeling ─────────────────────────────────────────────────
        if msg == WM_NCCALCSIZE and wparam:
            # Normaal venster: geen NC-aanpassing — client-area = volledig venster.
            # Gemaximaliseerd: Windows plaatst het venster border_x/border_y buiten
            # de schermrand; corrigeer alle zijden zodat content binnen het scherm blijft.
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
        print(f"[win32] FOUT: SetWindowLongPtrW mislukt! LastError={ctypes.windll.kernel32.GetLastError()}")
    return wnd_proc, set_left_button_width  # wnd_proc BEWAREN — anders garbage collected → crash


class WindowController(QObject):
    """Programmatische vensterbesturing via ShowWindow (native animaties)."""

    def __init__(self, hwnd: int, dpr: float, set_left_button_width, parent=None):
        super().__init__(parent)
        self._hwnd   = hwnd
        self._user32 = ctypes.windll.user32
        self._dpr    = dpr
        self._set_left = set_left_button_width

    @Slot(float)
    def setLeftButtonWidth(self, logical_width: float) -> None:
        """Wordt aangeroepen vanuit QML als de linker titelbalk-zone van breedte verandert."""
        self._set_left(round(logical_width * self._dpr))

    @Slot()
    def toggleMaximize(self):
        sw = SW_RESTORE if self._user32.IsZoomed(self._hwnd) else SW_MAXIMIZE
        self._user32.ShowWindow(self._hwnd, sw)

    @Slot()
    def minimize(self):
        self._user32.ShowWindow(self._hwnd, SW_MINIMIZE)
