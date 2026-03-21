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

AbstractButton {
    id: btn
    property string label: ""
    property string popupKey: ""
    property bool active: popupKey !== "" && menuViewModel.activePopup === popupKey

    height: parent.height
    implicitWidth: btnText.implicitWidth + 24
    hoverEnabled: true

    onHoveredChanged: if (hovered && popupKey !== "") menuViewModel.hoverPopup(popupKey)
    onClicked: if (popupKey !== "") menuViewModel.clickPopup(popupKey)

    background: Item {
        Rectangle {
            anchors.fill: parent
            color: btn.active ? theme.surfaceAlt
                              : btn.hovered ? theme.surfaceFloating : "transparent"
        }
        // Zijkant-borders alleen als actief — verbindt visueel met de popup eronder
        Rectangle { visible: btn.active; anchors.left:  parent.left;  width: 1; height: parent.height; color: theme.border }
        Rectangle { visible: btn.active; anchors.right: parent.right; width: 1; height: parent.height; color: theme.border }
    }

    contentItem: Text {
        id: btnText
        text: btn.label
        color: "#FFFFFF"
        font.pixelSize: theme.fontSizeSmall
        font.family: theme.fontFamily
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
}
