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
import QtQuick.Controls

// Herbruikbaar popup component voor menu dropdowns in de TitleBar.
// Biedt standaard fade+slide animaties en achtergrond (3-zijdige border, geen bovenkant).
// slideDown: true = slide naar beneden (TitleBar dropdowns), false = slide naar boven (StatusBar)
Popup {
    id: popup

    property bool slideDown: true

    padding: 0
    dim: false                              // geen overlay — voorkomt dat hover gestolen wordt
    closePolicy: Popup.NoAutoClose          // Python beheert visibility via property binding

    enter: Transition {
        ParallelAnimation {
            NumberAnimation { property: "opacity"; from: 0; to: 1; duration: 150; easing.type: Easing.OutCubic }
            NumberAnimation {
                property: "y"
                from: popup.slideDown ? popup.y - 8 : popup.y + 8
                to: popup.y
                duration: 150
                easing.type: Easing.OutCubic
            }
        }
    }
    exit: Transition {
        ParallelAnimation {
            NumberAnimation { property: "opacity"; from: 1; to: 0; duration: 100; easing.type: Easing.InCubic }
            NumberAnimation {
                property: "y"
                from: popup.y
                to: popup.slideDown ? popup.y - 8 : popup.y + 8
                duration: 100
                easing.type: Easing.InCubic
            }
        }
    }

    background: Item {
        Rectangle { anchors.fill: parent; color: theme.surfaceAlt }
        // Borders links, onder, rechts — geen bovenkant (grenst aan titlebar onderkant)
        Rectangle { anchors.left: parent.left;    width: 1; height: parent.height; color: theme.border }
        Rectangle { anchors.bottom: parent.bottom; height: 1; width: parent.width; color: theme.border }
        Rectangle { anchors.right: parent.right;  width: 1; height: parent.height; color: theme.border }
    }
}
