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
import QtQuick.Controls
import "../components"

Rectangle {
    id: statusBar
    height: 32
    color: theme.surfaceRaised

    // Border-top
    Rectangle {
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 1
        color: theme.border
    }

    // ── Links: editor snelkoppelingen (één knop per geregistreerde editor) ──

    Row {
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.leftMargin: 4

        Repeater {
            model: coreViewModel.editors

            StatusBarIconButton {
                // Eerste letter als tijdelijk icoon — TODO: icon veld in editors.toml
                iconText: modelData.title.charAt(0).toUpperCase()
                textFont: theme.fontFamily
                // TODO: opent editor dialog zodra QML editor beschikbaar is
                onClicked: console.log("Open editor:", modelData.id)
            }
        }
    }

    // ── Rechts: plugin naam knop ──────────────────────────────────────────

    // Plugin naam knop — opent dropdown omhoog; verborgen op de settings tab
    Item {
        id: pluginNameBtn
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        width: pluginNameRow.width + 20

        Rectangle {
            anchors.fill: parent
            color: statusBarViewModel.pluginDropdownOpen ? theme.surfaceAlt
                   : pluginNameHover.containsMouse ? theme.surfaceFloating : "transparent"
        }
        Rectangle { visible: statusBarViewModel.pluginDropdownOpen; anchors.left:  parent.left;  width: 1; height: parent.height; color: theme.border }
        Rectangle { visible: statusBarViewModel.pluginDropdownOpen; anchors.right: parent.right; width: 1; height: parent.height; color: theme.border }

        Row {
            id: pluginNameRow
            anchors.centerIn: parent
            spacing: 0

            Text {
                anchors.verticalCenter: parent.verticalCenter
                text: coreViewModel.pluginNames[statusBarViewModel.activePluginIndex] ?? ""
                color: "#FFFFFF"
                font.pixelSize: theme.fontSizeSmall
                font.family: theme.fontFamily
            }
        }

        MouseArea {
            id: pluginNameHover
            anchors.fill: parent
            hoverEnabled: true
            onClicked: statusBarViewModel.togglePluginDropdown()
        }

        // Inline dropdown — opent omhoog, rechtsuitgelijnd (plain Item, geen Popup)
        Item {
            id: pluginDropdown
            z: 10
            width: Math.max(pluginNameBtn.width, 140)
            height: pluginDropdownCol.implicitHeight
            x: pluginNameBtn.width - width
            y: -height
            visible: statusBarViewModel.pluginDropdownOpen

            Rectangle { anchors.fill: parent; color: theme.surfaceAlt }
            Rectangle { anchors.left:  parent.left;  width: 1; height: parent.height; color: theme.border }
            Rectangle { anchors.top:   parent.top;   height: 1; width: parent.width;  color: theme.border }
            Rectangle { anchors.right: parent.right; width: 1; height: parent.height; color: theme.border }

            Column {
                id: pluginDropdownCol
                width: parent.width
                spacing: 0

                Repeater {
                    model: coreViewModel.pluginNames

                    Rectangle {
                        width: parent.width
                        height: 28
                        color: dropItemHover.containsMouse ? theme.surfaceRaised : "transparent"

                        Text {
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.left: parent.left
                            anchors.leftMargin: 12
                            text: modelData
                            color: statusBarViewModel.activePluginIndex === index ? theme.accent : theme.text
                            font.pixelSize: theme.fontSizeSmall
                            font.family: theme.fontFamily
                            font.weight: statusBarViewModel.activePluginIndex === index ? Font.DemiBold : Font.Normal
                        }

                        MouseArea {
                            id: dropItemHover
                            anchors.fill: parent
                            hoverEnabled: true
                            onClicked: {
                                statusBarViewModel.setActivePlugin(index)
                                statusBarViewModel.closePluginDropdown()
                            }
                        }
                    }
                }
            }
        }
    }
}

