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
import QtQuick.Controls
import TinyUI

TabBar {
    id: tabBar
    currentIndex: TabViewModel.currentIndex
    spacing: -1
    height: 42

    background: Rectangle {
        color: Theme.surfaceAlt

        // Bottom border — the line the tabs sit on
        Rectangle {
            anchors.bottom: parent.bottom
            width: parent.width
            height: 1
            color: Theme.border
        }
    }

    Repeater {
        model: TabViewModel.tabNames

        TabButton {
            id: tab
            required property string modelData
            text: modelData
            width: implicitWidth
            leftPadding: 20
            rightPadding: 20
            topPadding: 10
            bottomPadding: 10

            background: Rectangle {
                color: tab.checked ? Theme.surface : Theme.surfaceAlt

                Rectangle { anchors.left: parent.left;  width: 1; height: parent.height; color: Theme.border }
                Rectangle { anchors.right: parent.right; width: 1; height: parent.height; color: Theme.border }
                Rectangle {
                    visible: !tab.checked
                    anchors.bottom: parent.bottom; width: parent.width; height: 1; color: Theme.border
                }
            }

            contentItem: Text {
                text: tab.text
                color: tab.checked ? Theme.text : Theme.textSecondary
                font.pixelSize: Theme.fontSizeBase
                font.family: Theme.fontFamily
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
        }
    }

    onCurrentIndexChanged: TabViewModel.setCurrentIndex(currentIndex)
}
