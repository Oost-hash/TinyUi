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

// Reusable schema list with column headers and scrollable rows
import QtQuick

Item {
    property var    theme
    property var    model:      []
    property string keyLabel:   "key"
    property string valueLabel: "value"
    property string emptyText:  "No data."

    // Column headers
    Item {
        id: header
        anchors.top:   parent.top
        anchors.left:  parent.left
        anchors.right: parent.right
        height: 24

        Rectangle {
            anchors.fill: parent
            color: theme ? theme.surfaceAlt : "#1e1f23"
        }
        Rectangle {
            anchors.bottom: parent.bottom
            width: parent.width
            height: 1
            color: theme ? theme.border : "#2a2b30"
        }

        Row {
            anchors.fill: parent
            anchors.leftMargin:  12
            anchors.rightMargin: 12

            Text {
                width:  parent.width * 0.45
                height: parent.height
                verticalAlignment: Text.AlignVCenter
                text:  keyLabel
                color: theme ? theme.textMuted : "#888"
                font.pixelSize: 10
                font.family:    "Consolas, Courier New, monospace"
                font.weight:    Font.DemiBold
            }
            Text {
                width:  parent.width * 0.35
                height: parent.height
                verticalAlignment: Text.AlignVCenter
                text:  valueLabel
                color: theme ? theme.textMuted : "#888"
                font.pixelSize: 10
                font.family:    "Consolas, Courier New, monospace"
                font.weight:    Font.DemiBold
            }
            Text {
                width:  parent.width * 0.20
                height: parent.height
                verticalAlignment: Text.AlignVCenter
                text:  "type / kind"
                color: theme ? theme.textMuted : "#888"
                font.pixelSize: 10
                font.family:    "Consolas, Courier New, monospace"
                font.weight:    Font.DemiBold
            }
        }
    }

    // Rows
    ListView {
        anchors.top:    header.bottom
        anchors.left:   parent.left
        anchors.right:  parent.right
        anchors.bottom: parent.bottom
        clip: true
        model: parent.model

        delegate: Item {
            required property var modelData
            required property int index

            readonly property bool isSection: modelData.rowType === "section"

            width:  ListView.view.width
            height: isSection ? 28 : 22

            // Section row
            Item {
                anchors.fill: parent
                visible: isSection

                Rectangle {
                    anchors.fill: parent
                    color: theme ? theme.surfaceAlt : "#1e1f23"
                }
                Rectangle {
                    anchors.bottom: parent.bottom
                    width: parent.width
                    height: 1
                    color: theme ? theme.border : "#2a2b30"
                }
                Rectangle {
                    anchors.top: parent.top
                    width: parent.width
                    height: 1
                    color: theme ? theme.border : "#2a2b30"
                    visible: index > 0
                }

                Row {
                    anchors.fill: parent
                    anchors.leftMargin: 12
                    spacing: 8

                    Text {
                        height: parent.height
                        verticalAlignment: Text.AlignVCenter
                        text:  modelData.label ?? ""
                        color: theme ? theme.text : "#fff"
                        font.pixelSize: theme ? theme.fontSizeSmall : 12
                        font.family:    theme ? theme.fontFamily : "sans-serif"
                        font.weight:    Font.DemiBold
                    }
                    Text {
                        height: parent.height
                        verticalAlignment: Text.AlignVCenter
                        text:  modelData.sublabel ?? ""
                        color: theme ? theme.textMuted : "#888"
                        font.pixelSize: theme ? theme.fontSizeSmall : 12
                        font.family:    theme ? theme.fontFamily : "sans-serif"
                    }
                }
            }

            // Data row
            Item {
                anchors.fill: parent
                visible: !isSection

                Rectangle {
                    anchors.fill: parent
                    color: index % 2 === 0
                           ? "transparent"
                           : (theme ? Qt.rgba(1, 1, 1, 0.02) : "#1a1b1f")
                }

                Row {
                    anchors.fill: parent
                    anchors.leftMargin:  12
                    anchors.rightMargin: 12

                    Text {
                        width:  parent.width * 0.45
                        height: parent.height
                        verticalAlignment: Text.AlignVCenter
                        text:  modelData.key ?? ""
                        color: theme ? theme.textMuted : "#888"
                        font.pixelSize: 11
                        font.family:    "Consolas, Courier New, monospace"
                        elide: Text.ElideRight
                    }
                    Text {
                        width:  parent.width * 0.35
                        height: parent.height
                        verticalAlignment: Text.AlignVCenter
                        text:  modelData.value ?? ""
                        color: theme ? theme.text : "#fff"
                        font.pixelSize: 11
                        font.family:    "Consolas, Courier New, monospace"
                        elide: Text.ElideRight
                    }
                    Text {
                        width:  parent.width * 0.20
                        height: parent.height
                        verticalAlignment: Text.AlignVCenter
                        text:  modelData.tag ?? ""
                        color: theme ? theme.textMuted : "#888"
                        font.pixelSize: 10
                        font.family:    "Consolas, Courier New, monospace"
                        elide: Text.ElideRight
                    }
                }
            }
        }

        // Empty state
        Text {
            anchors.centerIn: parent
            visible: parent.count === 0
            text:  emptyText
            color: theme ? theme.textMuted : "#888"
            font.pixelSize: theme ? theme.fontSizeSmall : 12
            font.family:    theme ? theme.fontFamily : "sans-serif"
        }
    }
}
