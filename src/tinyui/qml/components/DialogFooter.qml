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

Rectangle {
    id: footer

    property bool showRevert: false
    property bool showSave:   false
    property bool showClose:  true

    property bool revertEnabled: true
    property bool saveEnabled:   true
    property string saveLabel:   "Save"

    signal revertClicked()
    signal saveClicked()
    signal closeClicked()

    height: 48
    color: Theme.surfaceAlt

    Rectangle { width: footer.width; height: 1; color: Theme.border }

    Row {
        anchors.right: footer.right; anchors.rightMargin: 16
        anchors.verticalCenter: footer.verticalCenter
        spacing: 8
        topPadding: 1

        Rectangle {
            visible: footer.showRevert
            width: 80; height: 32; radius: 5
            color: revertHov.containsMouse ? Theme.surfaceFloating : Theme.surfaceRaised
            opacity: footer.revertEnabled ? 1 : 0.4
            Behavior on color   { ColorAnimation { duration: 80 } }
            Behavior on opacity { NumberAnimation { duration: 120 } }
            Text { anchors.centerIn: parent; text: "Revert"; color: Theme.text
                   font.pixelSize: Theme.fontSizeBase; font.family: Theme.fontFamily }
            MouseArea { id: revertHov; anchors.fill: parent; hoverEnabled: true
                onClicked: if (footer.revertEnabled) footer.revertClicked() }
        }

        Rectangle {
            visible: footer.showSave
            width: 80; height: 32; radius: 5
            color: saveHov.containsMouse ? Theme.accentHover : Theme.accent
            opacity: footer.saveEnabled ? 1 : 0.4
            Behavior on color   { ColorAnimation { duration: 80 } }
            Behavior on opacity { NumberAnimation { duration: 120 } }
            Text { anchors.centerIn: parent; text: footer.saveLabel; color: Theme.accentText
                   font.pixelSize: Theme.fontSizeBase; font.family: Theme.fontFamily
                   font.weight: Font.Medium }
            MouseArea { id: saveHov; anchors.fill: parent; hoverEnabled: true
                onClicked: if (footer.saveEnabled) footer.saveClicked() }
        }

        Rectangle {
            visible: footer.showClose
            width: 80; height: 32; radius: 5
            color: closeHov.containsMouse ? Theme.surfaceFloating : Theme.surfaceRaised
            Behavior on color { ColorAnimation { duration: 80 } }
            Text { anchors.centerIn: parent; text: "Close"; color: Theme.text
                   font.pixelSize: Theme.fontSizeBase; font.family: Theme.fontFamily }
            MouseArea { id: closeHov; anchors.fill: parent; hoverEnabled: true
                onClicked: footer.closeClicked() }
        }
    }
}
