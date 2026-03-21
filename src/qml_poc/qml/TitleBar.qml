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

Rectangle {
    id: titleBar

    height: theme.titleBarHeight
    color: theme.surfaceRaised

    property bool menuOpen: false
    property var activeMenuPopup: null

    function openMenuPopup(popup) {
        if (activeMenuPopup && activeMenuPopup !== popup)
            activeMenuPopup.close()
        menuDropdown.close()
        activeMenuPopup = popup
        popup.open()
        closeTimer.stop()
    }

    function closeMenuPopup() {
        if (activeMenuPopup) {
            activeMenuPopup.close()
            activeMenuPopup = null
        }
    }

    onMenuOpenChanged: {
        if (menuOpen) menuDropdown.open()
        else { menuDropdown.close(); closeMenuPopup() }
    }

    // Drag en dubbelklik-maximize worden afgehandeld door Windows via
    // WM_NCHITTEST → HTCAPTION (zie win32_window.py).
    // Alleen de knoppen-zones retourneren HTCLIENT zodat QML ze afhandelt.

    // Auto-close: sluit menu 5 seconden nadat muis de zone verlaat
    // Vuurt niet als er een popup open staat — popup-interactie reset de timer
    Timer {
        id: closeTimer
        interval: 5000
        onTriggered: {
            if (!titleBar.activeMenuPopup || !titleBar.activeMenuPopup.visible)
                titleBar.menuOpen = false
        }
    }

    // ── Delegate component voor menu-items (gedeeld door alle popups) ─────────

    component MenuItemDelegate: Rectangle {
        required property var modelData
        required property int index

        width: ListView.view ? ListView.view.width : parent.width
        height: modelData.sep ? 9 : 28
        color: (!modelData.sep && rowMouse.containsMouse) ? theme.surfaceRaised : "transparent"

        Rectangle {
            visible: modelData.sep
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.leftMargin: 8
            anchors.rightMargin: 8
            height: 1
            color: theme.border
        }

        Row {
            visible: !modelData.sep
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left
            anchors.leftMargin: 8
            spacing: 6

            Text {
                anchors.verticalCenter: parent.verticalCenter
                text: modelData.icon
                font.family: "Segoe Fluent Icons"
                font.pixelSize: 12
                color: theme.textMuted
            }
            Text {
                anchors.verticalCenter: parent.verticalCenter
                text: modelData.label
                color: theme.text
                font.pixelSize: theme.fontSizeSmall
                font.family: theme.fontFamily
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

    // ── Dropdown onder hamburger+TinyUi (opent mee met menu) ─────────────────

    MenuPopup {
        id: menuDropdown
        parent: titleBar
        x: 0
        y: titleBar.height
        width: 160

        onClosed: {
            if (titleBar.menuOpen && !titleBar.activeMenuPopup)
                closeTimer.restart()
        }

        contentItem: Column {
            spacing: 0

            Repeater {
                model: [
                    { icon: "\uE713", label: "Settings", sep: false, action: function() { tabViewModel.setCurrentIndex(1); titleBar.menuOpen = false } },
                    { icon: "",       label: "",         sep: true,  action: null },
                    { icon: "\uE8BB", label: "Sluiten",  sep: false, action: function() { root.close() } }
                ]

                delegate: MenuItemDelegate {}
            }
        }
    }

    // ── Popups (directe kinderen van titleBar voor correcte y-positie) ─────

    MenuPopup {
        id: helpPopup
        parent: titleBar
        x: menuItemsRow.x + helpBtn.x
        y: titleBar.height
        width: 200

        onClosed: {
            if (titleBar.activeMenuPopup === helpPopup)
                titleBar.activeMenuPopup = null
            if (titleBar.menuOpen && !titleBar.activeMenuPopup)
                closeTimer.restart()
        }

        contentItem: Column {
            spacing: 0

            Repeater {
                model: [
                    { icon: "\uE8A5", label: "Snelstartgids",  sep: false, action: function() { helpPopup.close() } },
                    { icon: "\uE897", label: "Documentatie",    sep: false, action: function() { helpPopup.close() } },
                    { icon: "\uE76E", label: "Sneltoetsen",     sep: false, action: function() { helpPopup.close() } },
                    { icon: "",       label: "",                sep: true,  action: null },
                    { icon: "\uE730", label: "Rapporteer bug",  sep: false, action: function() { helpPopup.close() } },
                    { icon: "\uE8F4", label: "Feedback geven",  sep: false, action: function() { helpPopup.close() } },
                    { icon: "\uE716", label: "Community",       sep: false, action: function() { helpPopup.close() } }
                ]

                delegate: MenuItemDelegate {}
            }
        }
    }

    MenuPopup {
        id: aboutPopup
        parent: titleBar
        x: menuItemsRow.x + aboutBtn.x
        y: titleBar.height
        width: 200

        onClosed: {
            if (titleBar.activeMenuPopup === aboutPopup)
                titleBar.activeMenuPopup = null
            if (titleBar.menuOpen && !titleBar.activeMenuPopup)
                closeTimer.restart()
        }

        contentItem: Column {
            spacing: 0

            Rectangle {
                width: aboutPopup.width
                height: 40
                color: "transparent"

                Column {
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.left: parent.left
                    anchors.leftMargin: 12
                    spacing: 2

                    Text {
                        text: appName
                        color: theme.text
                        font.pixelSize: theme.fontSizeSmall
                        font.family: theme.fontFamily
                        font.weight: Font.DemiBold
                    }
                    Text {
                        text: "v0.1.0"
                        color: theme.textMuted
                        font.pixelSize: theme.fontSizeSmall - 1
                        font.family: theme.fontFamily
                    }
                }
            }

            Rectangle {
                width: aboutPopup.width
                height: 1
                color: theme.border
            }

            Repeater {
                model: [
                    { icon: "\uE787", label: "Nieuwste updates", sep: false, action: function() { aboutPopup.close() } },
                    { icon: "\uE8A5", label: "Release notes",    sep: false, action: function() { aboutPopup.close() } },
                    { icon: "",       label: "",                 sep: true,  action: null },
                    { icon: "\uE946", label: "Licentie",         sep: false, action: function() { aboutPopup.close() } },
                    { icon: "\uE716", label: "Bijdragers",       sep: false, action: function() { aboutPopup.close() } },
                    { icon: "\uE8B6", label: "Privacy",          sep: false, action: function() { aboutPopup.close() } }
                ]

                delegate: MenuItemDelegate {}
            }
        }
    }

    // ── Links: hamburger + app naam + menu items ───────────────────────────

    Row {
        id: leftRow
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        spacing: 0

        // Informeer Win32 hit-testing live over de actuele breedte van de linker zone
        onWidthChanged: {
            if (typeof windowController !== "undefined")
                windowController.setLeftButtonWidth(width)
        }

        HoverHandler {
            onHoveredChanged: {
                if (hovered) {
                    closeTimer.stop()
                } else if (titleBar.menuOpen) {
                    // Geen timer als er een popup open staat — muis is dan over de popup
                    if (!titleBar.activeMenuPopup || !titleBar.activeMenuPopup.visible)
                        closeTimer.restart()
                }
            }
        }

        // Hamburger + app naam als één gecombineerde knop
        AbstractButton {
            id: menuBtn
            height: parent.height
            implicitWidth: menuIcon.implicitWidth + menuLabel.implicitWidth + 28
            hoverEnabled: true
            onHoveredChanged: {
                if (hovered && titleBar.menuOpen) {
                    titleBar.closeMenuPopup()
                    menuDropdown.open()
                    closeTimer.stop()
                }
            }
            onClicked: {
                titleBar.menuOpen = !titleBar.menuOpen
                closeTimer.stop()
            }

            background: Rectangle {
                color: menuBtn.hovered ? theme.surfaceFloating : "transparent"
            }

            contentItem: Item {
                Text {
                    id: menuIcon
                    anchors.left: parent.left
                    anchors.leftMargin: 12
                    anchors.verticalCenter: parent.verticalCenter
                    text: titleBar.menuOpen ? "\uE711" : "\uE700"
                    font.family: "Segoe Fluent Icons"
                    font.pixelSize: 10
                    color: "#FFFFFF"
                }

                Text {
                    id: menuLabel
                    anchors.left: menuIcon.right
                    anchors.leftMargin: 8
                    anchors.verticalCenter: parent.verticalCenter
                    text: appName
                    color: (titleBar.menuOpen || menuBtn.hovered) ? "#FFFFFF" : theme.textMuted
                    font.pixelSize: theme.fontSizeSmall
                    font.family: theme.fontFamily
                    font.weight: Font.Medium
                }
            }
        }

        Row {
            id: menuItemsRow
            height: parent.height
            spacing: 0
            opacity: titleBar.menuOpen ? 1.0 : 0.0
            visible: opacity > 0

            Behavior on opacity {
                NumberAnimation { duration: 180; easing.type: Easing.OutCubic }
            }

            MenuTextButton {
                id: helpBtn
                label: "Help"
                onHoveredChanged: if (hovered) titleBar.openMenuPopup(helpPopup)
                onClicked: helpPopup.visible ? titleBar.closeMenuPopup() : titleBar.openMenuPopup(helpPopup)
            }

            MenuTextButton {
                id: aboutBtn
                label: "About"
                onHoveredChanged: if (hovered) titleBar.openMenuPopup(aboutPopup)
                onClicked: aboutPopup.visible ? titleBar.closeMenuPopup() : titleBar.openMenuPopup(aboutPopup)
            }
        }
    }

    // ── Rechts: venster knoppen ───────────────────────────────────────────

    Row {
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        spacing: 0

        TitleBarButton {
            height: parent.height
            iconText: "\uE921"
            onClicked: windowController.minimize()
        }

        TitleBarButton {
            height: parent.height
            iconText: root.visibility === Window.Maximized ? "\uE923" : "\uE922"
            onClicked: windowController.toggleMaximize()
        }

        TitleBarButton {
            height: parent.height
            iconText: "\uE8BB"
            isCloseButton: true
            onClicked: root.close()
        }
    }
}
