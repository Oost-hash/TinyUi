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

TabBar {
    id: tabBar
    currentIndex: tabViewModel.currentIndex
    spacing: -1
    height: 42

    background: Rectangle {
        color: theme.surfaceAlt

        // Border-bottom (de lijn waarop de tabs staan)
        Rectangle {
            anchors.bottom: parent.bottom
            width: parent.width
            height: 1
            color: theme.border
        }
    }

    Repeater {
        model: tabViewModel.tabNames

        TabButton {
            id: tab
            text: modelData
            width: implicitWidth
            leftPadding: 20
            rightPadding: 20
            topPadding: 10
            bottomPadding: 10

            background: Rectangle {
                color: tab.checked ? theme.surface : theme.surfaceAlt

                Rectangle { anchors.left: parent.left;  width: 1; height: parent.height; color: theme.border }
                Rectangle { anchors.right: parent.right; width: 1; height: parent.height; color: theme.border }
                Rectangle {
                    visible: !tab.checked
                    anchors.bottom: parent.bottom; width: parent.width; height: 1; color: theme.border
                }
            }

            contentItem: Text {
                text: tab.text
                color: tab.checked ? theme.text : theme.textSecondary
                font.pixelSize: theme.fontSizeBase
                font.family: theme.fontFamily
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
        }
    }

    onCurrentIndexChanged: tabViewModel.setCurrentIndex(currentIndex)
}
