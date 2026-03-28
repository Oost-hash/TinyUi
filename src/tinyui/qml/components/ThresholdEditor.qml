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

// ── ThresholdEditor ────────────────────────────────────────────────────────────
// Renders the full threshold list for a WidgetContext.
// Each entry shows two rows:
//   Row 1 (always):  ≤ [value]  [color]  [flash toggle]  [×]
//   Row 2 (flash on, animated): Target [dropdown]  Speed [stepper]

Column {
    id: root

    property var context: null  // WidgetContext

    anchors.left:  parent ? parent.left  : undefined
    anchors.right: parent ? parent.right : undefined

    // ── Description ───────────────────────────────────────────────────────────
    Rectangle {
        anchors.left: parent.left; anchors.right: parent.right
        height: descLabel.implicitHeight + 16
        color: "transparent"

        Text {
            id: descLabel
            anchors.left:  parent.left;  anchors.leftMargin:  16
            anchors.right: parent.right; anchors.rightMargin: 16
            anchors.verticalCenter: parent.verticalCenter
            wrapMode:      Text.WordWrap
            text: "Each entry is an upper bound — the color is used while the value is at or below that number. Above all thresholds the widget uses its default color."
            color: Theme.textMuted
            font.pixelSize: Theme.fontSizeSmall
            font.family:    Theme.fontFamily
        }
        Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: Theme.border; opacity: 0.4 }
    }

    // ── Threshold entries ─────────────────────────────────────────────────────
    Repeater {
        model: root.context ? root.context.thresholds : []

        delegate: Column {
            id: entry
            required property var modelData
            required property int index

            anchors.left:  parent ? parent.left  : undefined
            anchors.right: parent ? parent.right : undefined

            // ── Row 1: value · color · flash toggle · remove ──────────────────
            Rectangle {
                id: row1
                anchors.left: parent.left; anchors.right: parent.right
                height: 44
                color: "transparent"

                Rectangle {
                    anchors.fill: parent
                    opacity: rowHover.hovered ? 1 : 0
                    Behavior on opacity { NumberAnimation { duration: 120 } }
                    gradient: Gradient {
                        orientation: Gradient.Horizontal
                        GradientStop { position: 0.0; color: "transparent" }
                        GradientStop { position: 0.6; color: "transparent" }
                        GradientStop { position: 1.0; color: "#20dec184" }
                    }
                }

                // ── Left: index badge + ≤ + value ─────────────────────────────
                Row {
                    anchors.left: parent.left; anchors.leftMargin: 16
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 8

                    // Index badge
                    Rectangle {
                        width: 18; height: 18; radius: 9
                        anchors.verticalCenter: parent.verticalCenter
                        color: entry.modelData.color
                        border.width: 1; border.color: Qt.darker(entry.modelData.color, 1.4)

                        Text {
                            anchors.centerIn: parent
                            text: entry.index + 1
                            font.pixelSize: 9; font.weight: Font.Bold
                            font.family: Theme.fontFamily
                            color: Qt.hsla(0, 0, Qt.colorEqual(entry.modelData.color, "black") ? 1 : 0, 1)
                        }
                    }

                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        text: "≤"
                        color: Theme.textSecondary
                        font.pixelSize: Theme.fontSizeBase
                        font.family:    Theme.fontFamily
                    }

                    NumberStepper {
                        anchors.verticalCenter: parent.verticalCenter
                        value: entry.modelData.value
                        step:  0.5
                        onCommit: (v) => {
                            if (root.context) root.context.setThresholdValue(entry.index, v)
                        }
                    }
                }

                // ── Right: color · flash label · toggle · remove ───────────────
                Row {
                    anchors.right: parent.right; anchors.rightMargin: 12
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 10

                    ColorPicker {
                        anchors.verticalCenter: parent.verticalCenter
                        value: entry.modelData.color
                        onColorPicked: (hex) => {
                            if (root.context) root.context.setThresholdColor(entry.index, hex)
                        }
                    }

                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        text: "Flash"
                        color: Theme.textMuted
                        font.pixelSize: Theme.fontSizeSmall
                        font.family:    Theme.fontFamily
                    }

                    ToggleSwitch {
                        anchors.verticalCenter: parent.verticalCenter
                        checked: entry.modelData.flash
                        onToggled: (v) => {
                            if (root.context) root.context.setThresholdFlash(entry.index, v)
                        }
                    }

                    // Remove button
                    Rectangle {
                        anchors.verticalCenter: parent.verticalCenter
                        width: 22; height: 22; radius: 11
                        color:        rmArea.containsMouse ? "#40FF4444" : "transparent"
                        border.width: 1
                        border.color: rmArea.containsMouse ? "#FF4444"   : Theme.border
                        Behavior on color        { ColorAnimation { duration: 80 } }
                        Behavior on border.color { ColorAnimation { duration: 80 } }

                        Text {
                            anchors.centerIn: parent
                            text:  "×"
                            font.pixelSize: 14; font.family: Theme.fontFamily
                            color: rmArea.containsMouse ? "#FF4444" : Theme.textMuted
                            Behavior on color { ColorAnimation { duration: 80 } }
                        }

                        MouseArea {
                            id: rmArea
                            anchors.fill: parent; hoverEnabled: true
                            onClicked: { if (root.context) root.context.removeThreshold(entry.index) }
                        }
                    }
                }

                HoverHandler { id: rowHover }
            }

            // ── Row 2: flash options (target + speed) — animated height ────────
            Rectangle {
                id: row2
                anchors.left: parent.left; anchors.right: parent.right

                readonly property bool expanded: entry.modelData.flash
                height: expanded ? 36 : 0
                clip:   true
                color:  Theme.surfaceAlt
                opacity: expanded ? 1 : 0

                Behavior on height  { NumberAnimation { duration: 150; easing.type: Easing.OutCubic } }
                Behavior on opacity { NumberAnimation { duration: 120 } }

                readonly property var _targets: ["value", "text", "widget"]

                Row {
                    anchors.left: parent.left; anchors.leftMargin: 44
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 12

                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        text: "Target"
                        color: Theme.textMuted
                        font.pixelSize: Theme.fontSizeSmall
                        font.family:    Theme.fontFamily
                    }

                    ThemedComboBox {
                        anchors.verticalCenter: parent.verticalCenter
                        model:         row2._targets
                        implicitWidth: 76
                        currentIndex: {
                            var i = row2._targets.indexOf(entry.modelData.flashTarget)
                            return i >= 0 ? i : 0
                        }
                        onActivated: (i) => {
                            if (root.context)
                                root.context.setThresholdFlashTarget(entry.index, row2._targets[i])
                        }
                    }

                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        text: "Speed"
                        color: Theme.textMuted
                        font.pixelSize: Theme.fontSizeSmall
                        font.family:    Theme.fontFamily
                    }

                    NumberStepper {
                        anchors.verticalCenter: parent.verticalCenter
                        value: entry.modelData.flashSpeed
                        step: 1; min: 1; max: 20
                        onCommit: (v) => {
                            if (root.context) root.context.setThresholdFlashSpeed(entry.index, v)
                        }
                    }
                }
            }

            // Separator
            Rectangle {
                anchors.left: parent.left; anchors.right: parent.right
                height: 1; color: Theme.border; opacity: 0.4
            }
        }
    }

    // ── Add threshold button ──────────────────────────────────────────────────
    Rectangle {
        anchors.left: parent.left; anchors.right: parent.right
        height: 40
        color: "transparent"

        Rectangle {
            anchors.left: parent.left; anchors.leftMargin: 16
            anchors.verticalCenter: parent.verticalCenter
            width: 130; height: 26; radius: 4
            color:        addArea.containsMouse ? Theme.surfaceRaised : "transparent"
            border.width: 1; border.color: Theme.border
            Behavior on color { ColorAnimation { duration: 80 } }

            Row {
                anchors.centerIn: parent
                spacing: 6
                Text {
                    anchors.verticalCenter: parent.verticalCenter
                    text:  "+"
                    font.pixelSize: 14; font.family: Theme.fontFamily
                    color: addArea.containsMouse ? Theme.accent : Theme.textMuted
                    Behavior on color { ColorAnimation { duration: 80 } }
                }
                Text {
                    anchors.verticalCenter: parent.verticalCenter
                    text:  "Add threshold"
                    font.pixelSize: Theme.fontSizeSmall; font.family: Theme.fontFamily
                    color: addArea.containsMouse ? Theme.accent : Theme.textMuted
                    Behavior on color { ColorAnimation { duration: 80 } }
                }
            }

            MouseArea {
                id: addArea
                anchors.fill: parent; hoverEnabled: true
                onClicked: { if (root.context) root.context.addDefaultThreshold() }
            }
        }
    }
}
