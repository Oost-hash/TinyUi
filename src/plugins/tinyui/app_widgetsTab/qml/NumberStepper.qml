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
import QtQuick.Window

Rectangle {
    id: stepperRoot

    readonly property var hostWindow: Window.window
    property var theme: stepperRoot.hostWindow && stepperRoot.hostWindow.theme ? stepperRoot.hostWindow.theme : null
    property real value: 0
    property real step: 1
    property real min: -999999
    property real max: 999999
    property int decimals: 0
    signal commit(real value)

    function c(token, fallback) {
        return theme ? theme[token] : fallback;
    }

    function f(token, fallback) {
        return theme ? theme[token] : fallback;
    }

    function clamped(nextValue) {
        return Math.max(min, Math.min(max, nextValue));
    }

    function rounded(nextValue) {
        var factor = Math.pow(10, decimals);
        return Math.round(nextValue * factor) / factor;
    }

    function formatted(nextValue) {
        return decimals > 0 ? Number(nextValue).toFixed(decimals) : String(Math.round(nextValue));
    }

    width: 120
    height: 28
    radius: 4
    color: enabled ? stepperRoot.c("surfaceFloating", "#20242b") : stepperRoot.c("surfaceAlt", "#2f343e")
    border.width: 1
    border.color: valueInput.activeFocus ? stepperRoot.c("accent", "#4a9eff") : stepperRoot.c("border", "#464b57")
    opacity: enabled ? 1 : 0.6
    Behavior on border.color {
        ColorAnimation {
            duration: 80
        }
    }

    Row {
        anchors.fill: parent

        StepperButton {
            label: "-"
            theme: stepperRoot.theme
            enabled: stepperRoot.enabled
            onPressed: {
                stepperRoot.value = stepperRoot.rounded(stepperRoot.clamped(stepperRoot.value - stepperRoot.step));
                stepperRoot.commit(stepperRoot.value);
            }
        }

        TextInput {
            id: valueInput
            width: parent.width - 48
            height: parent.height
            verticalAlignment: TextInput.AlignVCenter
            horizontalAlignment: TextInput.AlignHCenter
            color: stepperRoot.c("text", "#dce0e5")
            font.pixelSize: stepperRoot.f("fontSizeSmall", 11)
            font.family: stepperRoot.f("fontFamily", "sans-serif")
            selectByMouse: true
            validator: DoubleValidator {
                bottom: stepperRoot.min
                top: stepperRoot.max
                decimals: stepperRoot.decimals
                notation: DoubleValidator.StandardNotation
            }
            enabled: stepperRoot.enabled
            text: stepperRoot.formatted(stepperRoot.value)
            onEditingFinished: {
                var parsed = parseFloat(text);
                if (!isNaN(parsed)) {
                    stepperRoot.value = stepperRoot.rounded(stepperRoot.clamped(parsed));
                    stepperRoot.commit(stepperRoot.value);
                } else {
                    text = stepperRoot.formatted(stepperRoot.value);
                }
            }
        }

        StepperButton {
            label: "+"
            theme: stepperRoot.theme
            enabled: stepperRoot.enabled
            onPressed: {
                stepperRoot.value = stepperRoot.rounded(stepperRoot.clamped(stepperRoot.value + stepperRoot.step));
                stepperRoot.commit(stepperRoot.value);
            }
        }
    }

    component StepperButton: Item {
        id: stepperButtonRoot

        property var theme: null
        property string label: ""
        signal pressed

        function c(token, fallback) {
            return theme ? theme[token] : fallback;
        }

        function f(token, fallback) {
            return theme ? theme[token] : fallback;
        }

        width: 24
        height: parent ? parent.height : 28
        opacity: enabled ? 1 : 0.5

        Rectangle {
            anchors.fill: parent
            color: stepperHover.hovered ? stepperButtonRoot.c("surfaceRaised", "#3b414d") : "transparent"
            Behavior on color {
                ColorAnimation {
                    duration: 80
                }
            }
        }

        Text {
            anchors.centerIn: parent
            text: stepperButtonRoot.label
            color: stepperButtonRoot.c("textSecondary", "#a9afbc")
            font.pixelSize: stepperButtonRoot.f("fontSizeBase", 13)
            font.family: stepperButtonRoot.f("fontFamily", "sans-serif")
        }

        MouseArea {
            anchors.fill: parent
            enabled: stepperButtonRoot.enabled
            onClicked: stepperButtonRoot.pressed()
        }

        HoverHandler {
            id: stepperHover
        }
    }
}
