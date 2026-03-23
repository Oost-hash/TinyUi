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

// Theme-styled ComboBox for string enum settings.
ComboBox {
    id: root

    implicitWidth:  120
    implicitHeight:  28

    contentItem: Text {
        leftPadding: 8
        rightPadding: root.indicator.width + 4
        text: root.displayText
        color: theme.text
        font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }

    indicator: Text {
        x: root.width - width - 8
        anchors.verticalCenter: root.verticalCenter
        text: "▾"
        color: theme.textMuted
        font.pixelSize: 10
    }

    background: Rectangle {
        color: theme.surfaceFloating
        border.width: 1
        border.color: root.popup.opened ? theme.accent : theme.border
        radius: 4
        Behavior on border.color { ColorAnimation { duration: 80 } }
    }

    popup: Popup {
        y: root.height + 2
        width: root.width
        padding: 0

        contentItem: ListView {
            clip: true
            implicitHeight: Math.min(contentHeight, 200)
            model: root.delegateModel
            currentIndex: root.highlightedIndex
        }

        background: Rectangle {
            color: theme.surfaceFloating
            border.width: 1; border.color: theme.border
            radius: 4
        }
    }

    delegate: ItemDelegate {
        width: root.popup.width
        height: 32
        highlighted: root.highlightedIndex === index

        contentItem: Text {
            text: modelData
            color: highlighted ? "#dec184" : theme.text
            font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
            verticalAlignment: Text.AlignVCenter
            leftPadding: 8
            Behavior on color { ColorAnimation { duration: 80 } }
        }

        background: Rectangle {
            color: highlighted ? theme.surfaceRaised : "transparent"
        }
    }
}
