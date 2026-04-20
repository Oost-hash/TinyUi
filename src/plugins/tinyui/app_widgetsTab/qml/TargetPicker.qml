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

Row {
    id: targetPickerRoot

    readonly property var hostWindow: Window.window
    property var theme: targetPickerRoot.hostWindow && targetPickerRoot.hostWindow.theme ? targetPickerRoot.hostWindow.theme : null
    property var targets: []
    property string value: ""
    signal picked(string value)

    spacing: 4

    Repeater {
        model: targetPickerRoot.targets

        delegate: TargetChip {
            id: targetDelegate

            required property string modelData

            label: targetDelegate.modelData
            checked: targetPickerRoot.value === targetDelegate.modelData
            enabled: targetPickerRoot.enabled
            theme: targetPickerRoot.theme
            onPicked: {
                targetPickerRoot.value = targetDelegate.modelData;
                targetPickerRoot.picked(targetDelegate.modelData);
            }
        }
    }

    component TargetChip: Rectangle {
        id: targetChipRoot

        property var theme: null
        property string label: ""
        property bool checked: false
        signal picked

        function c(token, fallback) {
            return theme ? theme[token] : fallback;
        }

        function f(token, fallback) {
            return theme ? theme[token] : fallback;
        }

        width: chipText.implicitWidth + 16
        height: 26
        radius: 4
        color: checked ? targetChipRoot.c("surfaceRaised", "#3b414d") : targetChipRoot.c("surfaceFloating", "#20242b")
        border.width: 1
        border.color: checked ? targetChipRoot.c("accent", "#4a9eff") : (chipHover.hovered ? targetChipRoot.c("accentHover", "#6bb6ff") : targetChipRoot.c("border", "#464b57"))
        opacity: enabled ? 1 : 0.6
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
            id: chipText
            anchors.centerIn: parent
            text: (targetChipRoot.checked ? "v " : "") + targetChipRoot.label
            color: targetChipRoot.checked ? targetChipRoot.c("accent", "#4a9eff") : targetChipRoot.c("text", "#dce0e5")
            font.pixelSize: targetChipRoot.f("fontSizeSmall", 11)
            font.family: targetChipRoot.f("fontFamily", "sans-serif")
        }

        MouseArea {
            anchors.fill: parent
            enabled: targetChipRoot.enabled
            onClicked: targetChipRoot.picked()
        }

        HoverHandler {
            id: chipHover
        }
    }
}
