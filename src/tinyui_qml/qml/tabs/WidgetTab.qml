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
import "../components"

Item {
    id: widgetTab

    readonly property int colName:   200
    readonly property int colToggle:  56
    readonly property int colPad:     16  // horizontale tekst-inspringing

    // ── Header ────────────────────────────────────────────────────────────

    Rectangle {
        id: tableHeader
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 32
        color: "transparent"

        Row {
            anchors.fill: parent
            leftPadding: widgetTab.colPad

            Text {
                width: widgetTab.colName
                height: parent.height
                verticalAlignment: Text.AlignVCenter
                text: "Widget"
                color: theme.text
                font.pixelSize: theme.fontSizeSmall
                font.family: theme.fontFamily
            }

            Text {
                width: parent.width - widgetTab.colPad - widgetTab.colName - widgetTab.colToggle
                height: parent.height
                verticalAlignment: Text.AlignVCenter
                text: "Description"
                color: theme.text
                font.pixelSize: theme.fontSizeSmall
                font.family: theme.fontFamily
            }
        }

        Rectangle {
            anchors.bottom: parent.bottom
            width: parent.width
            height: 1
            color: theme.border
        }
    }

    // ── Rijen ─────────────────────────────────────────────────────────────

    ListView {
        anchors.top: tableHeader.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        clip: true
        model: coreViewModel.widgets
        spacing: 0

        delegate: Rectangle {
            id: row

            required property var modelData
            required property int index

            // Lokale toggle state — geïnitialiseerd vanuit backend, animaties draaien lokaal
            property bool widgetEnabled: modelData.enable

            width: ListView.view.width
            height: 40
            color: index % 2 === 0 ? theme.surfaceAlt : "transparent"

            // Hover gradient — rechts naar midden, rest transparant
            Rectangle {
                anchors.fill: parent
                opacity: rowHover.hovered ? 1 : 0
                Behavior on opacity { NumberAnimation { duration: 120 } }
                gradient: Gradient {
                    orientation: Gradient.Horizontal
                    GradientStop { position: 0.0; color: "transparent" }
                    GradientStop { position: 0.5; color: "transparent" }
                    GradientStop { position: 1.0; color: "#20dec184" }
                }
            }

            // Scheidingslijn
            Rectangle {
                anchors.bottom: parent.bottom
                width: parent.width
                height: 1
                color: theme.border
                opacity: 0.4
            }

            Row {
                anchors.fill: parent
                leftPadding: widgetTab.colPad

                // Widget naam
                Text {
                    width: widgetTab.colName
                    height: parent.height
                    verticalAlignment: Text.AlignVCenter
                    text: row.modelData.title
                    color: theme.text
                    font.pixelSize: theme.fontSizeBase
                    font.family: theme.fontFamily
                }

                // Omschrijving
                Text {
                    width: parent.width - widgetTab.colPad - widgetTab.colName - widgetTab.colToggle
                    height: parent.height
                    verticalAlignment: Text.AlignVCenter
                    text: row.modelData.description
                    color: rowHover.hovered ? "#dec184" : theme.textMuted
                    font.pixelSize: theme.fontSizeSmall
                    font.family: theme.fontFamily
                    elide: Text.ElideRight
                    Behavior on color { ColorAnimation { duration: 120 } }
                }

                // Toggle
                Item {
                    width: widgetTab.colToggle
                    height: parent.height

                    ToggleSwitch {
                        anchors.centerIn: parent
                        checked: row.widgetEnabled
                        onToggled: (newValue) => {
                            row.widgetEnabled = newValue
                            coreViewModel.setWidgetEnabled(row.modelData.id, newValue)
                        }
                    }
                }
            }

            HoverHandler { id: rowHover }
        }
    }
}
