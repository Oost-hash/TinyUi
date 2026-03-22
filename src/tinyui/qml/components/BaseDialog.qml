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

Window {
    id: baseDialog

    // ── API ───────────────────────────────────────────────────────────────────
    property string dialogTitle: ""

    // Inhoud van de dialog — kinderen van de instantie komen hier terecht
    default property alias content: contentArea.data

    // Consumers verbinden dit signaal om close te afhandelen.
    // Standaard geen handler — consumer beslist (bijv. closePanel() op ViewModel).
    signal closeRequested()

    // ── Platform chrome ───────────────────────────────────────────────────────
    readonly property bool nativeChrome: Qt.platform.os === "linux" || Qt.platform.os === "osx"
    flags: Qt.Window | Qt.FramelessWindowHint
    transientParent: null   // eigen taskbar-entry, niet gebonden aan hoofdvenster
    color: theme.surface

    // Win32 DWM chrome: shadow, rounded corners, Alt+Tab thumbnail.
    // applyToWindow() haalt winId() op via de Python QWindow API — winId() is niet
    // beschikbaar als QML-methode. WindowChromeHelper is idempotent.
    onVisibleChanged: {
        if (visible && Qt.platform.os === "windows" && typeof windowChromeHelper !== "undefined")
            windowChromeHelper.applyToWindow(baseDialog)
    }

    // ── Focus-clearer ─────────────────────────────────────────────────────────
    // Klik ergens buiten het actieve invoerveld → focus wegnemen zodat de cursor verdwijnt.
    // Controleert of de klik BUITEN het gefocuste item valt — als de gebruiker op het
    // TextInput zelf klikt blijft de focus intact en gaat editing door.
    MouseArea {
        anchors.fill: parent
        z: 999
        propagateComposedEvents: true
        hoverEnabled: false
        onPressed: (mouse) => {
            var focusItem = baseDialog.activeFocusItem
            // contentItem (QQuickRootItem) heeft altijd "focus" als fallback — overslaan
            var isRealInput = focusItem && focusItem !== baseDialog.contentItem
            if (isRealInput) {
                // mapFromItem(null, x, y) vertaalt vanuit scene-coördinaten
                var local = focusItem.mapFromItem(null, mouse.x, mouse.y)
                var outside = local.x < 0 || local.x > focusItem.width
                           || local.y < 0 || local.y > focusItem.height
if (outside)
                    focusItem.focus = false
            }
            mouse.accepted = false
        }
    }

    // ── Layout ────────────────────────────────────────────────────────────────
    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        DialogTitleBar {
            Layout.fillWidth: true
            visible: !baseDialog.nativeChrome
            title: baseDialog.dialogTitle
            onCloseClicked: baseDialog.closeRequested()
        }

        Item {
            id: contentArea
            Layout.fillWidth: true
            Layout.fillHeight: true
        }
    }
}
