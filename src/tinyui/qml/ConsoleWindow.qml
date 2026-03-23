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

// TinyUI — Console window: shows live Python log output.

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Window {
    id: consoleWin
    title: "Console — TinyUI"
    width: 720
    height: 400
    flags: Qt.Tool | Qt.WindowTitleHint | Qt.WindowSystemMenuHint
           | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint

    color: "#1a1a1a"

    // ── Toolbar ───────────────────────────────────────────────────────────────
    Rectangle {
        id: toolbar
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 32
        color: "#242424"

        Rectangle {
            anchors.bottom: parent.bottom
            width: parent.width; height: 1
            color: "#383838"
        }

        Row {
            anchors.verticalCenter: parent.verticalCenter
            anchors.right: parent.right
            anchors.rightMargin: 8
            spacing: 6

            // Auto-scroll toggle
            Rectangle {
                width: 80; height: 20
                radius: 3
                color: autoScrollBtn.containsMouse ? "#383838" : "transparent"

                Text {
                    anchors.centerIn: parent
                    text: scrollToggle.checked ? "Auto-scroll ON" : "Auto-scroll OFF"
                    color: scrollToggle.checked ? "#7ec8a0" : "#888888"
                    font.pixelSize: 11
                    font.family: "Consolas, monospace"
                }
                CheckBox {
                    id: scrollToggle
                    anchors.fill: parent
                    opacity: 0
                    checked: true
                }
                MouseArea {
                    id: autoScrollBtn
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: scrollToggle.checked = !scrollToggle.checked
                }
            }

            // Clear button
            Rectangle {
                width: 48; height: 20
                radius: 3
                color: clearMouse.containsMouse ? "#383838" : "transparent"

                Text {
                    anchors.centerIn: parent
                    text: "Clear"
                    color: "#888888"
                    font.pixelSize: 11
                    font.family: "Consolas, monospace"
                }
                MouseArea {
                    id: clearMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: logViewModel.clear()
                }
            }
        }
    }

    // ── Log area ──────────────────────────────────────────────────────────────
    ScrollView {
        id: scroll
        anchors.top: toolbar.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 0
        clip: true
        ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
        ScrollBar.vertical.policy: ScrollBar.AsNeeded

        TextArea {
            id: logArea
            readOnly: true
            wrapMode: TextArea.NoWrap
            background: null
            color: "#cccccc"
            font.family: "Consolas, Courier New, monospace"
            font.pixelSize: 12
            leftPadding: 8; rightPadding: 8
            topPadding: 4;  bottomPadding: 4
            selectByMouse: true
        }
    }

    // ── Receive new log lines ─────────────────────────────────────────────────
    Connections {
        target: logViewModel

        function onLineAdded(line) {
            // Colour lines by level
            var col = "#cccccc"
            if (line.indexOf("ERROR") !== -1 || line.indexOf("CRITICAL") !== -1)
                col = "#e06c6c"
            else if (line.indexOf("WARNING") !== -1)
                col = "#e0c46c"
            else if (line.indexOf("DEBUG") !== -1)
                col = "#888888"

            logArea.append("<span style='color:" + col + "'>"
                + line.replace(/&/g, "&amp;").replace(/</g, "&lt;") + "</span>")

            if (scrollToggle.checked)
                scroll.ScrollBar.vertical.position = 1.0 - scroll.ScrollBar.vertical.size
        }

        function onCleared() {
            logArea.clear()
        }
    }
}
