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

Window {
    id: win

    property var widgetContext: null

    flags:  Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowDoesNotAcceptFocus
    color:  "transparent"
    width:  120
    height: 56

    // Position and visibility driven by context
    x:       widgetContext ? widgetContext.widgetX : 0
    y:       widgetContext ? widgetContext.widgetY : 0
    visible: widgetContext
        ? (
            widgetOverlayState.previewWidgetId === widgetContext.widgetId
            || (
                widgetOverlayState.overlayVisible
                && widgetContext.enabled
            )
        )
        : false

    readonly property bool _flashVisible: widgetContext ? widgetContext.textVisible : true
    readonly property string _flashTarget: widgetContext ? widgetContext.flashTarget : "value"

    // "widget" target: whole window fades in/out
    opacity: _flashTarget === "widget" ? (_flashVisible ? 1.0 : 0.0) : 1.0

    Rectangle {
        anchors.fill: parent
        color:        "#CC000000"
        radius:       6
    }

    Column {
        anchors.centerIn: parent
        spacing:          2
        // "text" target: label + value together fade
        opacity: win._flashTarget === "text" ? (win._flashVisible ? 1.0 : 0.0) : 1.0

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text:           win.widgetContext ? win.widgetContext.label : ""
            color:          "#888888"
            font.pixelSize: 10
            font.family:    "Segoe UI"
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text:           win.widgetContext ? win.widgetContext.text  : ""
            color:          win.widgetContext ? win.widgetContext.color : "#E0E0E0"
            // "value" target: only the number fades
            opacity:        win._flashTarget === "value" ? (win._flashVisible ? 1.0 : 0.0) : 1.0
            font.pixelSize: 22
            font.bold:      true
            font.family:    "Segoe UI"
        }
    }

    // Drag the window by clicking anywhere on it — OS handles the move natively
    MouseArea {
        anchors.fill: parent
        cursorShape:  pressed ? Qt.ClosedHandCursor : Qt.OpenHandCursor

        onPressed:  win.startSystemMove()
        onReleased: if (win.widgetContext) win.widgetContext.move(win.x, win.y)
    }
}
