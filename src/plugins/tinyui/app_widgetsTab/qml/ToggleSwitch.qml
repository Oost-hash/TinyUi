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

Item {
    id: toggleRoot

    property var theme: Window.window && Window.window.theme ? Window.window.theme : null
    property bool checked: false
    signal toggled(bool checked)

    function c(token, fallback) {
        return theme ? theme[token] : fallback;
    }

    width: 34
    height: 18
    opacity: enabled ? 1 : 0.45

    Rectangle {
        anchors.fill: parent
        radius: height / 2
        color: toggleRoot.checked ? toggleRoot.c("accent", "#4a9eff") : toggleRoot.c("surfaceFloating", "#20242b")
        border.width: 1
        border.color: toggleRoot.checked ? toggleRoot.c("accentHover", "#6bb6ff") : toggleRoot.c("border", "#464b57")
        Behavior on color {
            ColorAnimation {
                duration: 100
            }
        }
        Behavior on border.color {
            ColorAnimation {
                duration: 100
            }
        }
    }

    Rectangle {
        width: 14
        height: 14
        radius: 7
        y: 2
        x: toggleRoot.checked ? toggleRoot.width - width - 2 : 2
        color: toggleRoot.checked ? toggleRoot.c("accentText", "#ffffff") : toggleRoot.c("textMuted", "#878a98")
        Behavior on x {
            NumberAnimation {
                duration: 120
                easing.type: Easing.OutCubic
            }
        }
        Behavior on color {
            ColorAnimation {
                duration: 100
            }
        }
    }

    MouseArea {
        anchors.fill: parent
        enabled: toggleRoot.enabled
        onClicked: {
            toggleRoot.checked = !toggleRoot.checked;
            toggleRoot.toggled(toggleRoot.checked);
        }
    }
}
