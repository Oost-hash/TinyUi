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
import QtQuick.Window

AbstractButton {
    id: btn

    readonly property var hostWindow: Window.window
    readonly property var hostTheme: hostWindow && hostWindow.theme ? hostWindow.theme : null

    property string iconText: ""
    property bool selected: false
    property string textFont: hostTheme ? hostTheme.fontFamily : "Segoe UI"
    readonly property color accentColor: hostTheme ? hostTheme.accent : "#74ADE8"
    readonly property color textColor: hostTheme ? hostTheme.text : "#FFFFFF"

    width: 28
    height: parent.height
    hoverEnabled: true

    background: Item {}

    contentItem: Text {
        text: btn.iconText
        font.family: btn.textFont
        font.pixelSize: 14
        color: btn.selected ? accentColor : textColor
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
}
