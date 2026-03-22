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
import QtQuick.Layouts

Item {
    id: demoTab

    // ── Status bar ────────────────────────────────────────────────────────────

    Rectangle {
        id: statusBar
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 36
        color: "transparent"

        Row {
            anchors.fill: parent
            anchors.leftMargin: 16
            spacing: 16

            // Connection indicator
            Rectangle {
                width: 8; height: 8
                radius: 4
                anchors.verticalCenter: parent.verticalCenter
                color: tyreDemoViewModel.active
                    ? "#4caf50"
                    : tyreDemoViewModel.gameRunning ? "#ff9800"
                    : tyreDemoViewModel.connected  ? "#888"
                    : "#f44336"

                Behavior on color { ColorAnimation { duration: 200 } }
            }

            Text {
                anchors.verticalCenter: parent.verticalCenter
                text: tyreDemoViewModel.active
                    ? "LMU — active  |  v" + tyreDemoViewModel.gameVersion
                          + "  |  Front: " + tyreDemoViewModel.compoundFront
                          + "  Rear: " + tyreDemoViewModel.compoundRear
                    : tyreDemoViewModel.gameRunning
                        ? "LMU — waiting for session…"
                        : tyreDemoViewModel.connected
                            ? "LMU — game not running"
                            : "LMU — not found"
                color: theme.textSecondary
                font.pixelSize: theme.fontSizeSmall
                font.family: theme.fontFamily
            }
        }

        Rectangle {
            anchors.bottom: parent.bottom
            width: parent.width; height: 1
            color: theme.border
        }
    }

    // ── Tyre cards ────────────────────────────────────────────────────────────

    Row {
        anchors.top: statusBar.bottom
        anchors.topMargin: 24
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 16

        Repeater {
            model: tyreDemoViewModel.tyres

            Rectangle {
                id: card
                required property var modelData
                required property int index

                // Live data directly from the viewmodel — rebinds on every tyreDataChanged
                readonly property var live: tyreDemoViewModel.tyres[index]

                width: 160
                height: 200
                radius: 6
                color: theme.surfaceAlt
                border.color: theme.border
                border.width: 1

                Column {
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 0

                    // Tyre label (FL/FR/RL/RR)
                    Text {
                        width: parent.width
                        text: card.modelData.label
                        color: "#dec184"
                        font.pixelSize: 22
                        font.family: theme.fontFamily
                        font.bold: true
                        horizontalAlignment: Text.AlignHCenter
                        bottomPadding: 10
                    }

                    // Separator
                    Rectangle {
                        width: parent.width; height: 1
                        color: theme.border
                        opacity: 0.5
                    }

                    Item { width: 1; height: 8 }

                    // Value rows — label is static, value binds to card.live
                    Repeater {
                        model: ["Surface", "Inner", "Pressure", "Wear"]

                        Row {
                            width: parent.width
                            height: 28
                            required property string modelData

                            readonly property string displayValue: {
                                if (!tyreDemoViewModel.active) return "–"
                                if (modelData === "Surface")  return card.live.surface  + " °C"
                                if (modelData === "Inner")    return card.live.inner    + " °C"
                                if (modelData === "Pressure") return card.live.pressure + " kPa"
                                if (modelData === "Wear")     return (card.live.wear * 100).toFixed(1) + " %"
                                return "–"
                            }

                            Text {
                                width: parent.width * 0.5
                                height: parent.height
                                verticalAlignment: Text.AlignVCenter
                                text: modelData
                                color: theme.textSecondary
                                font.pixelSize: theme.fontSizeSmall
                                font.family: theme.fontFamily
                            }

                            Text {
                                width: parent.width * 0.5
                                height: parent.height
                                verticalAlignment: Text.AlignVCenter
                                horizontalAlignment: Text.AlignRight
                                text: parent.displayValue
                                color: theme.text
                                font.pixelSize: theme.fontSizeSmall
                                font.family: theme.fontFamily

                                Behavior on text {
                                    SequentialAnimation {
                                        ColorAnimation { target: parent; property: "color"; to: "#dec184"; duration: 80 }
                                        ColorAnimation { target: parent; property: "color"; to: theme.text;  duration: 300 }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
