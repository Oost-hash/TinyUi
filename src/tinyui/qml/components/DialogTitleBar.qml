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

Rectangle {
    id: root

    property string title: ""
    signal closeClicked()

    height: theme.titleBarHeight
    color: theme.surfaceAlt

    // startSystemMove() works on all platforms in Qt 6
    DragHandler {
        target: null
        onActiveChanged: if (active) root.Window.window.startSystemMove()
    }

    Text {
        anchors.left: parent.left; anchors.leftMargin: 16
        anchors.verticalCenter: parent.verticalCenter
        text: root.title
        color: theme.text
        font.pixelSize: theme.fontSizeBase; font.family: theme.fontFamily
        font.weight: Font.DemiBold
    }

    TitleBarButton {
        anchors.right: maximizeBtn.left
        height: parent.height
        iconText: icons.minimize
        onClicked: root.Window.window.showMinimized()
    }

    TitleBarButton {
        id: maximizeBtn
        anchors.right: closeBtn.left
        height: parent.height
        iconText: root.Window.window.visibility === Window.Maximized ? icons.restore : icons.maximize
        onClicked: {
            if (root.Window.window.visibility === Window.Maximized)
                root.Window.window.showNormal()
            else
                root.Window.window.showMaximized()
        }
    }

    TitleBarButton {
        id: closeBtn
        anchors.right: parent.right
        height: parent.height
        iconText: icons.close
        isCloseButton: true
        onClicked: root.closeClicked()
    }

    Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: theme.border }
}
