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

AbstractButton {
    id: btn
    property string iconText: ""
    property bool selected: false

    width: 28
    height: parent.height
    hoverEnabled: true

    background: Item {}

    contentItem: Item {
        Rectangle {
            anchors.centerIn: parent
            width: 22
            height: 22
            radius: 4
            color: btn.hovered ? theme.surfaceFloating : "transparent"
        }

        Text {
            anchors.centerIn: parent
            text: btn.iconText
            font.family: "Segoe Fluent Icons"
            font.pixelSize: 14
            color: btn.selected ? theme.accent : "#FFFFFF"
        }
    }
}
