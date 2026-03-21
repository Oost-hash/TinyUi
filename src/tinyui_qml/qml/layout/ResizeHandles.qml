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

import QtQuick

// Resize-zones voor Linux/Wayland. Elke zone start een compositor-resize
// via windowController.startResize(edge) zodra de DragHandler actief wordt.
// Op Windows worden resize en hit-testing afgehandeld door WndProc — dit
// component is dan onzichtbaar en inactief.

Item {
    anchors.fill: parent
    z: 20

    readonly property int b: 8   // rand-breedte
    readonly property int c: 16  // hoek-grootte

    // ── Hoeken ────────────────────────────────────────────────────────────

    Item {
        x: 0; y: 0; width: c; height: c
        HoverHandler { cursorShape: Qt.SizeFDiagCursor }
        DragHandler  { target: null; onActiveChanged: if (active) windowController.startResize(Qt.TopEdge    | Qt.LeftEdge)  }
    }
    Item {
        x: parent.width - c; y: 0; width: c; height: c
        HoverHandler { cursorShape: Qt.SizeBDiagCursor }
        DragHandler  { target: null; onActiveChanged: if (active) windowController.startResize(Qt.TopEdge    | Qt.RightEdge) }
    }
    Item {
        x: 0; y: parent.height - c; width: c; height: c
        HoverHandler { cursorShape: Qt.SizeBDiagCursor }
        DragHandler  { target: null; onActiveChanged: if (active) windowController.startResize(Qt.BottomEdge | Qt.LeftEdge)  }
    }
    Item {
        x: parent.width - c; y: parent.height - c; width: c; height: c
        HoverHandler { cursorShape: Qt.SizeFDiagCursor }
        DragHandler  { target: null; onActiveChanged: if (active) windowController.startResize(Qt.BottomEdge | Qt.RightEdge) }
    }

    // ── Randen ────────────────────────────────────────────────────────────

    Item {
        x: c; y: 0; width: parent.width - 2 * c; height: b
        HoverHandler { cursorShape: Qt.SizeVerCursor }
        DragHandler  { target: null; onActiveChanged: if (active) windowController.startResize(Qt.TopEdge)    }
    }
    Item {
        x: c; y: parent.height - b; width: parent.width - 2 * c; height: b
        HoverHandler { cursorShape: Qt.SizeVerCursor }
        DragHandler  { target: null; onActiveChanged: if (active) windowController.startResize(Qt.BottomEdge) }
    }
    Item {
        x: 0; y: c; width: b; height: parent.height - 2 * c
        HoverHandler { cursorShape: Qt.SizeHorCursor }
        DragHandler  { target: null; onActiveChanged: if (active) windowController.startResize(Qt.LeftEdge)   }
    }
    Item {
        x: parent.width - b; y: c; width: b; height: parent.height - 2 * c
        HoverHandler { cursorShape: Qt.SizeHorCursor }
        DragHandler  { target: null; onActiveChanged: if (active) windowController.startResize(Qt.RightEdge)  }
    }
}
