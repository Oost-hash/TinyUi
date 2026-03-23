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

    // Dialog content — children of the instance end up here
    default property alias content: contentArea.data

    // Consumers connect this signal to handle close.
    // No handler by default — consumer decides (e.g. closePanel() on ViewModel).
    signal closeRequested()

    // ── Platform chrome ───────────────────────────────────────────────────────
    readonly property bool nativeChrome: Qt.platform.os === "linux" || Qt.platform.os === "osx"
    flags: Qt.Window | Qt.FramelessWindowHint
    transientParent: null   // own taskbar entry, not bound to main window
    color: theme.surface

    // Win32 DWM chrome: shadow, rounded corners, Alt+Tab thumbnail.
    // applyToWindow() retrieves winId() via the Python QWindow API — winId() is not
    // available as a QML method. WindowChromeHelper is idempotent.
    onVisibleChanged: {
        if (visible && Qt.platform.os === "windows" && typeof windowChromeHelper !== "undefined")
            windowChromeHelper.applyToWindow(baseDialog)
    }

    // ── Focus-clearer ─────────────────────────────────────────────────────────
    // Click anywhere outside the active input — clear focus so the cursor disappears.
    // Checks whether the click falls OUTSIDE the focused item — if the user clicks
    // the TextInput itself, focus remains and editing continues.
    MouseArea {
        anchors.fill: parent
        z: 999
        propagateComposedEvents: true
        hoverEnabled: false
        onPressed: (mouse) => {
            var focusItem = baseDialog.activeFocusItem
            // contentItem (QQuickRootItem) always has focus as fallback — skip it
            var isRealInput = focusItem && focusItem !== baseDialog.contentItem
            if (isRealInput) {
                // mapFromItem(null, x, y) translates from scene coordinates
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
