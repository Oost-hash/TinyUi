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
    id: editRowRoot

    readonly property var hostWindow: Window.window
    property var theme: editRowRoot.hostWindow && editRowRoot.hostWindow.theme ? editRowRoot.hostWindow.theme : null
    property string label: ""
    property string description: ""
    property string value: ""
    default property alias rightContent: rightSlot.data

    function c(token, fallback) {
        return theme ? theme[token] : fallback;
    }

    function f(token, fallback) {
        return theme ? theme[token] : fallback;
    }

    anchors.left: parent ? parent.left : undefined
    anchors.right: parent ? parent.right : undefined
    implicitHeight: visible ? (description !== "" || value !== "" ? 52 : 44) : 0
    color: "transparent"

    Rectangle {
        anchors.fill: parent
        opacity: editRowHover.hovered ? 1 : 0
        Behavior on opacity {
            NumberAnimation {
                duration: 120
            }
        }
        gradient: Gradient {
            orientation: Gradient.Horizontal
            GradientStop {
                position: 0.0
                color: "transparent"
            }
            GradientStop {
                position: 0.5
                color: "transparent"
            }
            GradientStop {
                position: 1.0
                color: "#20dec184"
            }
        }
    }

    Rectangle {
        anchors.bottom: parent.bottom
        width: parent.width
        height: 1
        color: editRowRoot.c("border", "#464b57")
        opacity: 0.4
    }

    Column {
        anchors.left: parent.left
        anchors.leftMargin: 16
        anchors.right: rightSlot.left
        anchors.rightMargin: 8
        anchors.verticalCenter: parent.verticalCenter
        spacing: 3

        Text {
            width: parent.width
            text: editRowRoot.label
            color: editRowRoot.c("text", "#dce0e5")
            font.pixelSize: editRowRoot.f("fontSizeBase", 13)
            font.family: editRowRoot.f("fontFamily", "sans-serif")
            elide: Text.ElideRight
        }

        Text {
            width: parent.width
            visible: editRowRoot.description !== "" || editRowRoot.value !== ""
            text: editRowRoot.description !== "" ? editRowRoot.description : editRowRoot.value
            color: editRowHover.hovered ? "#dec184" : editRowRoot.c("textMuted", "#878a98")
            font.pixelSize: editRowRoot.f("fontSizeSmall", 11)
            font.family: editRowRoot.f("fontFamily", "sans-serif")
            elide: Text.ElideRight
            Behavior on color {
                ColorAnimation {
                    duration: 120
                }
            }
        }
    }

    Item {
        id: rightSlot
        anchors.right: parent.right
        anchors.rightMargin: 12
        anchors.verticalCenter: parent.verticalCenter
        width: 128
        height: parent.height
    }

    HoverHandler {
        id: editRowHover
    }
}
