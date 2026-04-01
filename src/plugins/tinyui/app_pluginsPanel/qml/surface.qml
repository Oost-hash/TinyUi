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
    property var hostActions: hostWindow && hostWindow.hostActions ? hostWindow.hostActions : null

    anchors.fill: parent
    color: theme ? theme.surface : "#17181c"

    Column {
        anchors.fill: parent
        spacing: 0

        // Header
        Rectangle {
            width: parent.width
            height: 36
            color: theme ? theme.surfaceAlt : "#2f343e"

            Rectangle {
                anchors.bottom: parent.bottom
                width: parent.width
                height: 1
                color: theme ? theme.border : "#464b57"
            }

            Text {
                anchors.left: parent.left
                anchors.leftMargin: 12
                anchors.verticalCenter: parent.verticalCenter
                text: "Plugins"
                color: theme ? theme.text : "#ffffff"
                font.pixelSize: theme ? theme.fontSizeBase : 13
                font.family: theme ? theme.fontFamily : "sans-serif"
                font.weight: Font.DemiBold
            }
        }

        // Content
        Row {
            width: parent.width
            height: parent.height - 36

            // Left pane — info + actions
            Rectangle {
                width: parent.width * 0.40
                height: parent.height
                color: theme ? Qt.rgba(0, 0, 0, 0.12) : "#121316"

                Column {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 12

                    Text {
                        width: parent.width
                        text: "Manage your installed plugins and configure their settings."
                        color: theme ? theme.textSecondary : "#a9afbc"
                        font.pixelSize: theme ? theme.fontSizeSmall : 11
                        font.family: theme ? theme.fontFamily : "sans-serif"
                        wrapMode: Text.Wrap
                    }

                    Rectangle {
                        width: parent.width
                        height: 1
                        color: theme ? theme.border : "#464b57"
                    }

                    Rectangle {
                        width: parent.width
                        height: 32
                        radius: 4
                        color: settingsMouse.containsMouse
                            ? (theme ? theme.accentHover : "#3a7ac9")
                            : (theme ? theme.accent : "#4a9eff")

                        Text {
                            anchors.centerIn: parent
                            text: "Open Settings"
                            color: theme ? theme.accentText : "#ffffff"
                            font.pixelSize: theme ? theme.fontSizeSmall : 11
                            font.family: theme ? theme.fontFamily : "sans-serif"
                            font.weight: Font.DemiBold
                        }

                        MouseArea {
                            id: settingsMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            onClicked: {
                                if (root.hostActions)
                                    root.hostActions.trigger("open:settings.main")
                            }
                        }
                    }
                }
            }

            // Right pane — plugin list
            Rectangle {
                width: parent.width * 0.60
                height: parent.height
                color: "transparent"

                Column {
                    anchors.fill: parent
                    anchors.margins: 0
                    spacing: 0

                    // List header
                    Rectangle {
                        width: parent.width
                        height: 28
                        color: theme ? theme.surfaceRaised : "#3b414d"

                        Row {
                            anchors.fill: parent
                            anchors.leftMargin: 12
                            anchors.rightMargin: 12

                            Text {
                                width: parent.width * 0.60
                                height: parent.height
                                verticalAlignment: Text.AlignVCenter
                                text: "Plugin"
                                color: theme ? theme.textMuted : "#878a98"
                                font.pixelSize: 10
                                font.family: theme ? theme.fontFamily : "sans-serif"
                                font.weight: Font.DemiBold
                            }

                            Text {
                                width: parent.width * 0.40
                                height: parent.height
                                verticalAlignment: Text.AlignVCenter
                                text: "Type"
                                color: theme ? theme.textMuted : "#878a98"
                                font.pixelSize: 10
                                font.family: theme ? theme.fontFamily : "sans-serif"
                                font.weight: Font.DemiBold
                            }
                        }
                    }

                    ListView {
                        width: parent.width
                        height: parent.height - 28
                        clip: true
                        model: root.inspector ? root.inspector.pluginRows : []

                        delegate: Rectangle {
                            required property var modelData
                            required property int index

                            width: ListView.view.width
                            height: 32
                            color: index % 2 === 0
                                ? "transparent"
                                : (theme ? Qt.rgba(1, 1, 1, 0.02) : "#1a1b1f")

                            Row {
                                anchors.fill: parent
                                anchors.leftMargin: 12
                                anchors.rightMargin: 12

                                Text {
                                    width: parent.width * 0.60
                                    height: parent.height
                                    verticalAlignment: Text.AlignVCenter
                                    text: modelData.label ?? ""
                                    color: theme ? theme.text : "#ffffff"
                                    font.pixelSize: 12
                                    font.family: theme ? theme.fontFamily : "sans-serif"
                                    elide: Text.ElideRight
                                }

                                Text {
                                    width: parent.width * 0.40
                                    height: parent.height
                                    verticalAlignment: Text.AlignVCenter
                                    text: modelData.sublabel ?? ""
                                    color: theme ? theme.textMuted : "#878a98"
                                    font.pixelSize: 11
                                    font.family: theme ? theme.fontFamily : "sans-serif"
                                    elide: Text.ElideRight
                                }
                            }
                        }

                        // Empty state
                        Text {
                            anchors.centerIn: parent
                            visible: parent.count === 0
                            text: "No plugins available."
                            color: theme ? theme.textMuted : "#878a98"
                            font.pixelSize: theme ? theme.fontSizeSmall : 11
                            font.family: theme ? theme.fontFamily : "sans-serif"
                        }
                    }
                }
            }
        }
    }
}
