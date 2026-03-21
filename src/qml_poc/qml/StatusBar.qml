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

Rectangle {
    id: statusBar
    height: 32
    bottomLeftRadius: 8
    bottomRightRadius: 8
    color: theme.surfaceRaised

    // Icoontje per tab-index (zelfde volgorde als register() in main.py)
    property var tabIcons: ["\uE80F", "\uE74C"]

    // Border-top
    Rectangle {
        anchors.top: parent.top
        width: parent.width
        height: 1
        color: theme.border
    }

    // ── Links: favorites bar ──────────────────────────────────────────────
    // TODO: favorites bar — vaste shortcuts naar plugins/pagina's

    Row {
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.leftMargin: 4

        StatusBarIconButton {
            iconText: "\uE80F"
            selected: tabViewModel.currentIndex === 0
            onClicked: tabViewModel.setCurrentIndex(0)
        }

        StatusBarIconButton {
            iconText: "\uE74C"
            selected: tabViewModel.currentIndex === 1
            onClicked: tabViewModel.setCurrentIndex(1)
        }
    }

    // ── Rechts: plugin naam knop ──────────────────────────────────────────

    // Plugin naam knop — opent dropdown omhoog
    Rectangle {
        id: pluginNameBtn
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        width: pluginNameRow.width + 20
        color: pluginDropdown.visible || pluginNameHover.containsMouse
               ? theme.surfaceFloating : "transparent"
        bottomRightRadius: 8

        Row {
            id: pluginNameRow
            anchors.centerIn: parent
            spacing: 6

            Text {
                anchors.verticalCenter: parent.verticalCenter
                text: statusBar.tabIcons[tabViewModel.currentIndex] ?? ""
                font.family: "Segoe Fluent Icons"
                font.pixelSize: 12
                color: "#FFFFFF"
            }

            Text {
                id: pluginNameText
                anchors.verticalCenter: parent.verticalCenter
                text: tabViewModel.tabNames[tabViewModel.currentIndex] ?? ""
                color: "#FFFFFF"
                font.pixelSize: theme.fontSizeSmall
                font.family: theme.fontFamily
            }
        }

        MouseArea {
            id: pluginNameHover
            anchors.fill: parent
            hoverEnabled: true
            onClicked: pluginDropdown.visible ? pluginDropdown.close() : pluginDropdown.open()
        }

        // Custom dropdown — opent omhoog, rechtsuitgelijnd
        MenuPopup {
            id: pluginDropdown
            slideDown: false
            width: Math.max(pluginNameBtn.width, 140)
            x: pluginNameBtn.width - width
            y: -height

            // Override achtergrond: borders links, boven, rechts (geen onderkant)
            background: Item {
                Rectangle { anchors.fill: parent; color: theme.surfaceAlt }
                Rectangle { anchors.left: parent.left;   width: 1; height: parent.height; color: theme.border }
                Rectangle { anchors.top: parent.top;     height: 1; width: parent.width;  color: theme.border }
                Rectangle { anchors.right: parent.right; width: 1; height: parent.height; color: theme.border }
            }

            contentItem: Column {
                spacing: 0

                Repeater {
                    model: tabViewModel.tabNames

                    Rectangle {
                        width: pluginDropdown.width
                        height: 28
                        radius: 0
                        color: tabViewModel.currentIndex === index
                               ? theme.surfaceFloating
                               : dropItemHover.containsMouse ? theme.surfaceRaised : "transparent"
                        Behavior on color { ColorAnimation { duration: 60 } }

                        Row {
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.left: parent.left
                            anchors.leftMargin: 8
                            spacing: 6

                            Text {
                                anchors.verticalCenter: parent.verticalCenter
                                text: statusBar.tabIcons[index] ?? ""
                                font.family: "Segoe Fluent Icons"
                                font.pixelSize: 12
                                color: tabViewModel.currentIndex === index ? theme.accent : theme.textMuted
                            }

                            Text {
                                anchors.verticalCenter: parent.verticalCenter
                                text: modelData
                                color: tabViewModel.currentIndex === index ? theme.accent : theme.text
                                font.pixelSize: theme.fontSizeSmall
                                font.family: theme.fontFamily
                                font.weight: tabViewModel.currentIndex === index ? Font.DemiBold : Font.Normal
                            }
                        }

                        MouseArea {
                            id: dropItemHover
                            anchors.fill: parent
                            hoverEnabled: true
                            onClicked: {
                                tabViewModel.setCurrentIndex(index)
                                pluginDropdown.close()
                            }
                        }
                    }
                }
            }
        }
    }
}

