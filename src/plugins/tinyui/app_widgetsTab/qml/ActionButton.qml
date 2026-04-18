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
    id: actionButtonRoot

    property var theme: Window.window && Window.window.theme ? Window.window.theme : null
    property string label: ""
    signal clicked

    function c(token, fallback) {
        return theme ? theme[token] : fallback;
    }

    function f(token, fallback) {
        return theme ? theme[token] : fallback;
    }

    width: 82
    height: 28
    radius: 4
    color: actionButtonHover.hovered ? actionButtonRoot.c("surfaceRaised", "#3b414d") : actionButtonRoot.c("surfaceFloating", "#20242b")
    border.width: 1
    border.color: actionButtonHover.hovered ? actionButtonRoot.c("accent", "#4a9eff") : actionButtonRoot.c("border", "#464b57")
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

    Text {
        anchors.centerIn: parent
        text: actionButtonRoot.label
        color: actionButtonHover.hovered ? actionButtonRoot.c("accent", "#4a9eff") : actionButtonRoot.c("text", "#dce0e5")
        font.pixelSize: actionButtonRoot.f("fontSizeSmall", 11)
        font.family: actionButtonRoot.f("fontFamily", "sans-serif")
    }

    MouseArea {
        anchors.fill: parent
        enabled: actionButtonRoot.enabled
        onClicked: actionButtonRoot.clicked()
    }

    HoverHandler {
        id: actionButtonHover
    }
}
