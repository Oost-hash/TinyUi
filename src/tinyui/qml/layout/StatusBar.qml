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
import TinyUI
import "../components"

Rectangle {
    id: statusBar
    height: 32
    color: Theme.surfaceRaised

    // Border-top
    Rectangle {
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 1
        color: Theme.border
    }

    // ── Left: editor shortcuts (one button per registered editor) ────────────

    Row {
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.leftMargin: 4

        Repeater {
            model: CoreViewModel.editors

            StatusBarIconButton {
                required property var modelData
                // First letter as temporary icon — TODO: add icon field to editors.toml
                iconText: modelData.title.charAt(0).toUpperCase()
                textFont: Theme.fontFamily
                onClicked: SettingsPanelViewModel.openPanel()
            }
        }
    }

    // ── Right: plugin name button ─────────────────────────────────────────

    // Plugin name button — opens dropdown upward; hidden on the settings tab
    Item {
        id: pluginNameBtn
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        width: pluginNameRow.width + 20

        Rectangle {
            anchors.fill: parent
            color: StatusBarViewModel.pluginDropdownOpen ? Theme.surfaceAlt
                   : pluginNameHover.containsMouse ? Theme.surfaceFloating : "transparent"
        }
        Rectangle { visible: StatusBarViewModel.pluginDropdownOpen; anchors.left:  parent.left;  width: 1; height: parent.height; color: Theme.border }
        Rectangle { visible: StatusBarViewModel.pluginDropdownOpen; anchors.right: parent.right; width: 1; height: parent.height; color: Theme.border }

        Row {
            id: pluginNameRow
            anchors.centerIn: parent
            spacing: 0

            Text {
                anchors.verticalCenter: parent.verticalCenter
                text: CoreViewModel.pluginNames[StatusBarViewModel.activePluginIndex] ?? ""
                color: "#FFFFFF"
                font.pixelSize: Theme.fontSizeSmall
                font.family: Theme.fontFamily
            }
        }

        MouseArea {
            id: pluginNameHover
            anchors.fill: parent
            hoverEnabled: true
            onClicked: StatusBarViewModel.togglePluginDropdown()
        }

        // Inline dropdown — opens upward, right-aligned (plain Item, no Popup)
        Item {
            id: pluginDropdown
            z: 10
            width: Math.max(pluginNameBtn.width, 140)
            height: pluginDropdownCol.implicitHeight
            x: pluginNameBtn.width - width
            y: -height
            visible: StatusBarViewModel.pluginDropdownOpen

            Rectangle { anchors.fill: parent; color: Theme.surfaceAlt }
            Rectangle { anchors.left:  parent.left;  width: 1; height: parent.height; color: Theme.border }
            Rectangle { anchors.top:   parent.top;   height: 1; width: parent.width;  color: Theme.border }
            Rectangle { anchors.right: parent.right; width: 1; height: parent.height; color: Theme.border }

            Column {
                id: pluginDropdownCol
                width: parent.width
                spacing: 0

                Repeater {
                    model: CoreViewModel.pluginNames

                    Rectangle {
                        id: pluginItem
                        required property string modelData
                        required property int index
                        width: parent.width
                        height: 28
                        color: dropItemHover.containsMouse ? Theme.surfaceRaised : "transparent"

                        Text {
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.left: parent.left
                            anchors.leftMargin: 12
                            text: pluginItem.modelData
                            color: StatusBarViewModel.activePluginIndex === pluginItem.index ? Theme.accent : Theme.text
                            font.pixelSize: Theme.fontSizeSmall
                            font.family: Theme.fontFamily
                            font.weight: StatusBarViewModel.activePluginIndex === pluginItem.index ? Font.DemiBold : Font.Normal
                        }

                        MouseArea {
                            id: dropItemHover
                            anchors.fill: parent
                            hoverEnabled: true
                            onClicked: StatusBarViewModel.selectPlugin(pluginItem.index)
                        }
                    }
                }
            }
        }
    }
}

