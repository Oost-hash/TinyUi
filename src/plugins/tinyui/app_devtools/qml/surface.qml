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
    id: root

    property var hostWindow: Window.window
    property var inspector: hostWindow && hostWindow.inspector ? hostWindow.inspector : null
    property var theme: hostWindow && hostWindow.theme ? hostWindow.theme : null

    anchors.fill: parent
    color: theme ? theme.surface : "#17181c"

    property int currentTab: 0
    readonly property var tabs: ["Plugins", "Settings"]

    Column {
        anchors.fill: parent
        spacing: 0

        // Tab strip
        Rectangle {
            width: parent.width
            height: 32
            color: theme ? theme.surfaceAlt : "#2f343e"

            Rectangle {
                anchors.bottom: parent.bottom
                width: parent.width
                height: 1
                color: theme ? theme.border : "#464b57"
            }

            Row {
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.leftMargin: 8
                spacing: 0

                Repeater {
                    model: root.tabs

                    delegate: Rectangle {
                        required property string modelData
                        required property int index
                        width: tabLabel.implicitWidth + 24
                        height: parent.height
                        color: "transparent"

                        readonly property bool active: root.currentTab === index

                        Rectangle {
                            anchors.bottom: parent.bottom
                            width: parent.width
                            height: 2
                            color: active ? (theme ? theme.accent : "#4a9eff") : "transparent"
                        }

                        Text {
                            id: tabLabel
                            anchors.centerIn: parent
                            text: modelData
                            color: active ? (theme ? theme.accent : "#4a9eff") : (theme ? theme.textMuted : "#878a98")
                            font.pixelSize: theme ? theme.fontSizeSmall : 11
                            font.family: theme ? theme.fontFamily : "sans-serif"
                            font.weight: active ? Font.DemiBold : Font.Normal
                        }

                        MouseArea {
                            anchors.fill: parent
                            onClicked: root.currentTab = index
                        }
                    }
                }
            }
        }

        // Plugins tab
        SchemaList {
            visible: root.currentTab === 0
            width: parent.width
            height: parent.height - 32
            theme: root.theme
            model: root.inspector ? root.inspector.pluginRows : []
            keyLabel: "property"
            valueLabel: "value"
            emptyText: "No plugins loaded."
        }

        // Settings tab
        SchemaList {
            visible: root.currentTab === 1
            width: parent.width
            height: parent.height - 32
            theme: root.theme
            model: root.inspector ? root.inspector.settingRows : []
            keyLabel: "key"
            valueLabel: "value"
            emptyText: "No settings declared."
        }
    }
}
