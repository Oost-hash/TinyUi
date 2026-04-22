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

Item {
    id: root

    readonly property var hostWindow: Window.window
    property var theme: hostWindow && hostWindow.theme ? hostWindow.theme : null
    property color value: "#ffffff"
    signal colorPicked(string hex)

    implicitWidth: swatchRow.implicitWidth
    implicitHeight: swatchRow.implicitHeight

    property real _h: 0
    property real _s: 1
    property real _v: 1

    function c(token, fallback) {
        return theme ? theme[token] : fallback;
    }

    function f(token, fallback) {
        return theme ? theme[token] : fallback;
    }

    Component.onCompleted: root._syncFromValue()
    onValueChanged: root._syncFromValue()

    function _syncFromValue() {
        var current = Qt.colorEqual(root.value, "transparent") ? Qt.color("white") : root.value;
        root._h = current.hsvHue < 0 ? 0 : current.hsvHue;
        root._s = current.hsvSaturation;
        root._v = current.hsvValue;
    }

    function _currentColor() {
        return Qt.hsva(root._h, root._s, root._v, 1);
    }

    function _toHex(colorValue) {
        var red = Math.round(colorValue.r * 255).toString(16).padStart(2, "0");
        var green = Math.round(colorValue.g * 255).toString(16).padStart(2, "0");
        var blue = Math.round(colorValue.b * 255).toString(16).padStart(2, "0");
        return ("#" + red + green + blue).toUpperCase();
    }

    function _commitHex(text) {
        if (!/^#[0-9A-Fa-f]{6}$/.test(text)) {
            hexInput.text = root._toHex(root.value);
            return;
        }

        var hex = text.toUpperCase();
        root.value = hex;
        root.colorPicked(hex);
        hexInput.focus = false;
    }

    function _openPicker() {
        if (!root.enabled)
            return;

        root._syncFromValue();
        var global = swatch.mapToGlobal(swatch.width / 2, 0);
        pickerWindow.x = Math.round(global.x - pickerWindow.width / 2);
        pickerWindow.y = Math.round(global.y - pickerWindow.height);
        pickerWindow.show();
        pickerWindow.requestActivate();
    }

    Row {
        id: swatchRow
        spacing: 6
        anchors.verticalCenter: parent.verticalCenter
        opacity: root.enabled ? 1 : 0.6

        Rectangle {
            id: swatch
            width: 20
            height: 20
            radius: 4
            anchors.verticalCenter: parent.verticalCenter
            color: root.value
            border.width: 1
            border.color: root.c("border", "#464b57")

            MouseArea {
                anchors.fill: parent
                enabled: root.enabled
                cursorShape: root.enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
                onClicked: root._openPicker()
            }
        }

        Rectangle {
            width: 92
            height: 28
            radius: 4
            anchors.verticalCenter: parent.verticalCenter
            color: root.enabled ? root.c("surfaceFloating", "#20242b") : root.c("surfaceAlt", "#2f343e")
            border.width: 1
            border.color: hexInput.activeFocus ? root.c("accent", "#4a9eff") : root.c("border", "#464b57")

            Behavior on border.color {
                ColorAnimation {
                    duration: 80
                }
            }

            TextInput {
                id: hexInput
                anchors.fill: parent
                anchors.leftMargin: 8
                anchors.rightMargin: 8
                verticalAlignment: TextInput.AlignVCenter
                text: root._toHex(root.value)
                color: root.c("text", "#dce0e5")
                font.pixelSize: root.f("fontSizeSmall", 11)
                font.family: root.f("fontFamily", "sans-serif")
                maximumLength: 7
                selectByMouse: true
                enabled: root.enabled

                Keys.onReturnPressed: root._commitHex(text)
                Keys.onEscapePressed: {
                    text = root._toHex(root.value);
                    focus = false;
                }

                onActiveFocusChanged: {
                    if (!activeFocus)
                        text = root._toHex(root.value);
                }
            }
        }
    }

    Window {
        id: pickerWindow
        flags: Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        color: "transparent"
        width: 244
        height: pickerContent.height + arrow.height

        onActiveChanged: {
            if (!active)
                pickerWindow.hide();
        }

        Connections {
            target: root.hostWindow

            function onXChanged() {
                pickerWindow.hide();
            }

            function onYChanged() {
                pickerWindow.hide();
            }

            function onWidthChanged() {
                pickerWindow.hide();
            }

            function onHeightChanged() {
                pickerWindow.hide();
            }
        }

        readonly property int _arrowH: 10
        readonly property int _arrowW: 18

        Canvas {
            id: arrow
            anchors.bottom: parent.bottom
            anchors.horizontalCenter: parent.horizontalCenter
            width: pickerWindow._arrowW
            height: pickerWindow._arrowH

            onPaint: {
                var ctx = getContext("2d");
                ctx.clearRect(0, 0, width, height);
                ctx.fillStyle = root.c("border", "#464b57");
                ctx.beginPath();
                ctx.moveTo(0, 0);
                ctx.lineTo(width / 2, height);
                ctx.lineTo(width, 0);
                ctx.fill();

                ctx.fillStyle = root.c("surfaceFloating", "#20242b");
                ctx.beginPath();
                ctx.moveTo(1, 0);
                ctx.lineTo(width / 2, height - 1);
                ctx.lineTo(width - 1, 0);
                ctx.fill();
            }
        }

        Rectangle {
            id: pickerContent
            anchors.top: parent.top
            anchors.horizontalCenter: parent.horizontalCenter
            width: pickerWindow.width
            height: 268
            radius: 8
            color: root.c("surfaceFloating", "#20242b")
            border.width: 1
            border.color: root.c("border", "#464b57")

            Column {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 8

                Item {
                    id: svSquare
                    width: parent.width
                    height: 150

                    Rectangle {
                        anchors.fill: parent
                        radius: 4
                        color: Qt.hsva(root._h, 1, 1, 1)
                    }

                    Rectangle {
                        anchors.fill: parent
                        radius: 4
                        gradient: Gradient {
                            orientation: Gradient.Horizontal
                            GradientStop { position: 0.0; color: "white" }
                            GradientStop { position: 1.0; color: "transparent" }
                        }
                    }

                    Rectangle {
                        anchors.fill: parent
                        radius: 4
                        gradient: Gradient {
                            GradientStop { position: 0.0; color: "transparent" }
                            GradientStop { position: 1.0; color: "black" }
                        }
                    }

                    Rectangle {
                        x: root._s * svSquare.width - width / 2
                        y: (1 - root._v) * svSquare.height - height / 2
                        width: 10
                        height: 10
                        radius: 5
                        color: "transparent"
                        border.width: 2
                        border.color: root._v > 0.4 ? "black" : "white"
                    }

                    MouseArea {
                        anchors.fill: parent
                        onPositionChanged: mouse => svSquare._updateSV(mouse.x, mouse.y)
                        onPressed: mouse => svSquare._updateSV(mouse.x, mouse.y)
                    }

                    function _updateSV(mx, my) {
                        root._s = Math.max(0, Math.min(1, mx / svSquare.width));
                        root._v = Math.max(0, Math.min(1, 1 - my / svSquare.height));
                    }
                }

                Item {
                    id: hueSlider
                    width: parent.width
                    height: 14

                    Rectangle {
                        anchors.fill: parent
                        radius: 7
                        gradient: Gradient {
                            orientation: Gradient.Horizontal
                            GradientStop { position: 0 / 6; color: "#ff0000" }
                            GradientStop { position: 1 / 6; color: "#ffff00" }
                            GradientStop { position: 2 / 6; color: "#00ff00" }
                            GradientStop { position: 3 / 6; color: "#00ffff" }
                            GradientStop { position: 4 / 6; color: "#0000ff" }
                            GradientStop { position: 5 / 6; color: "#ff00ff" }
                            GradientStop { position: 6 / 6; color: "#ff0000" }
                        }
                    }

                    Rectangle {
                        x: root._h * hueSlider.width - width / 2
                        y: hueSlider.height / 2 - height / 2
                        width: 10
                        height: 14
                        radius: 3
                        color: "transparent"
                        border.width: 2
                        border.color: "white"
                    }

                    MouseArea {
                        anchors.fill: parent
                        onPositionChanged: mouse => root._h = Math.max(0, Math.min(1, mouse.x / hueSlider.width))
                        onPressed: mouse => root._h = Math.max(0, Math.min(1, mouse.x / hueSlider.width))
                    }
                }

                Row {
                    width: parent.width
                    spacing: 8

                    Rectangle {
                        width: 32
                        height: 28
                        radius: 4
                        color: root._currentColor()
                        border.width: 1
                        border.color: root.c("border", "#464b57")
                    }

                    Rectangle {
                        width: parent.width - 40
                        height: 28
                        radius: 4
                        color: root.c("surface", "#17181c")
                        border.width: 1
                        border.color: pickerHex.activeFocus ? root.c("accent", "#4a9eff") : root.c("border", "#464b57")

                        Behavior on border.color {
                            ColorAnimation {
                                duration: 80
                            }
                        }

                        TextInput {
                            id: pickerHex
                            anchors.fill: parent
                            anchors.leftMargin: 8
                            anchors.rightMargin: 8
                            verticalAlignment: TextInput.AlignVCenter
                            text: root._toHex(root._currentColor())
                            color: root.c("text", "#dce0e5")
                            font.pixelSize: root.f("fontSizeSmall", 11)
                            font.family: root.f("fontFamily", "sans-serif")
                            maximumLength: 7
                            selectByMouse: true

                            Connections {
                                target: root

                                function on_HChanged() {
                                    pickerHex.text = root._toHex(root._currentColor());
                                }

                                function on_SChanged() {
                                    pickerHex.text = root._toHex(root._currentColor());
                                }

                                function on_VChanged() {
                                    pickerHex.text = root._toHex(root._currentColor());
                                }
                            }

                            Keys.onReturnPressed: {
                                if (/^#[0-9A-Fa-f]{6}$/.test(text)) {
                                    root.value = text.toUpperCase();
                                    root._syncFromValue();
                                } else {
                                    text = root._toHex(root._currentColor());
                                }
                            }

                            Keys.onEscapePressed: {
                                text = root._toHex(root._currentColor());
                                focus = false;
                            }
                        }
                    }
                }

                Rectangle {
                    width: parent.width
                    height: 28
                    radius: 4
                    color: okArea.containsMouse ? root.c("accent", "#4a9eff") : root.c("surfaceRaised", "#3b414d")

                    Behavior on color {
                        ColorAnimation {
                            duration: 80
                        }
                    }

                    Text {
                        anchors.centerIn: parent
                        text: "OK"
                        color: okArea.containsMouse ? root.c("accentText", "#ffffff") : root.c("text", "#dce0e5")
                        font.pixelSize: root.f("fontSizeSmall", 11)
                        font.family: root.f("fontFamily", "sans-serif")
                        font.weight: Font.Medium
                    }

                    MouseArea {
                        id: okArea
                        anchors.fill: parent
                        hoverEnabled: true

                        onClicked: {
                            var hex = root._toHex(root._currentColor());
                            root.value = hex;
                            root.colorPicked(hex);
                            pickerWindow.hide();
                        }
                    }
                }
            }
        }
    }
}
