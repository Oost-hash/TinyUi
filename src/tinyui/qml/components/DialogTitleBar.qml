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
import TinyUI

Rectangle {
    id: root

    property string title: ""
    signal closeClicked()

    height: Theme.titleBarHeight
    color: Theme.surfaceAlt

    // startSystemMove() works on all platforms in Qt 6
    DragHandler {
        target: null
        onActiveChanged: if (active) root.Window.window.startSystemMove()
    }

    Text {
        anchors.left: parent.left; anchors.leftMargin: 16
        anchors.verticalCenter: parent.verticalCenter
        text: root.title
        color: Theme.text
        font.pixelSize: Theme.fontSizeBase; font.family: Theme.fontFamily
        font.weight: Font.DemiBold
    }

    WindowButton {
        anchors.right: maximizeBtn.left
        height: parent.height
        iconSource: "../../assets/icons/window-minimize.svg"
        onClicked: root.Window.window.showMinimized()
    }

    WindowButton {
        id: maximizeBtn
        anchors.right: closeBtn.left
        height: parent.height
        iconSource: root.Window.window.visibility === Window.Maximized
            ? "../../assets/icons/window-restore.svg"
            : "../../assets/icons/window-maximize.svg"
        onClicked: {
            if (root.Window.window.visibility === Window.Maximized)
                root.Window.window.showNormal()
            else
                root.Window.window.showMaximized()
        }
    }

    WindowButton {
        id: closeBtn
        anchors.right: parent.right
        height: parent.height
        iconSource: "../../assets/icons/window-close.svg"
        isCloseButton: true
        onClicked: root.closeClicked()
    }

    Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: Theme.border }
}
