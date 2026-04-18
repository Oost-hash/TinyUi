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
    id: textInputBoxRoot

    property var theme: Window.window && Window.window.theme ? Window.window.theme : null
    property string textValue: ""
    signal commit(string text)

    function c(token, fallback) {
        return theme ? theme[token] : fallback;
    }

    function f(token, fallback) {
        return theme ? theme[token] : fallback;
    }

    width: 120
    height: 28
    radius: 4
    color: enabled ? textInputBoxRoot.c("surfaceFloating", "#20242b") : textInputBoxRoot.c("surfaceAlt", "#2f343e")
    border.width: 1
    border.color: textInput.activeFocus ? textInputBoxRoot.c("accent", "#4a9eff") : textInputBoxRoot.c("border", "#464b57")
    opacity: enabled ? 1 : 0.6
    Behavior on border.color {
        ColorAnimation {
            duration: 80
        }
    }

    TextInput {
        id: textInput
        anchors.fill: parent
        anchors.leftMargin: 8
        anchors.rightMargin: 8
        verticalAlignment: TextInput.AlignVCenter
        text: textInputBoxRoot.textValue
        color: textInputBoxRoot.c("text", "#dce0e5")
        font.pixelSize: textInputBoxRoot.f("fontSizeSmall", 11)
        font.family: textInputBoxRoot.f("fontFamily", "sans-serif")
        selectByMouse: true
        enabled: textInputBoxRoot.enabled

        onEditingFinished: {
            textInputBoxRoot.textValue = text;
            textInputBoxRoot.commit(text);
        }
    }
}
