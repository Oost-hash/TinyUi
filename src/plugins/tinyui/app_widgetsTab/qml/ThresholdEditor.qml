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
import QtQuick.Window

Column {
    id: thresholdEditorRoot

    readonly property var hostWindow: Window.window
    property var theme: hostWindow && hostWindow.theme ? hostWindow.theme : null
    property var entries: []
    property bool editable: false

    signal updateThreshold(int index, string key, var value)
    signal removeThreshold(int index)
    signal addThreshold

    function c(token, fallback) {
        return theme ? theme[token] : fallback;
    }

    function f(token, fallback) {
        return theme ? theme[token] : fallback;
    }

    anchors.left: parent ? parent.left : undefined
    anchors.right: parent ? parent.right : undefined

    Rectangle {
        anchors.left: parent.left
        anchors.right: parent.right
        height: thresholdDescription.implicitHeight + 16
        color: "transparent"

        Text {
            id: thresholdDescription
            anchors.left: parent.left
            anchors.leftMargin: 16
            anchors.right: parent.right
            anchors.rightMargin: 16
            anchors.verticalCenter: parent.verticalCenter
            wrapMode: Text.WordWrap
            text: "Each entry is an upper bound. The color is used while the value is at or below that number; flash can hide the selected target on each tick."
            color: thresholdEditorRoot.c("textMuted", "#878a98")
            font.pixelSize: thresholdEditorRoot.f("fontSizeSmall", 11)
            font.family: thresholdEditorRoot.f("fontFamily", "sans-serif")
        }

        Rectangle {
            anchors.bottom: parent.bottom
            width: parent.width
            height: 1
            color: thresholdEditorRoot.c("border", "#464b57")
            opacity: 0.4
        }
    }

    Repeater {
        model: thresholdEditorRoot.entries

        delegate: Column {
            id: thresholdEntry

            required property var modelData
            required property int index
            readonly property var targets: ["value", "text", "widget", "border"]

            anchors.left: parent ? parent.left : undefined
            anchors.right: parent ? parent.right : undefined

            Rectangle {
                id: thresholdRow
                anchors.left: parent.left
                anchors.right: parent.right
                height: 44
                color: "transparent"

                Rectangle {
                    anchors.fill: parent
                    opacity: thresholdHover.hovered ? 1 : 0
                    Behavior on opacity {
                        NumberAnimation {
                            duration: 120
                        }
                    }
                    gradient: Gradient {
                        orientation: Gradient.Horizontal
                        GradientStop {
                            position: 0.0
                            color: "transparent"
                        }
                        GradientStop {
                            position: 0.6
                            color: "transparent"
                        }
                        GradientStop {
                            position: 1.0
                            color: "#20dec184"
                        }
                    }
                }

                Row {
                    anchors.left: parent.left
                    anchors.leftMargin: 16
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 8

                    Rectangle {
                        width: 18
                        height: 18
                        radius: 9
                        anchors.verticalCenter: parent.verticalCenter
                        color: thresholdEntry.modelData.color
                        border.width: 1
                        border.color: thresholdEditorRoot.c("border", "#464b57")

                        Text {
                            anchors.centerIn: parent
                            text: thresholdEntry.index + 1
                            color: "#ffffff"
                            font.pixelSize: 9
                            font.family: thresholdEditorRoot.f("fontFamily", "sans-serif")
                            font.weight: Font.Bold
                        }
                    }

                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        text: "<="
                        color: thresholdEditorRoot.c("textSecondary", "#a9afbc")
                        font.pixelSize: thresholdEditorRoot.f("fontSizeBase", 13)
                        font.family: thresholdEditorRoot.f("fontFamily", "sans-serif")
                    }

                    NumberStepper {
                        anchors.verticalCenter: parent.verticalCenter
                        width: 80
                        value: thresholdEntry.modelData.value
                        step: 0.5
                        decimals: 1
                        enabled: thresholdEditorRoot.editable
                        theme: thresholdEditorRoot.theme
                        onCommit: value => thresholdEditorRoot.updateThreshold(thresholdEntry.index, "value", value)
                    }
                }

                Row {
                    anchors.right: parent.right
                    anchors.rightMargin: 12
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 8

                    ColorPicker {
                        anchors.verticalCenter: parent.verticalCenter
                        value: thresholdEntry.modelData.color
                        enabled: thresholdEditorRoot.editable
                        theme: thresholdEditorRoot.theme
                        onColorPicked: hex => thresholdEditorRoot.updateThreshold(thresholdEntry.index, "color", hex)
                    }

                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        text: "Flash"
                        color: thresholdEditorRoot.c("textMuted", "#878a98")
                        font.pixelSize: thresholdEditorRoot.f("fontSizeSmall", 11)
                        font.family: thresholdEditorRoot.f("fontFamily", "sans-serif")
                    }

                    ToggleSwitch {
                        anchors.verticalCenter: parent.verticalCenter
                        checked: thresholdEntry.modelData.flash === true
                        enabled: thresholdEditorRoot.editable
                        theme: thresholdEditorRoot.theme
                        onToggled: value => thresholdEditorRoot.updateThreshold(thresholdEntry.index, "flash", value)
                    }

                    Rectangle {
                        anchors.verticalCenter: parent.verticalCenter
                        width: 22
                        height: 22
                        radius: 4
                        color: removeHover.hovered ? "#40FF4444" : "transparent"
                        border.width: 1
                        border.color: removeHover.hovered ? "#FF4444" : thresholdEditorRoot.c("border", "#464b57")
                        Behavior on color {
                            ColorAnimation {
                                duration: 80
                            }
                        }
                        Behavior on border.color {
                            ColorAnimation {
                                duration: 80
                            }
                        }

                        Text {
                            anchors.centerIn: parent
                            text: "x"
                            color: removeHover.hovered ? "#FF4444" : thresholdEditorRoot.c("textMuted", "#878a98")
                            font.pixelSize: thresholdEditorRoot.f("fontSizeBase", 13)
                            font.family: thresholdEditorRoot.f("fontFamily", "sans-serif")
                        }

                        MouseArea {
                            anchors.fill: parent
                            enabled: thresholdEditorRoot.editable
                            onClicked: thresholdEditorRoot.removeThreshold(thresholdEntry.index)
                        }

                        HoverHandler {
                            id: removeHover
                        }
                    }
                }

                HoverHandler {
                    id: thresholdHover
                }
            }

            Rectangle {
                anchors.left: parent.left
                anchors.right: parent.right
                height: thresholdEntry.modelData.flash === true ? 72 : 36
                clip: true
                color: thresholdEditorRoot.c("surfaceAlt", "#2f343e")
                opacity: 1

                Behavior on height {
                    NumberAnimation {
                        duration: 150
                        easing.type: Easing.OutCubic
                    }
                }

                Column {
                    anchors.left: parent.left
                    anchors.leftMargin: 44
                    anchors.right: parent.right
                    anchors.rightMargin: 12
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 6

                    Row {
                        spacing: 10

                        Text {
                            anchors.verticalCenter: parent.verticalCenter
                            width: 44
                            text: "Color"
                            color: thresholdEditorRoot.c("textMuted", "#878a98")
                            font.pixelSize: thresholdEditorRoot.f("fontSizeSmall", 11)
                            font.family: thresholdEditorRoot.f("fontFamily", "sans-serif")
                        }

                        TargetPicker {
                            anchors.verticalCenter: parent.verticalCenter
                            targets: thresholdEntry.targets
                            value: thresholdEntry.modelData.colorTarget
                            enabled: thresholdEditorRoot.editable
                            theme: thresholdEditorRoot.theme
                            onPicked: value => thresholdEditorRoot.updateThreshold(thresholdEntry.index, "colorTarget", value)
                        }
                    }

                    Row {
                        visible: thresholdEntry.modelData.flash === true
                        spacing: 10

                        Text {
                            anchors.verticalCenter: parent.verticalCenter
                            width: 44
                            text: "Flash"
                            color: thresholdEditorRoot.c("textMuted", "#878a98")
                            font.pixelSize: thresholdEditorRoot.f("fontSizeSmall", 11)
                            font.family: thresholdEditorRoot.f("fontFamily", "sans-serif")
                        }

                        TargetPicker {
                            anchors.verticalCenter: parent.verticalCenter
                            targets: thresholdEntry.targets
                            value: thresholdEntry.modelData.flashTarget
                            enabled: thresholdEditorRoot.editable
                            theme: thresholdEditorRoot.theme
                            onPicked: value => thresholdEditorRoot.updateThreshold(thresholdEntry.index, "flashTarget", value)
                        }

                        Text {
                            anchors.verticalCenter: parent.verticalCenter
                            text: "Speed"
                            color: thresholdEditorRoot.c("textMuted", "#878a98")
                            font.pixelSize: thresholdEditorRoot.f("fontSizeSmall", 11)
                            font.family: thresholdEditorRoot.f("fontFamily", "sans-serif")
                        }

                        NumberStepper {
                            anchors.verticalCenter: parent.verticalCenter
                            width: 80
                            value: thresholdEntry.modelData.flashSpeed
                            step: 1
                            min: 1
                            max: 20
                            enabled: thresholdEditorRoot.editable
                            theme: thresholdEditorRoot.theme
                            onCommit: value => thresholdEditorRoot.updateThreshold(thresholdEntry.index, "flashSpeed", Math.round(value))
                        }
                    }
                }
            }

            Rectangle {
                anchors.left: parent.left
                anchors.right: parent.right
                height: 1
                color: thresholdEditorRoot.c("border", "#464b57")
                opacity: 0.4
            }
        }
    }

    Rectangle {
        anchors.left: parent.left
        anchors.right: parent.right
        height: 40
        color: "transparent"

        Rectangle {
            anchors.left: parent.left
            anchors.leftMargin: 16
            anchors.verticalCenter: parent.verticalCenter
            width: 130
            height: 26
            radius: 4
            color: addHover.hovered ? thresholdEditorRoot.c("surfaceRaised", "#3b414d") : "transparent"
            border.width: 1
            border.color: thresholdEditorRoot.c("border", "#464b57")
            Behavior on color {
                ColorAnimation {
                    duration: 80
                }
            }

            Row {
                anchors.centerIn: parent
                spacing: 6

                Text {
                    anchors.verticalCenter: parent.verticalCenter
                    text: "+"
                    color: addHover.hovered ? thresholdEditorRoot.c("accent", "#4a9eff") : thresholdEditorRoot.c("textMuted", "#878a98")
                    font.pixelSize: thresholdEditorRoot.f("fontSizeBase", 13)
                    font.family: thresholdEditorRoot.f("fontFamily", "sans-serif")
                }

                Text {
                    anchors.verticalCenter: parent.verticalCenter
                    text: "Add threshold"
                    color: addHover.hovered ? thresholdEditorRoot.c("accent", "#4a9eff") : thresholdEditorRoot.c("textMuted", "#878a98")
                    font.pixelSize: thresholdEditorRoot.f("fontSizeSmall", 11)
                    font.family: thresholdEditorRoot.f("fontFamily", "sans-serif")
                }
            }

            MouseArea {
                anchors.fill: parent
                enabled: thresholdEditorRoot.editable
                onClicked: thresholdEditorRoot.addThreshold()
            }

            HoverHandler {
                id: addHover
            }
        }
    }
}
