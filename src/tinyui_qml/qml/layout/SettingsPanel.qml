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

Item {
    id: panel
    anchors.fill: parent
    opacity: settingsPanelViewModel.open ? 1 : 0
    visible: opacity > 0
    z: 5

    Behavior on opacity {
        NumberAnimation { duration: 180; easing.type: Easing.OutCubic }
    }

    // Achtergrond
    Rectangle {
        anchors.fill: parent
        color: theme.surface
    }

    // ── Header ────────────────────────────────────────────────────────────

    Rectangle {
        id: panelHeader
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 40
        color: theme.surfaceAlt

        Text {
            anchors.left: parent.left
            anchors.leftMargin: 16
            anchors.verticalCenter: parent.verticalCenter
            text: "Settings"
            color: theme.text
            font.pixelSize: theme.fontSizeBase
            font.family: theme.fontFamily
            font.weight: Font.DemiBold
        }

        Item {
            anchors.right: parent.right
            width: 40
            height: parent.height

            Text {
                anchors.centerIn: parent
                text: icons.close
                font.family: theme.iconFont
                font.pixelSize: 10
                color: closeHover.containsMouse ? theme.text : theme.textMuted
                Behavior on color { ColorAnimation { duration: 80 } }
            }

            MouseArea {
                id: closeHover
                anchors.fill: parent
                hoverEnabled: true
                onClicked: settingsPanelViewModel.closePanel()
            }
        }

        Rectangle {
            anchors.bottom: parent.bottom
            width: parent.width
            height: 1
            color: theme.border
        }
    }

    // ── Settings lijst ────────────────────────────────────────────────────

    ListView {
        anchors.top: panelHeader.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        clip: true
        model: coreViewModel.settingsByPlugin
        spacing: 0

        // Eén delegate per plugin — bevat een sectie-header + rijen
        delegate: Column {
            id: pluginSection

            required property var modelData   // { plugin, settings[] }
            required property int index

            width: ListView.view.width

            // Sectie-header
            Rectangle {
                width: parent.width
                height: 28
                color: theme.surfaceAlt

                Text {
                    anchors.left: parent.left
                    anchors.leftMargin: 16
                    anchors.verticalCenter: parent.verticalCenter
                    text: pluginSection.modelData.plugin
                    color: theme.textMuted
                    font.pixelSize: theme.fontSizeSmall
                    font.family: theme.fontFamily
                    font.weight: Font.Medium
                }

                Rectangle {
                    anchors.bottom: parent.bottom
                    width: parent.width
                    height: 1
                    color: theme.border
                }
            }

            // Setting rijen
            Repeater {
                model: pluginSection.modelData.settings

                Rectangle {
                    id: settingRow

                    required property var modelData   // { key, label, type, value, description, options[] }
                    required property int index

                    width: pluginSection.width
                    height: 44
                    color: rowHover.hovered ? "#dec1841a" : "transparent"
                    Behavior on color { ColorAnimation { duration: 80 } }

                    Rectangle {
                        anchors.bottom: parent.bottom
                        width: parent.width
                        height: 1
                        color: theme.border
                        opacity: 0.4
                    }

                    Row {
                        anchors.fill: parent
                        leftPadding: 16

                        // Label + omschrijving
                        Column {
                            width: parent.width - 16 - 100
                            anchors.verticalCenter: parent.verticalCenter
                            spacing: 3

                            Text {
                                text: settingRow.modelData.label
                                color: theme.text
                                font.pixelSize: theme.fontSizeBase
                                font.family: theme.fontFamily
                            }

                            Text {
                                visible: settingRow.modelData.description !== ""
                                text: settingRow.modelData.description
                                color: rowHover.hovered ? "#dec184" : theme.textMuted
                                font.pixelSize: theme.fontSizeSmall
                                font.family: theme.fontFamily
                                Behavior on color { ColorAnimation { duration: 120 } }
                            }
                        }

                        // Control
                        Item {
                            width: 100
                            height: parent.height

                            // Bool → toggle
                            Rectangle {
                                visible: settingRow.modelData.type === "bool"
                                anchors.centerIn: parent
                                width: 34
                                height: 18
                                radius: 9
                                color: settingRow.modelData.value ? theme.accent : theme.surfaceFloating
                                border.width: 1
                                border.color: settingRow.modelData.value ? "transparent" : theme.border
                                Behavior on color       { ColorAnimation { duration: 140 } }
                                Behavior on border.color { ColorAnimation { duration: 140 } }

                                Rectangle {
                                    anchors.verticalCenter: parent.verticalCenter
                                    x: settingRow.modelData.value ? parent.width - width - 2 : 2
                                    width: 14; height: 14; radius: 7
                                    color: "#FFFFFF"
                                    Behavior on x { NumberAnimation { duration: 140; easing.type: Easing.OutCubic } }
                                }

                                MouseArea {
                                    anchors.fill: parent
                                    onClicked: coreViewModel.setSettingValue(
                                        pluginSection.modelData.plugin,
                                        settingRow.modelData.key,
                                        !settingRow.modelData.value
                                    )
                                }
                            }

                            // Enum → pijl-selector
                            Row {
                                visible: settingRow.modelData.type === "enum"
                                anchors.centerIn: parent
                                spacing: 8

                                Text {
                                    anchors.verticalCenter: parent.verticalCenter
                                    text: "\u2039"   // ‹
                                    color: prevHover.containsMouse ? theme.text : theme.textMuted
                                    font.pixelSize: theme.fontSizeBase
                                    font.family: theme.fontFamily
                                    Behavior on color { ColorAnimation { duration: 80 } }
                                    MouseArea {
                                        id: prevHover
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        onClicked: {
                                            var opts = settingRow.modelData.options
                                            var idx  = opts.indexOf(settingRow.modelData.value)
                                            coreViewModel.setSettingValue(
                                                pluginSection.modelData.plugin,
                                                settingRow.modelData.key,
                                                opts[(idx - 1 + opts.length) % opts.length]
                                            )
                                        }
                                    }
                                }

                                Text {
                                    anchors.verticalCenter: parent.verticalCenter
                                    text: settingRow.modelData.value
                                    color: theme.text
                                    font.pixelSize: theme.fontSizeSmall
                                    font.family: theme.fontFamily
                                    width: 42
                                    horizontalAlignment: Text.AlignHCenter
                                }

                                Text {
                                    anchors.verticalCenter: parent.verticalCenter
                                    text: "\u203A"   // ›
                                    color: nextHover.containsMouse ? theme.text : theme.textMuted
                                    font.pixelSize: theme.fontSizeBase
                                    font.family: theme.fontFamily
                                    Behavior on color { ColorAnimation { duration: 80 } }
                                    MouseArea {
                                        id: nextHover
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        onClicked: {
                                            var opts = settingRow.modelData.options
                                            var idx  = opts.indexOf(settingRow.modelData.value)
                                            coreViewModel.setSettingValue(
                                                pluginSection.modelData.plugin,
                                                settingRow.modelData.key,
                                                opts[(idx + 1) % opts.length]
                                            )
                                        }
                                    }
                                }
                            }
                        }
                    }

                    HoverHandler { id: rowHover }
                }
            }
        }
    }
}
