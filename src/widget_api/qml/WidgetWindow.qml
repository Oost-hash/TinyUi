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
    id: root

    property var widgetData: ({})
    property var widgetConfigWrite: null
    property var widgetEffects: null

    x: widgetData && widgetData.x !== undefined ? widgetData.x : 0
    y: widgetData && widgetData.y !== undefined ? widgetData.y : 0

    width: 180
    height: 72
    visible: widgetData && widgetData.visible !== undefined ? widgetData.visible : true
    color: "transparent"
    flags: Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowDoesNotAcceptFocus
    title: widgetData && widgetData.widgetId ? widgetData.widgetId : "widget"
    transientParent: null

    TextWidget {
        anchors.fill: parent
        widgetData: root.widgetData
        widgetEffects: root.widgetEffects
    }

    // Drag the window by clicking anywhere on it — OS handles the move natively.
    // On release, the new position is written back to the config store.
    MouseArea {
        anchors.fill: parent
        cursorShape: pressed ? Qt.ClosedHandCursor : Qt.OpenHandCursor

        onPressed: root.startSystemMove()

        onReleased: {
            if (root.widgetConfigWrite && root.widgetData) {
                root.widgetConfigWrite.setWidgetPosition(
                    root.widgetData.overlayId,
                    root.widgetData.widgetId,
                    root.x,
                    root.y
                )
            }
        }
    }
}
