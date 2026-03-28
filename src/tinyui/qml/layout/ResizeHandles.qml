//  TinyUI
//  Copyright (C) 2026 Oost-hash
//
//  This file is part of TinyUI.
//
//  TinyUI is free software: you can redistribute it and/or modify
//  it under the terms of the GNU General Public License as published by
//  the Free Software Foundation, either version 3 of the License, or
//  (at your option) any later version.
//
//  TinyUI is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU General Public License for more details.
//
//  You should have received a copy of the GNU General Public License
//  along with this program.  If not, see <https://www.gnu.org/licenses/>.
//
//  TinyUI builds on TinyPedal by s-victor (https://github.com/s-victor/TinyPedal),
//  licensed under GPLv3.

pragma ComponentBehavior: Bound

import QtQuick
import TinyUI

// Resize zones for Linux/Wayland. Each zone starts a compositor-driven resize
// via WindowController.startResize(edge) as soon as the DragHandler activates.
// On Windows, resize and hit-testing are handled by WndProc — this component
// is invisible and inactive there.

Item {
    id: resizeHandles
    anchors.fill: parent
    z: 20

    readonly property int b: 8   // rand-breedte
    readonly property int c: 16  // hoek-grootte

    // ── Hoeken ────────────────────────────────────────────────────────────

    Item {
        x: 0; y: 0; width: resizeHandles.c; height: resizeHandles.c
        HoverHandler { cursorShape: Qt.SizeFDiagCursor }
        DragHandler  { target: null; onActiveChanged: if (active) WindowController.startResize(Qt.TopEdge    | Qt.LeftEdge)  }
    }
    Item {
        x: resizeHandles.width - resizeHandles.c; y: 0; width: resizeHandles.c; height: resizeHandles.c
        HoverHandler { cursorShape: Qt.SizeBDiagCursor }
        DragHandler  { target: null; onActiveChanged: if (active) WindowController.startResize(Qt.TopEdge    | Qt.RightEdge) }
    }
    Item {
        x: 0; y: resizeHandles.height - resizeHandles.c; width: resizeHandles.c; height: resizeHandles.c
        HoverHandler { cursorShape: Qt.SizeBDiagCursor }
        DragHandler  { target: null; onActiveChanged: if (active) WindowController.startResize(Qt.BottomEdge | Qt.LeftEdge)  }
    }
    Item {
        x: resizeHandles.width - resizeHandles.c; y: resizeHandles.height - resizeHandles.c; width: resizeHandles.c; height: resizeHandles.c
        HoverHandler { cursorShape: Qt.SizeFDiagCursor }
        DragHandler  { target: null; onActiveChanged: if (active) WindowController.startResize(Qt.BottomEdge | Qt.RightEdge) }
    }

    // ── Randen ────────────────────────────────────────────────────────────

    Item {
        x: resizeHandles.c; y: 0; width: resizeHandles.width - 2 * resizeHandles.c; height: resizeHandles.b
        HoverHandler { cursorShape: Qt.SizeVerCursor }
        DragHandler  { target: null; onActiveChanged: if (active) WindowController.startResize(Qt.TopEdge)    }
    }
    Item {
        x: resizeHandles.c; y: resizeHandles.height - resizeHandles.b; width: resizeHandles.width - 2 * resizeHandles.c; height: resizeHandles.b
        HoverHandler { cursorShape: Qt.SizeVerCursor }
        DragHandler  { target: null; onActiveChanged: if (active) WindowController.startResize(Qt.BottomEdge) }
    }
    Item {
        x: 0; y: resizeHandles.c; width: resizeHandles.b; height: resizeHandles.height - 2 * resizeHandles.c
        HoverHandler { cursorShape: Qt.SizeHorCursor }
        DragHandler  { target: null; onActiveChanged: if (active) WindowController.startResize(Qt.LeftEdge)   }
    }
    Item {
        x: resizeHandles.width - resizeHandles.b; y: resizeHandles.c; width: resizeHandles.b; height: resizeHandles.height - 2 * resizeHandles.c
        HoverHandler { cursorShape: Qt.SizeHorCursor }
        DragHandler  { target: null; onActiveChanged: if (active) WindowController.startResize(Qt.RightEdge)  }
    }
}
