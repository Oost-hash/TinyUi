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

pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Layouts
import TinyUI
import "../../tinyui/qml/components"

BaseDialog {
    id: devTools
    dialogTitle: "Dev Tools"
    width: 800
    height: 500

    onCloseRequested: devTools.hide()

    property int currentTab: 0
    readonly property var _tabs: ["State", "Runtime", "Console"]

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // ── Tab strip ─────────────────────────────────────────────────────────
        Rectangle {
            Layout.fillWidth: true
            implicitHeight: 32
            color: Theme.surfaceAlt

            Rectangle {
                anchors.bottom: parent.bottom
                width: parent.width; height: 1
                color: Theme.border
            }

            Row {
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.leftMargin: 8
                spacing: 0

                Repeater {
                    model: devTools._tabs

                    delegate: Rectangle {
                        id: tabItem
                        required property string modelData
                        required property int    index

                        width: tabLabel.implicitWidth + 24
                        height: parent.height
                        color: "transparent"

                        readonly property bool active: devTools.currentTab === tabItem.index

                        Rectangle {
                            anchors.bottom: parent.bottom
                            width: parent.width; height: 2
                            color: tabItem.active ? Theme.accent : "transparent"
                        }

                        Text {
                            id: tabLabel
                            anchors.centerIn: parent
                            text: tabItem.modelData
                            color: tabItem.active ? Theme.accent : Theme.textMuted
                            font.pixelSize: Theme.fontSizeSmall
                            font.family: Theme.fontFamily
                            font.weight: tabItem.active ? Font.DemiBold : Font.Normal
                        }

                        MouseArea {
                            anchors.fill: parent
                            onClicked: devTools.currentTab = tabItem.index
                        }
                    }
                }
            }
        }

        // ── Tab content ───────────────────────────────────────────────────────

        DevToolsStateTab {
            Layout.fillWidth: true
            Layout.fillHeight: true
            visible: devTools.currentTab === 0
        }

        DevToolsRuntimeTab {
            Layout.fillWidth: true
            Layout.fillHeight: true
            visible: devTools.currentTab === 1
        }

        ConsolePane {
            Layout.fillWidth: true
            Layout.fillHeight: true
            visible: devTools.currentTab === 2
        }
    }
}
