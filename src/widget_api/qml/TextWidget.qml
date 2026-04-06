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

    property var widgetData: ({})

    width: 180
    height: 72
    radius: 8
    color: widgetData && widgetData.backgroundColor ? widgetData.backgroundColor : "#CC000000"
    visible: widgetData && widgetData.visible !== undefined ? widgetData.visible : true

    readonly property string labelText: widgetData && widgetData.label ? widgetData.label : ""
    readonly property string sourceText: widgetData && widgetData.source ? widgetData.source : ""
    readonly property string displayText: widgetData && widgetData.displayText ? widgetData.displayText : ""
    readonly property string valueColor: widgetData && widgetData.textColor ? widgetData.textColor : "#E0E0E0"

    Column {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 4

        Text {
            text: root.labelText
            color: "#8F8F8F"
            font.pixelSize: 11
            font.family: "Segoe UI"
        }

        Text {
            text: root.displayText
            color: root.valueColor
            font.pixelSize: 24
            font.bold: true
            font.family: "Segoe UI"
        }

        Text {
            text: root.sourceText
            color: "#6E6E6E"
            font.pixelSize: 10
            font.family: "Segoe UI"
            visible: root.sourceText.length > 0
        }
    }
}
