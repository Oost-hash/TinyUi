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
import QtQuick.Layouts
import "../components"

// Generieke plugin widget tab — toont de actieve widget naam + placeholder.
// Wordt vervangen zodra het plugin widget systeem verder uitgewerkt is.

Item {
    Column {
        anchors.centerIn: parent
        spacing: 12

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: tabViewModel.currentTabTitle
            color: theme.text
            font.pixelSize: theme.fontSizeTitle
            font.family: theme.fontFamily
            font.weight: Font.DemiBold
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: "Plugin widget — coming soon"
            color: theme.textMuted
            font.pixelSize: theme.fontSizeSmall
            font.family: theme.fontFamily
        }
    }
}
