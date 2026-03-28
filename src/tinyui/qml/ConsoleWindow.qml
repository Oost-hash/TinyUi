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
import TinyUI
import TinyDevTools
import "components"

BaseDialog {
    id: consoleWin
    dialogTitle: "Console"
    width: 800
    height: 440

    onCloseRequested: consoleWin.hide()

    // ── Level filter state ────────────────────────────────────────────────────
    property bool showDebug:   true
    property bool showInfo:    true
    property bool showWarning: true
    property bool showError:   true

    function _levelVisible(level) {
        if (level === "DEBUG")    return showDebug
        if (level === "INFO")     return showInfo
        if (level === "WARNING")  return showWarning
        return showError  // ERROR / CRITICAL
    }

    function _levelColor(level) {
        if (level === "DEBUG")    return Theme.textMuted
        if (level === "INFO")     return Theme.text
        if (level === "WARNING")  return Theme.warning
        return Theme.danger  // ERROR / CRITICAL
    }

    // ── Log model ─────────────────────────────────────────────────────────────
    ListModel { id: logModel }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // ── Toolbar ───────────────────────────────────────────────────────────
        Rectangle {
            Layout.fillWidth: true
            implicitHeight: 36
            color: Theme.surfaceAlt

            Rectangle {
                anchors.bottom: parent.bottom
                width: parent.width; height: 1
                color: Theme.border
            }

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 8
                anchors.rightMargin: 8

                // ── Level filter chips ─────────────────────────────────────
                Row {
                    spacing: 4

                    Repeater {
                        model: ["DEBUG", "INFO", "WARN", "ERROR"]

                        delegate: Rectangle {
                            required property string modelData

                            property bool   active:   {
                                if (modelData === "DEBUG") return consoleWin.showDebug
                                if (modelData === "INFO")  return consoleWin.showInfo
                                if (modelData === "WARN")  return consoleWin.showWarning
                                return consoleWin.showError
                            }
                            property color  levelCol: {
                                if (modelData === "DEBUG") return Theme.textMuted
                                if (modelData === "INFO")  return Theme.text
                                if (modelData === "WARN")  return Theme.warning
                                return Theme.danger
                            }

                            width: 52; height: 22
                            radius: 3
                            color:        active ? Qt.rgba(levelCol.r, levelCol.g, levelCol.b, 0.15) : "transparent"
                            border.color: active ? levelCol : Theme.border
                            border.width: 1

                            Text {
                                anchors.centerIn: parent
                                text: modelData
                                color: active ? levelCol : Theme.textMuted
                                font.pixelSize: Theme.fontSizeSmall
                                font.family: "Consolas, Courier New, monospace"
                                font.weight: Font.DemiBold
                            }

                            MouseArea {
                                anchors.fill: parent
                                onClicked: {
                                    if (modelData === "DEBUG") consoleWin.showDebug   = !consoleWin.showDebug
                                    if (modelData === "INFO")  consoleWin.showInfo    = !consoleWin.showInfo
                                    if (modelData === "WARN")  consoleWin.showWarning = !consoleWin.showWarning
                                    if (modelData === "ERROR") consoleWin.showError   = !consoleWin.showError
                                }
                            }
                        }
                    }
                }

                Item { Layout.fillWidth: true }

                // ── Auto-scroll toggle ─────────────────────────────────────
                Rectangle {
                    implicitWidth: 100; implicitHeight: 22
                    radius: 3
                    color: autoScrollMouse.containsMouse ? Theme.surfaceRaised : "transparent"

                    Text {
                        anchors.centerIn: parent
                        text: scrollToggle.checked ? "Auto-scroll ON" : "Auto-scroll OFF"
                        color: scrollToggle.checked ? Theme.accent : Theme.textMuted
                        font.pixelSize: Theme.fontSizeSmall
                        font.family: "Consolas, Courier New, monospace"
                    }
                    MouseArea {
                        id: autoScrollMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: scrollToggle.checked = !scrollToggle.checked
                    }
                    CheckBox { id: scrollToggle; checked: true; visible: false }
                }

                // ── Clear button ───────────────────────────────────────────
                Rectangle {
                    implicitWidth: 48; implicitHeight: 22
                    radius: 3
                    color: clearMouse.containsMouse ? Theme.surfaceRaised : "transparent"

                    Text {
                        anchors.centerIn: parent
                        text: "Clear"
                        color: Theme.textMuted
                        font.pixelSize: Theme.fontSizeSmall
                        font.family: "Consolas, Courier New, monospace"
                    }
                    MouseArea {
                        id: clearMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: { logModel.clear(); LogViewModel.clear() }
                    }
                }
            }
        }

        // ── Log list ──────────────────────────────────────────────────────────
        ListView {
            id: logList
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: logModel
            spacing: 0
            ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

            delegate: Item {
                width: logList.width
                visible: consoleWin._levelVisible(model.level)
                height: visible ? row.implicitHeight + 2 : 0

                RowLayout {
                    id: row
                    anchors { left: parent.left; right: parent.right; leftMargin: 8; rightMargin: 8 }
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 0

                    // Timestamp
                    Text {
                        text: model.time
                        color: Theme.textMuted
                        font.pixelSize: 11
                        font.family: "Consolas, Courier New, monospace"
                        rightPadding: 8
                    }

                    // Level badge
                    Rectangle {
                        implicitWidth: 52; implicitHeight: 16
                        radius: 2
                        color: Qt.rgba(
                            Qt.darker(consoleWin._levelColor(model.level), 1.0).r,
                            Qt.darker(consoleWin._levelColor(model.level), 1.0).g,
                            Qt.darker(consoleWin._levelColor(model.level), 1.0).b, 0.15)
                        Layout.rightMargin: 8

                        Text {
                            anchors.centerIn: parent
                            text: model.level === "CRITICAL" ? "CRIT" : model.level
                            color: consoleWin._levelColor(model.level)
                            font.pixelSize: 10
                            font.family: "Consolas, Courier New, monospace"
                            font.weight: Font.Bold
                        }
                    }

                    // Logger name
                    Text {
                        text: model.name
                        color: Theme.textSecondary
                        font.pixelSize: 11
                        font.family: "Consolas, Courier New, monospace"
                        leftPadding: 6
                        rightPadding: 8
                        elide: Text.ElideRight
                        Layout.preferredWidth: 200
                    }

                    // Message
                    Text {
                        text: model.message
                        color: consoleWin._levelColor(model.level)
                        font.pixelSize: 11
                        font.family: "Consolas, Courier New, monospace"
                        Layout.fillWidth: true
                        wrapMode: Text.NoWrap
                        elide: Text.ElideRight
                    }
                }
            }

            onCountChanged: {
                if (scrollToggle.checked)
                    logList.positionViewAtEnd()
            }
        }
    }

    // ── Receive new log records ───────────────────────────────────────────────
    Connections {
        target: LogViewModel

        function onRecordAdded(time, level, name, message) {
            logModel.append({ time, level, name, message })
        }

        function onCleared() { logModel.clear() }
    }
}
