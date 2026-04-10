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

Window {
    id: root

    property var widgets: []
    property var widgetEffects: null
    readonly property int widgetCount: widgets ? widgets.length : 0

    width: 420
    height: 220
    visible: true
    color: "#101114"
    title: "Widget API Preview"

    Rectangle {
        anchors.fill: parent
        color: "#101114"
    }

    Flow {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12

        Repeater {
            model: root.widgets

            delegate: TextWidget {
                widgetData: modelData
                widgetEffects: root.widgetEffects
            }
        }
    }
}
