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

// Reusable schema list with column headers and scrollable rows
import QtQuick

Item {
    id: root
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
            color: root.theme ? root.theme.surfaceAlt : "#1e1f23"
        }
        Rectangle {
            anchors.bottom: parent.bottom
            width: parent.width
            height: 1
            color: root.theme ? root.theme.border : "#2a2b30"
        }

        Row {
            anchors.fill: parent
            anchors.leftMargin:  12
            anchors.rightMargin: 12

            Text {
                width:  parent.width * 0.45
                height: parent.height
                verticalAlignment: Text.AlignVCenter
                text:  root.keyLabel
                color: root.theme ? root.theme.textMuted : "#888"
                font.pixelSize: 10
                font.family:    "Consolas, Courier New, monospace"
                font.weight:    Font.DemiBold
            }
            Text {
                width:  parent.width * 0.35
                height: parent.height
                verticalAlignment: Text.AlignVCenter
                text:  root.valueLabel
                color: root.theme ? root.theme.textMuted : "#888"
                font.pixelSize: 10
                font.family:    "Consolas, Courier New, monospace"
                font.weight:    Font.DemiBold
            }
            Text {
                width:  parent.width * 0.20
                height: parent.height
                verticalAlignment: Text.AlignVCenter
                text:  "type / kind"
                color: root.theme ? root.theme.textMuted : "#888"
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
        model: root.model

        delegate: Item {
            id: rowDelegate
            required property var modelData
            required property int index

            readonly property bool isSection: rowDelegate.modelData.rowType === "section"

            width:  ListView.view.width
            height: rowDelegate.isSection ? 28 : 22

            // Section row
            Item {
                anchors.fill: parent
                visible: rowDelegate.isSection

                Rectangle {
                    anchors.fill: parent
                    color: root.theme ? root.theme.surfaceAlt : "#1e1f23"
                }
                Rectangle {
                    anchors.bottom: parent.bottom
                    width: parent.width
                    height: 1
                    color: root.theme ? root.theme.border : "#2a2b30"
                }
                Rectangle {
                    anchors.top: parent.top
                    width: parent.width
                    height: 1
                    color: root.theme ? root.theme.border : "#2a2b30"
                    visible: rowDelegate.index > 0
                }

                Row {
                    anchors.fill: parent
                    anchors.leftMargin: 12
                    spacing: 8

                    Text {
                        height: parent.height
                        verticalAlignment: Text.AlignVCenter
                        text:  rowDelegate.modelData.label ?? ""
                        color: root.theme ? root.theme.text : "#fff"
                        font.pixelSize: root.theme ? root.theme.fontSizeSmall : 12
                        font.family:    root.theme ? root.theme.fontFamily : "sans-serif"
                        font.weight:    Font.DemiBold
                    }
                    Text {
                        height: parent.height
                        verticalAlignment: Text.AlignVCenter
                        text:  rowDelegate.modelData.sublabel ?? ""
                        color: root.theme ? root.theme.textMuted : "#888"
                        font.pixelSize: root.theme ? root.theme.fontSizeSmall : 12
                        font.family:    root.theme ? root.theme.fontFamily : "sans-serif"
                    }
                }
            }

            // Data row
            Item {
                anchors.fill: parent
                visible: !rowDelegate.isSection

                Rectangle {
                    anchors.fill: parent
                    color: rowDelegate.index % 2 === 0
                           ? "transparent"
                           : (root.theme ? Qt.rgba(1, 1, 1, 0.02) : "#1a1b1f")
                }

                Row {
                    anchors.fill: parent
                    anchors.leftMargin:  12
                    anchors.rightMargin: 12

                    Text {
                        width:  parent.width * 0.45
                        height: parent.height
                        verticalAlignment: Text.AlignVCenter
                        text:  rowDelegate.modelData.key ?? ""
                        color: root.theme ? root.theme.textMuted : "#888"
                        font.pixelSize: 11
                        font.family:    "Consolas, Courier New, monospace"
                        elide: Text.ElideRight
                    }
                    Text {
                        width:  parent.width * 0.35
                        height: parent.height
                        verticalAlignment: Text.AlignVCenter
                        text:  rowDelegate.modelData.value ?? ""
                        color: {
                            if (rowDelegate.modelData.tag === "status") {
                                var val = rowDelegate.modelData.value ?? ""
                                if (val === "active") return root.theme ? root.theme.success : "#4caf50"
                                if (val === "error") return root.theme ? root.theme.danger : "#f44336"
                                if (val === "enabling" || val === "loading") return root.theme ? root.theme.warning : "#ff9800"
                                return root.theme ? root.theme.textMuted : "#888"
                            }
                            if (rowDelegate.modelData.tag === "error") return root.theme ? root.theme.danger : "#f44336"
                            return root.theme ? root.theme.text : "#fff"
                        }
                        font.pixelSize: 11
                        font.family:    "Consolas, Courier New, monospace"
                        elide: Text.ElideRight
                    }
                    Text {
                        width:  parent.width * 0.20
                        height: parent.height
                        verticalAlignment: Text.AlignVCenter
                        text:  rowDelegate.modelData.tag ?? ""
                        color: root.theme ? root.theme.textMuted : "#888"
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
            text:  root.emptyText
            color: root.theme ? root.theme.textMuted : "#888"
            font.pixelSize: root.theme ? root.theme.fontSizeSmall : 12
            font.family:    root.theme ? root.theme.fontFamily : "sans-serif"
        }
    }
}
