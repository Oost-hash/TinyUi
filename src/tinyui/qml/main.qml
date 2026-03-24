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
import "."

ApplicationWindow {
    id: root

    width: 900
    height: 600
    minimumWidth: 400
    minimumHeight: 300
    visible: true

    // Minimum width computed once based on the longest description
    TextMetrics {
        id: _descMetrics
        font.family: theme.fontFamily
        font.pixelSize: theme.fontSizeSmall
    }
    function _minWidth(): int {
        var max = 0
        var widgets = coreViewModel.widgets
        for (var i = 0; i < widgets.length; i++) {
            _descMetrics.text = widgets[i].description
            if (_descMetrics.advanceWidth > max) max = _descMetrics.advanceWidth
        }
        return Math.ceil(16 + 200 + max + 56)  // colPad + colName + desc + colToggle
    }
    Component.onCompleted: minimumWidth = _minWidth()

    title: appName
    // Windows: frameless + custom TitleBar + DWM chrome.
    // Linux/macOS: server-side decorations — compositor/AppKit handles chrome.
    //              Our TitleBar acts as a menu bar below the native chrome.
    readonly property bool nativeChrome: Qt.platform.os === "linux" || Qt.platform.os === "osx"

    function openDevTools() { devToolsWindow.show() }
    flags: nativeChrome ? Qt.Window : Qt.Window | Qt.FramelessWindowHint
    color: theme.surface

    // Both backdrops cover only the content area (between title bar and status bar).
    // Mutual exclusion is enforced in Python — they are never open simultaneously.
    // On Linux: no custom title bar, so content starts at y:0.

    readonly property int contentTop: Qt.platform.os === "linux" ? 0 : theme.titleBarHeight

    // Catches clicks outside an open menu popup — closes popup, menu stays open.
    // Covers from tab bar downward so clicking a tab while the dropdown is open
    // both dismisses the popup and switches the tab (propagateComposedEvents).
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

    // Catches clicks outside the plugin dropdown — closes dropdown
    MouseArea {
        x: 0; y: root.contentTop + 42
        width: parent.width
        height: parent.height - root.contentTop - 42 - 32
        z: 3
        enabled: statusBarViewModel.pluginDropdownOpen
        propagateComposedEvents: true
        onClicked: mouse => {
            statusBarViewModel.closePluginDropdown()
            mouse.accepted = false
        }
    }

    // Linux: compositor has no built-in resize for frameless windows — QML handles it.
    // Windows: WndProc (win_window.py) handles resize via HTTEST. macOS: native chrome.
    ResizeHandles { visible: Qt.platform.os === "linux" }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        TitleBar {
            Layout.fillWidth: true
            z: 1  // dropdowns render above StyledTabBar and content
        }

        StyledTabBar {
            Layout.fillWidth: true
        }

        StackLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: tabViewModel.currentIndex

            WidgetTab {}
        }

        StatusBar {
            Layout.fillWidth: true
        }
    }

    // SettingsDialog and DevToolsWindow are Windows — outside ColumnLayout
    SettingsDialog {}
    DevToolsWindow { id: devToolsWindow }

    // F12 — open Dev Tools, just like browser devtools
    // TODO: make keyboard shortcuts configurable in settings
    Shortcut {
        sequence: "F12"
        onActivated: devToolsWindow.visible ? devToolsWindow.hide() : devToolsWindow.show()
    }
}
