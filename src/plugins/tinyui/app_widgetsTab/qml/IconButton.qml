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
import QtQuick.Window

Rectangle {
    id: iconButtonRoot

    readonly property var hostWindow: Window.window
    property var theme: iconButtonRoot.hostWindow && iconButtonRoot.hostWindow.theme ? iconButtonRoot.hostWindow.theme : null
    property url iconSource: ""
    signal clicked

    function c(token, fallback) {
        return theme ? theme[token] : fallback;
    }

    width: 28
    height: 28
    radius: 4
    color: iconButtonHover.hovered ? iconButtonRoot.c("surfaceRaised", "#3b414d") : "transparent"
    border.width: 1
    border.color: iconButtonHover.hovered ? iconButtonRoot.c("accent", "#4a9eff") : iconButtonRoot.c("border", "#464b57")
    opacity: enabled ? 1.0 : 0.45
    Behavior on color {
        ColorAnimation {
            duration: 80
        }
    }
    Behavior on border.color {
        ColorAnimation {
            duration: 80
        }
    }

    Image {
        anchors.centerIn: parent
        width: 16
        height: 16
        source: iconButtonRoot.iconSource
        sourceSize.width: 16
        sourceSize.height: 16
        fillMode: Image.PreserveAspectFit
        opacity: iconButtonHover.hovered ? 1.0 : 0.75
        Behavior on opacity {
            NumberAnimation {
                duration: 80
            }
        }
    }

    MouseArea {
        anchors.fill: parent
        enabled: iconButtonRoot.enabled
        onClicked: iconButtonRoot.clicked()
    }

    HoverHandler {
        id: iconButtonHover
    }
}
