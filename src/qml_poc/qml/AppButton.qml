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

Button {
    id: btn
    property bool primary: false

    leftPadding: 20
    rightPadding: 20
    topPadding: 10
    bottomPadding: 10

    background: Rectangle {
        radius: 6
        color: {
            if (btn.primary) {
                return btn.pressed ? theme.accentPressed
                     : btn.hovered ? theme.accentHover
                     : theme.accent
            }
            return btn.pressed ? theme.surface
                 : btn.hovered ? theme.surfaceFloating
                 : theme.surfaceRaised
        }

        Behavior on color {
            ColorAnimation { duration: 80 }
        }
    }

    contentItem: Text {
        text: btn.text
        color: btn.primary ? theme.accentText : theme.text
        font.pixelSize: theme.fontSizeBase
        font.family: theme.fontFamily
        font.weight: Font.Medium
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
}
