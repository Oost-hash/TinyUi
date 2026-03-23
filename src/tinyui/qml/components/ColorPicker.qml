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

Item {
    id: root

    property color value: "#ffffff"
    signal colorPicked(string hex)

    implicitWidth:  swatchRow.implicitWidth
    implicitHeight: swatchRow.implicitHeight

    // ── Interne HSV staat ─────────────────────────────────────────────────────
    property real _h: 0
    property real _s: 1
    property real _v: 1

    Component.onCompleted: _syncFromValue()
    onValueChanged: _syncFromValue()

    function _syncFromValue() {
        var c = Qt.colorEqual(value, "transparent") ? Qt.color("white") : value
        _h = c.hsvHue < 0 ? 0 : c.hsvHue
        _s = c.hsvSaturation
        _v = c.hsvValue
    }

    function _currentColor() { return Qt.hsva(_h, _s, _v, 1) }

    function _toHex(c) {
        var r = Math.round(c.r * 255).toString(16).padStart(2, "0")
        var g = Math.round(c.g * 255).toString(16).padStart(2, "0")
        var b = Math.round(c.b * 255).toString(16).padStart(2, "0")
        return "#" + r + g + b
    }

    // ── Collapsed: swatch + hex label ─────────────────────────────────────────
    Row {
        id: swatchRow
        spacing: 6
        anchors.verticalCenter: parent.verticalCenter

        Rectangle {
            id: swatch
            width: 20; height: 20; radius: 4
            anchors.verticalCenter: parent.verticalCenter
            color: root.value
            border.width: 1; border.color: theme.border

            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                onClicked: _openPicker()
            }
        }

        Rectangle {
            width: 92; height: 28; radius: 4
            anchors.verticalCenter: parent.verticalCenter
            color: theme.surfaceFloating
            border.width: 1
            border.color: hexInput.activeFocus ? theme.accent : theme.border
            Behavior on border.color { ColorAnimation { duration: 80 } }

            TextInput {
                id: hexInput
                anchors.fill: parent; anchors.leftMargin: 8; anchors.rightMargin: 8
                verticalAlignment: TextInput.AlignVCenter
                text: root._toHex(root.value)
                color: theme.text
                font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
                maximumLength: 7; selectByMouse: true
                Keys.onReturnPressed: _commitHex(text)
                Keys.onEscapePressed: { text = root._toHex(root.value); focus = false }
                onActiveFocusChanged: if (!activeFocus) text = root._toHex(root.value)
            }
        }
    }

    function _commitHex(txt) {
        if (/^#[0-9A-Fa-f]{6}$/.test(txt)) {
            root.value = txt
            root.colorPicked(txt)
            hexInput.focus = false
        } else {
            hexInput.text = root._toHex(root.value)
        }
    }

    function _openPicker() {
        root._syncFromValue()
        // Position: above the swatch, arrow points down toward the swatch
        var arrowH  = 10
        var winW    = pickerWin.width
        var winH    = pickerWin.height
        var global  = swatch.mapToGlobal(swatch.width / 2, 0)
        pickerWin.x = Math.round(global.x - winW / 2)
        pickerWin.y = Math.round(global.y - winH)
        pickerWin.show()
        pickerWin.requestActivate()
    }

    // ── Picker window ─────────────────────────────────────────────────────────
    // Qt.Tool = no taskbar entry, always on top of the parent window
    // Transparent so the arrow tip can draw outside the rectangular bounds
    Window {
        id: pickerWin
        flags:  Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        color:  "transparent"
        width:  244
        height: pickerContent.height + arrow.height

        // Close when focus is lost (click outside the window)
        onActiveChanged: if (!active) pickerWin.hide()

        // Close when the parent window moves or resizes
        Connections {
            target: root.Window.window
            function onXChanged() { pickerWin.hide() }
            function onYChanged() { pickerWin.hide() }
            function onWidthChanged()  { pickerWin.hide() }
            function onHeightChanged() { pickerWin.hide() }
        }

        readonly property int _arrowH: 10
        readonly property int _arrowW: 18
        readonly property int _radius: 8

        // ── Arrow ────────────────────────────────────────────────────
        Canvas {
            id: arrow
            anchors.bottom: parent.bottom
            anchors.horizontalCenter: parent.horizontalCenter
            width: pickerWin._arrowW
            height: pickerWin._arrowH

            onPaint: {
                var ctx = getContext("2d")
                ctx.clearRect(0, 0, width, height)
                ctx.fillStyle   = theme.border
                ctx.strokeStyle = theme.border
                ctx.beginPath()
                ctx.moveTo(0, 0)
                ctx.lineTo(width / 2, height)
                ctx.lineTo(width, 0)
                ctx.fill()
                ctx.fillStyle = theme.surfaceFloating
                ctx.beginPath()
                ctx.moveTo(1, 0)
                ctx.lineTo(width / 2, height - 1)
                ctx.lineTo(width - 1, 0)
                ctx.fill()
            }

        }

        // ── Picker inhoud ─────────────────────────────────────────────────────
        Rectangle {
            id: pickerContent
            anchors.top: parent.top
            anchors.horizontalCenter: parent.horizontalCenter
            width: pickerWin.width
            height: 268
            radius: pickerWin._radius
            color: theme.surfaceFloating
            border.width: 1; border.color: theme.border

            Column {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 8

                // ── SV square ─────────────────────────────────────────────────
                Item {
                    id: svSquare
                    width: parent.width; height: 150

                    Rectangle { anchors.fill: parent; radius: 4; color: Qt.hsva(root._h, 1, 1, 1) }
                    Rectangle {
                        anchors.fill: parent; radius: 4
                        gradient: Gradient {
                            orientation: Gradient.Horizontal
                            GradientStop { position: 0.0; color: "white" }
                            GradientStop { position: 1.0; color: "transparent" }
                        }
                    }
                    Rectangle {
                        anchors.fill: parent; radius: 4
                        gradient: Gradient {
                            GradientStop { position: 0.0; color: "transparent" }
                            GradientStop { position: 1.0; color: "black" }
                        }
                    }

                    // Cursor
                    Rectangle {
                        x: root._s * svSquare.width  - width  / 2
                        y: (1 - root._v) * svSquare.height - height / 2
                        width: 10; height: 10; radius: 5
                        color: "transparent"
                        border.width: 2
                        border.color: root._v > 0.4 ? "black" : "white"
                    }

                    MouseArea {
                        anchors.fill: parent
                        onPositionChanged: (m) => svSquare._updateSV(m.x, m.y)
                        onPressed:         (m) => svSquare._updateSV(m.x, m.y)
                    }

                    function _updateSV(mx, my) {
                        root._s = Math.max(0, Math.min(1, mx / svSquare.width))
                        root._v = Math.max(0, Math.min(1, 1 - my / svSquare.height))
                    }
                }

                // ── Hue slider ────────────────────────────────────────────────
                Item {
                    id: hueSlider
                    width: parent.width; height: 14

                    Rectangle {
                        anchors.fill: parent; radius: 7
                        gradient: Gradient {
                            orientation: Gradient.Horizontal
                            GradientStop { position: 0/6; color: "#ff0000" }
                            GradientStop { position: 1/6; color: "#ffff00" }
                            GradientStop { position: 2/6; color: "#00ff00" }
                            GradientStop { position: 3/6; color: "#00ffff" }
                            GradientStop { position: 4/6; color: "#0000ff" }
                            GradientStop { position: 5/6; color: "#ff00ff" }
                            GradientStop { position: 6/6; color: "#ff0000" }
                        }
                    }

                    Rectangle {
                        x: root._h * hueSlider.width - width / 2
                        y: hueSlider.height / 2 - height / 2
                        width: 10; height: 14; radius: 3
                        color: "transparent"
                        border.width: 2; border.color: "white"
                    }

                    MouseArea {
                        anchors.fill: parent
                        onPositionChanged: (m) => root._h = Math.max(0, Math.min(1, m.x / hueSlider.width))
                        onPressed:         (m) => root._h = Math.max(0, Math.min(1, m.x / hueSlider.width))
                    }
                }

                // ── Preview + hex ─────────────────────────────────────────────
                Row {
                    width: parent.width
                    spacing: 8

                    Rectangle {
                        width: 32; height: 28; radius: 4
                        color: root._currentColor()
                        border.width: 1; border.color: theme.border
                    }

                    Rectangle {
                        width: parent.width - 32 - 8; height: 28; radius: 4
                        color: theme.surface
                        border.width: 1
                        border.color: pickerHex.activeFocus ? theme.accent : theme.border
                        Behavior on border.color { ColorAnimation { duration: 80 } }

                        TextInput {
                            id: pickerHex
                            anchors.fill: parent; anchors.leftMargin: 8; anchors.rightMargin: 8
                            verticalAlignment: TextInput.AlignVCenter
                            text: root._toHex(root._currentColor())
                            color: theme.text
                            font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
                            maximumLength: 7; selectByMouse: true

                            Connections {
                                target: root
                                function on_HChanged() { pickerHex.text = root._toHex(root._currentColor()) }
                                function on_SChanged() { pickerHex.text = root._toHex(root._currentColor()) }
                                function on_VChanged() { pickerHex.text = root._toHex(root._currentColor()) }
                            }

                            Keys.onReturnPressed: {
                                if (/^#[0-9A-Fa-f]{6}$/.test(text)) {
                                    root.value = text
                                    root._syncFromValue()
                                } else {
                                    text = root._toHex(root._currentColor())
                                }
                            }
                            Keys.onEscapePressed: { text = root._toHex(root._currentColor()); focus = false }
                        }
                    }
                }

                // ── OK knop ───────────────────────────────────────────────────
                Rectangle {
                    width: parent.width; height: 28; radius: 4
                    color: okArea.containsMouse ? theme.accent : theme.surfaceRaised
                    Behavior on color { ColorAnimation { duration: 80 } }

                    Text {
                        anchors.centerIn: parent
                        text: "OK"
                        color: okArea.containsMouse ? theme.accentText : theme.text
                        font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
                        font.weight: Font.Medium
                        Behavior on color { ColorAnimation { duration: 80 } }
                    }

                    MouseArea {
                        id: okArea
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: {
                            var hex = root._toHex(root._currentColor())
                            root.value = hex
                            root.colorPicked(hex)
                            pickerWin.hide()
                        }
                    }
                }
            }
        }
    }
}
