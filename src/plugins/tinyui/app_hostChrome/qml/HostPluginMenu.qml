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

Item {
    id: root

    property var theme: null
    property var pluginMenuItems: []
    property string pluginMenuLabel: "Plugins"
    property bool open: false

    readonly property real buttonWidth: pluginMenuButton.width

    signal openRequested(bool open)
    signal triggerAction(string action)

    visible: root.pluginMenuItems.length > 0
    width: Math.max(160, pluginMenuButton.width)
    height: 32
    z: 25

    Rectangle {
        id: pluginMenuButton
        visible: root.pluginMenuItems.length > 0
        x: 0
        y: 0
        width: pluginMenuLabelText.implicitWidth + 24
        height: 32
        color: pluginMenuMouse.containsMouse || root.open ? (root.theme ? root.theme.surfaceAlt : "#2f343e") : "transparent"

        Text {
            id: pluginMenuLabelText
            anchors.centerIn: parent
            text: root.pluginMenuLabel || "Plugins"
            color: pluginMenuMouse.containsMouse || root.open ? "#FFFFFF" : (root.theme ? root.theme.textMuted : "#878a98")
            font.pixelSize: 12
        }

        MouseArea {
            id: pluginMenuMouse
            anchors.fill: parent
            hoverEnabled: true
            onClicked: root.openRequested(!root.open)
        }
    }

    Item {
        z: 50
        x: 0
        y: 32
        width: 160
        height: pluginMenuColumn.implicitHeight
        visible: root.open && root.pluginMenuItems.length > 0

        Rectangle {
            anchors.fill: parent
            color: root.theme ? root.theme.surfaceAlt : "#2f343e"
        }
        Rectangle {
            anchors.left: parent.left
            width: 1
            height: parent.height
            color: root.theme ? root.theme.border : "#464b57"
        }
        Rectangle {
            anchors.bottom: parent.bottom
            width: parent.width
            height: 1
            color: root.theme ? root.theme.border : "#464b57"
        }
        Rectangle {
            anchors.right: parent.right
            width: 1
            height: parent.height
            color: root.theme ? root.theme.border : "#464b57"
        }

        Column {
            id: pluginMenuColumn
            width: parent.width
            spacing: 0
            padding: 0
            topPadding: 0
            bottomPadding: 0

            Repeater {
                model: root.pluginMenuItems

                delegate: Item {
                    id: pluginMenuDelegate
                    required property var modelData
                    visible: pluginMenuDelegate.modelData.visible === undefined ? true : !!pluginMenuDelegate.modelData.visible
                    width: 160
                    height: visible ? (pluginMenuDelegate.modelData.separator ? 9 : 28) : 0

                    Rectangle {
                        visible: !!pluginMenuDelegate.modelData.separator
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.leftMargin: 8
                        anchors.rightMargin: 8
                        height: 1
                        color: root.theme ? root.theme.border : "#464b57"
                    }

                    Rectangle {
                        visible: !pluginMenuDelegate.modelData.separator
                        anchors.fill: parent
                        color: pluginItemMouse.containsMouse ? (root.theme ? root.theme.surfaceRaised : "#3b414d") : "transparent"

                        Text {
                            anchors.left: parent.left
                            anchors.leftMargin: 12
                            anchors.verticalCenter: parent.verticalCenter
                            text: pluginMenuDelegate.modelData.label
                            color: root.theme ? root.theme.text : "#dce0e5"
                            font.pixelSize: root.theme ? root.theme.fontSizeSmall : 11
                        }

                        MouseArea {
                            id: pluginItemMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            onClicked: {
                                root.openRequested(false);
                                root.triggerAction(pluginMenuDelegate.modelData.action);
                            }
                        }
                    }
                }
            }
        }
    }
}
