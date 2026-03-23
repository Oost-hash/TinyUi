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

// − [value] +
// Value field is read-only until clicked; commits on Enter or focus loss.
Row {
    id: root

    property real value: 0
    property real step:  1
    property real min:  -1e9
    property real max:   1e9

    signal commit(real v)

    spacing: 6

    function _decimals() {
        var s = step.toString()
        var dot = s.indexOf(".")
        return dot < 0 ? 0 : s.length - dot - 1
    }

    function _fmt(v) { return v.toFixed(_decimals()) }

    function _clamp(v) { return Math.min(max, Math.max(min, v)) }

    function _round(v) { return parseFloat(v.toFixed(_decimals())) }

    function _apply(v) {
        var clamped = _round(_clamp(v))
        stepEdit.text = _fmt(clamped)
        root.commit(clamped)
        stepperRow._editing = false
    }

    // Sync display when value changes externally
    onValueChanged: {
        if (!stepperRow._editing)
            stepEdit.text = _fmt(value)
    }

    // − button
    Item {
        width: 24; height: 26
        anchors.verticalCenter: parent.verticalCenter

        Text {
            anchors.centerIn: parent
            text: "\u2212"
            color: decArea.containsMouse ? theme.text : theme.textMuted
            font.pixelSize: theme.fontSizeBase; font.family: theme.fontFamily
            Behavior on color { ColorAnimation { duration: 80 } }
        }

        MouseArea {
            id: decArea; anchors.fill: parent; hoverEnabled: true
            onClicked: root._apply(parseFloat(stepEdit.text) - root.step)
        }
    }

    // Value box — transparent at rest, editable on click
    Rectangle {
        width: 72; height: 26
        anchors.verticalCenter: parent.verticalCenter
        radius: 3
        color: stepperRow._editing ? theme.surfaceFloating : "transparent"
        border.width: 1
        border.color: stepperRow._editing ? theme.accent
                    : numHov.hovered      ? theme.border
                    : "transparent"
        Behavior on border.color { ColorAnimation { duration: 80 } }
        Behavior on color        { ColorAnimation { duration: 80 } }

        TextInput {
            id: stepEdit
            anchors.fill: parent
            anchors.leftMargin: 5; anchors.rightMargin: 5
            horizontalAlignment: TextInput.AlignHCenter
            verticalAlignment:   TextInput.AlignVCenter
            text: root._fmt(root.value)
            color: stepperRow._editing ? theme.accent : theme.text
            font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
            selectByMouse: true
            readOnly: !stepperRow._editing
            inputMethodHints: Qt.ImhFormattedNumbersOnly
            Behavior on color { ColorAnimation { duration: 80 } }

            Keys.onReturnPressed: root._apply(parseFloat(text))
            Keys.onEscapePressed: {
                text = root._fmt(root.value)
                stepperRow._editing = false
            }
            onActiveFocusChanged: {
                if (!activeFocus && stepperRow._editing) {
                    root._apply(parseFloat(text))
                }
            }
        }

        HoverHandler {
            id: numHov
            enabled: !stepperRow._editing
            cursorShape: Qt.IBeamCursor
        }

        MouseArea {
            anchors.fill: parent
            enabled: !stepperRow._editing
            acceptedButtons: Qt.LeftButton
            onClicked: {
                stepperRow._editing = true
                stepEdit.forceActiveFocus()
                stepEdit.selectAll()
            }
        }
    }

    // + button
    Item {
        width: 24; height: 26
        anchors.verticalCenter: parent.verticalCenter

        Text {
            anchors.centerIn: parent
            text: "+"
            color: incArea.containsMouse ? theme.text : theme.textMuted
            font.pixelSize: theme.fontSizeBase; font.family: theme.fontFamily
            Behavior on color { ColorAnimation { duration: 80 } }
        }

        MouseArea {
            id: incArea; anchors.fill: parent; hoverEnabled: true
            onClicked: root._apply(parseFloat(stepEdit.text) + root.step)
        }
    }

    // Internal edit-mode state
    Item {
        id: stepperRow
        property bool _editing: false
        width: 0; height: 0; visible: false
    }
}
