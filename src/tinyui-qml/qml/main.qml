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
import QtQuick.Layouts
import "layout"
import "tabs"

ApplicationWindow {
    id: root

    width: 900
    height: 600
    minimumWidth: 400
    minimumHeight: 300
    visible: true

    title: appName
    // Windows: frameless + custom TitleBar + DWM chrome.
    // Linux/macOS: server-side decorations — compositor/AppKit verzorgt chrome.
    //              Onze TitleBar fungeert als menu bar onder de native chrome.
    readonly property bool nativeChrome: Qt.platform.os === "linux" || Qt.platform.os === "osx"
    flags: nativeChrome ? Qt.Window : Qt.Window | Qt.FramelessWindowHint
    color: theme.surface

    // Beide backdrops dekken alleen de content area (tussen titelbalk en statusbalk).
    // Mutual exclusion wordt afgedwongen in Python — ze zijn nooit tegelijk actief.
    // Op Linux: geen custom titelbalk, dus content begint op y:0.

    readonly property int contentTop: Qt.platform.os === "linux" ? 0 : theme.titleBarHeight

    // Vangt klikken buiten een open menu popup op — sluit popup, menu blijft open
    MouseArea {
        x: 0; y: root.contentTop
        width: parent.width
        height: parent.height - root.contentTop - 32
        z: 4
        enabled: menuViewModel.menuOpen
        propagateComposedEvents: true
        onClicked: mouse => {
            menuViewModel.dismissActivePopup()
            mouse.accepted = false
        }
    }

    // Vangt klikken buiten de plugin dropdown op — sluit dropdown
    MouseArea {
        x: 0; y: root.contentTop
        width: parent.width
        height: parent.height - root.contentTop - 32
        z: 3
        enabled: statusBarViewModel.pluginDropdownOpen
        propagateComposedEvents: true
        onClicked: mouse => {
            statusBarViewModel.closePluginDropdown()
            mouse.accepted = false
        }
    }

    // Op Linux/macOS: native chrome verzorgt resize
    ResizeHandles { visible: !root.nativeChrome }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        TitleBar {
            Layout.fillWidth: true
            z: 1  // dropdowns renderen boven StyledTabBar en content
        }

        StyledTabBar {
            Layout.fillWidth: true
        }

        // Tab content met fade-transitie
        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true

            HomeTab {
                anchors.fill: parent
                viewModel: homeTabViewModel
                opacity: tabViewModel.currentIndex === 0 ? 1 : 0
                enabled: tabViewModel.currentIndex === 0
                Behavior on opacity {
                    NumberAnimation { duration: 180; easing.type: Easing.OutCubic }
                }
            }

            SettingsTab {
                anchors.fill: parent
                viewModel: settingsTabViewModel
                opacity: tabViewModel.currentIndex === 1 ? 1 : 0
                enabled: tabViewModel.currentIndex === 1
                Behavior on opacity {
                    NumberAnimation { duration: 180; easing.type: Easing.OutCubic }
                }
            }
        }

        StatusBar {
            Layout.fillWidth: true
        }
    }
}
