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

    height: theme.titleBarHeight
    color: theme.surfaceRaised

    Rectangle {
        anchors.bottom: parent.bottom
        width: parent.width
        height: 1
        color: theme.border
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

    // ── Inline dropdown-component: gewone Item, geen Popup-overlay ────────────
    // Popup steelt hover van onderliggende items zodra de overlay verschijnt.
    // Een Item met z:10 rendert bovenop zonder overlay en laat hover intact.

    component TitleDropdown: Item {
        z: 10
        y: titleBar.height

        // Achtergrond + 3-zijdige border (geen bovenkant)
        Rectangle { anchors.fill: parent; color: theme.surfaceAlt }
        Rectangle { anchors.left: parent.left;   width: 1;  height: parent.height; color: theme.border }
        Rectangle { anchors.bottom: parent.bottom; height: 1; width: parent.width;  color: theme.border }
        Rectangle { anchors.right: parent.right;  width: 1;  height: parent.height; color: theme.border }

        Behavior on opacity {
            NumberAnimation { duration: 120; easing.type: Easing.OutCubic }
        }
    }

    // ── Delegate voor menu-items (gedeeld door alle dropdowns) ────────────────

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

        Row {
            visible: !modelData.sep
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left; anchors.leftMargin: 8
            spacing: 6

            Text {
                anchors.verticalCenter: parent.verticalCenter
                text: modelData.icon
                font.family: theme.iconFont; font.pixelSize: 12
                color: theme.textMuted
            }
            Text {
                anchors.verticalCenter: parent.verticalCenter
                text: modelData.label
                color: theme.text
                font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
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
                model: [
                    { icon: icons.settingsAlt, label: "Settings", sep: false, action: function() { tabViewModel.setCurrentIndex(1); menuViewModel.closeMenu() } },
                    { icon: "",                label: "",          sep: true,  action: null },
                    { icon: icons.close,       label: "Sluiten",   sep: false, action: function() { root.close() } }
                ]
                delegate: MenuItemDelegate {}
            }
        }
        height: menuDropdownCol.implicitHeight
    }

    // ── Help dropdown ─────────────────────────────────────────────────────────

    TitleDropdown {
        id: helpDropdown
        x: menuItemsRow.x + helpBtn.x
        width: 200
        opacity: menuViewModel.activePopup === "help" ? 1.0 : 0.0
        visible: opacity > 0

        Column {
            id: helpCol
            width: parent.width; spacing: 0

            Repeater {
                model: [
                    { icon: icons.document,  label: "Snelstartgids",  sep: false, action: function() { menuViewModel.closeMenu() } },
                    { icon: icons.book,      label: "Documentatie",    sep: false, action: function() { menuViewModel.closeMenu() } },
                    { icon: icons.keyboard,  label: "Sneltoetsen",     sep: false, action: function() { menuViewModel.closeMenu() } },
                    { icon: "",              label: "",                sep: true,  action: null },
                    { icon: icons.bugReport, label: "Rapporteer bug",  sep: false, action: function() { menuViewModel.closeMenu() } },
                    { icon: icons.feedback,  label: "Feedback geven",  sep: false, action: function() { menuViewModel.closeMenu() } },
                    { icon: icons.group,     label: "Community",       sep: false, action: function() { menuViewModel.closeMenu() } }
                ]
                delegate: MenuItemDelegate {}
            }
        }
        height: helpCol.implicitHeight
    }

    // ── About dropdown ────────────────────────────────────────────────────────

    TitleDropdown {
        id: aboutDropdown
        x: menuItemsRow.x + aboutBtn.x
        width: 200
        opacity: menuViewModel.activePopup === "about" ? 1.0 : 0.0
        visible: opacity > 0

        Column {
            id: aboutCol
            width: parent.width; spacing: 0

            // App-header
            Rectangle {
                width: parent.width; height: 40; color: "transparent"

                Column {
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.left: parent.left; anchors.leftMargin: 12
                    spacing: 2

                    Text {
                        text: appName
                        color: theme.text
                        font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
                        font.weight: Font.DemiBold
                    }
                    Text {
                        text: "v0.1.0"
                        color: theme.textMuted
                        font.pixelSize: theme.fontSizeSmall - 1; font.family: theme.fontFamily
                    }
                }
            }

            Rectangle { width: parent.width; height: 1; color: theme.border }

            Repeater {
                model: [
                    { icon: icons.updates,  label: "Nieuwste updates", sep: false, action: function() { menuViewModel.closeMenu() } },
                    { icon: icons.document, label: "Release notes",    sep: false, action: function() { menuViewModel.closeMenu() } },
                    { icon: "",             label: "",                 sep: true,  action: null },
                    { icon: icons.license,  label: "Licentie",         sep: false, action: function() { menuViewModel.closeMenu() } },
                    { icon: icons.group,    label: "Bijdragers",       sep: false, action: function() { menuViewModel.closeMenu() } },
                    { icon: icons.privacy,  label: "Privacy",          sep: false, action: function() { menuViewModel.closeMenu() } }
                ]
                delegate: MenuItemDelegate {}
            }
        }
        height: aboutCol.implicitHeight
    }

    // ── Links: hamburger + app naam + menu items ──────────────────────────────

    Row {
        id: leftRow
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        spacing: 0

        onWidthChanged: {
            if (typeof windowController !== "undefined")
                windowController.setLeftButtonWidth(width)
        }

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
                Text {
                    id: menuIcon
                    anchors.left: parent.left; anchors.leftMargin: 12
                    anchors.verticalCenter: parent.verticalCenter
                    text: menuViewModel.menuOpen ? icons.menuOpen : icons.menu
                    font.family: theme.iconFont; font.pixelSize: 10
                    color: "#FFFFFF"
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

        Row {
            id: menuItemsRow
            height: parent.height
            spacing: 0
            opacity: menuViewModel.menuOpen ? 1.0 : 0.0
            visible: opacity > 0

            Behavior on opacity {
                NumberAnimation { duration: 180; easing.type: Easing.OutCubic }
            }

            MenuTextButton {
                id: helpBtn
                label: "Help"
                popupKey: "help"
            }

            MenuTextButton {
                id: aboutBtn
                label: "About"
                popupKey: "about"
            }
        }
    }

    // ── Rechts: venster knoppen (niet op Linux/macOS — native chrome levert die) ──

    Row {
        visible: !root.nativeChrome
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        spacing: 0

        TitleBarButton {
            height: parent.height
            iconText: icons.minimize
            onClicked: windowController.minimize()
        }

        TitleBarButton {
            height: parent.height
            iconText: root.visibility === Window.Maximized ? icons.restore : icons.maximize
            onClicked: windowController.toggleMaximize()
        }

        TitleBarButton {
            height: parent.height
            iconText: icons.close
            isCloseButton: true
            onClicked: root.close()
        }
    }
}
