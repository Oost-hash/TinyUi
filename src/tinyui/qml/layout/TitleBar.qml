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
import "../components"

Rectangle {
    id: titleBar

    function _menuItems() {
        return [
            {
                label: "Show Overlay",
                sep: false,
                checkable: true,
                checked: widgetOverlayState ? widgetOverlayState.overlayVisible : false,
                action: function() {
                    if (widgetOverlayState)
                        widgetOverlayState.toggleOverlayVisible()
                }
            },
            { label: "",           sep: true,  action: null },
            { label: "Settings",   sep: false, action: function() { settingsPanelViewModel.openPanel(); menuViewModel.closeMenu() } },
            { label: "",           sep: true,  action: null },
            { label: "Dev Tools",  sep: false, action: function() { root.openDevTools(); menuViewModel.closeMenu() } },
            { label: "",           sep: true,  action: null },
            { label: "Close",      sep: false, action: function() { root.close() } }
        ]
    }

    height: theme.titleBarHeight
    color: theme.surfaceRaised

    Rectangle {
        anchors.bottom: parent.bottom
        width: parent.width
        height: 1
        color: theme.border
    }

    // Keep WndProc left zone in sync — expand to cover open dropdown so
    // the drag zone doesn't overlap the visible menu items.
    function _updateLeftZone() {
        if (typeof windowController === "undefined") return
        var zone = menuViewModel.dropdownOpen
                   ? Math.max(leftRow.width, menuDropdown.width)
                   : leftRow.width
        windowController.setLeftButtonWidth(zone)
    }

    Connections {
        target: menuViewModel
        function onDropdownOpenChanged() { titleBar._updateLeftZone() }
    }

    // Windows: drag en dubbelklik-maximize via WM_NCHITTEST → HTCAPTION (win_window.py).
    // Linux:   DragHandler start compositor-move; TapHandler handelt dubbeltik af.
    DragHandler {
        enabled: Qt.platform.os === "linux"
        target: null
        onActiveChanged: if (active) windowController.startMove()
    }
    TapHandler {
        enabled: Qt.platform.os === "linux"
        onTapped: if (tapCount === 2) windowController.toggleMaximize()
    }

    // ── Inline dropdown component: plain Item, no Popup overlay ──────────────
    // Popup captures hover from underlying items once the overlay appears.
    // An Item with z:10 renders on top without an overlay and keeps hover intact.

    component TitleDropdown: Item {
        z: 10
        y: titleBar.height

        // Background + 3-sided border (no top)
        Rectangle { anchors.fill: parent; color: theme.surfaceAlt }
        Rectangle { anchors.left: parent.left;   width: 1;  height: parent.height; color: theme.border }
        Rectangle { anchors.bottom: parent.bottom; height: 1; width: parent.width;  color: theme.border }
        Rectangle { anchors.right: parent.right;  width: 1;  height: parent.height; color: theme.border }

        Behavior on opacity {
            NumberAnimation { duration: 120; easing.type: Easing.OutCubic }
        }
    }

    // ── Delegate for menu items (shared by all dropdowns) ─────────────────────

    component MenuItemDelegate: Rectangle {
        required property var modelData
        required property int index

        width: ListView.view ? ListView.view.width : parent.width
        height: modelData.sep ? 9 : 28
        color: (!modelData.sep && rowMouse.containsMouse) ? theme.surfaceRaised : "transparent"

        Rectangle {
            visible: modelData.sep
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left; anchors.right: parent.right
            anchors.leftMargin: 8;     anchors.rightMargin: 8
            height: 1; color: theme.border
        }

        Text {
            visible: !modelData.sep
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: checkboxIndicator.visible ? checkboxIndicator.right : parent.left
            anchors.leftMargin: checkboxIndicator.visible ? 10 : 12
            text: modelData.label
            color: theme.text
            font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
        }

        Rectangle {
            id: checkboxIndicator
            visible: !modelData.sep && !!modelData.checkable
            anchors.left: parent.left
            anchors.leftMargin: 8
            anchors.verticalCenter: parent.verticalCenter
            width: 14
            height: 14
            radius: 3
            color: !!modelData.checked ? theme.accent : "transparent"
            border.width: 1
            border.color: !!modelData.checked ? theme.accent : theme.border

            Text {
                anchors.centerIn: parent
                visible: !!modelData.checked
                text: "✓"
                color: theme.accentText
                font.pixelSize: 9
                font.family: theme.fontFamily
                font.weight: Font.DemiBold
            }
        }

        MouseArea {
            id: rowMouse
            anchors.fill: parent
            hoverEnabled: true
            enabled: !modelData.sep
            onClicked: modelData.action ? modelData.action() : undefined
        }
    }

    // ── Dropdown onder hamburger+TinyUi ───────────────────────────────────────

    TitleDropdown {
        id: menuDropdown
        x: 0
        width: 160
        opacity: menuViewModel.dropdownOpen ? 1.0 : 0.0
        visible: opacity > 0

        Column {
            id: menuDropdownCol
            width: parent.width; spacing: 0

            Repeater {
                model: titleBar._menuItems()
                delegate: MenuItemDelegate {}
            }
        }
        height: menuDropdownCol.implicitHeight
    }

    // ── Links: hamburger + app naam ───────────────────────────────────────────

    Row {
        id: leftRow
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        spacing: 0

        onWidthChanged: _updateLeftZone()
        Component.onCompleted: _updateLeftZone()

        HoverHandler {
            onHoveredChanged: {
                if (hovered) menuViewModel.mouseEnteredMenu()
                else menuViewModel.mouseLeftMenu()
            }
        }

        AbstractButton {
            id: menuBtn
            height: parent.height
            implicitWidth: menuIcon.implicitWidth + menuLabel.implicitWidth + 28
            hoverEnabled: true
            onHoveredChanged: {
                if (hovered && menuViewModel.menuOpen)
                    menuViewModel.closeActivePopup()
            }
            onClicked: menuViewModel.toggleMenu()

            background: Item {
                readonly property bool active: menuViewModel.dropdownOpen

                Rectangle {
                    anchors.fill: parent
                    color: parent.active ? theme.surfaceAlt
                                        : menuBtn.hovered ? theme.surfaceFloating : "transparent"
                }
                Rectangle { visible: parent.active; anchors.left:  parent.left;  width: 1; height: parent.height; color: theme.border }
                Rectangle { visible: parent.active; anchors.right: parent.right; width: 1; height: parent.height; color: theme.border }
            }

            contentItem: Item {
                Image {
                    id: menuIcon
                    anchors.left: parent.left
                    anchors.leftMargin: 12
                    anchors.verticalCenter: parent.verticalCenter
                    width: 10
                    height: 10
                    source: menuViewModel.menuOpen
                        ? "../../assets/icons/menu-open.svg"
                        : "../../assets/icons/menu.svg"
                    sourceSize.width: width
                    sourceSize.height: height
                    fillMode: Image.PreserveAspectFit
                    smooth: true
                }
                Text {
                    id: menuLabel
                    anchors.left: menuIcon.right; anchors.leftMargin: 8
                    anchors.verticalCenter: parent.verticalCenter
                    text: appName
                    color: (menuViewModel.menuOpen || menuBtn.hovered) ? "#FFFFFF" : theme.textMuted
                    font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
                    font.weight: Font.Medium
                }
            }
        }

    }

    // ── Right: window buttons (not on Linux/macOS — native chrome provides them) ──

    Row {
        visible: !root.nativeChrome
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        spacing: 0

        TitleBarButton {
            height: parent.height
            iconSource: "../../assets/icons/window-minimize.svg"
            onClicked: windowController.minimize()
        }

        TitleBarButton {
            height: parent.height
            iconSource: root.visibility === Window.Maximized
                ? "../../assets/icons/window-restore.svg"
                : "../../assets/icons/window-maximize.svg"
            onClicked: windowController.toggleMaximize()
        }

        TitleBarButton {
            height: parent.height
            iconSource: "../../assets/icons/window-close.svg"
            isCloseButton: true
            onClicked: root.close()
        }
    }
}
