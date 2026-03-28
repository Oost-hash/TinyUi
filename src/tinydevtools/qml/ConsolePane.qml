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

pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import TinyUI
import TinyDevTools

Item {
    id: root

    // ── Level filter state ────────────────────────────────────────────────────
    property bool showDebug:   true
    property bool showInfo:    true
    property bool showWarning: true
    property bool showError:   true

    function levelVisible(level) {
        if (level === "DEBUG")   return root.showDebug
        if (level === "INFO")    return root.showInfo
        if (level === "WARNING") return root.showWarning
        return root.showError
    }

    function levelColor(level) {
        if (level === "DEBUG")   return Theme.textMuted
        if (level === "INFO")    return Theme.text
        if (level === "WARNING") return Theme.warning
        return Theme.danger
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
                anchors.leftMargin: 8; anchors.rightMargin: 8

                Row {
                    spacing: 4
                    Repeater {
                        model: ["DEBUG", "INFO", "WARN", "ERROR"]
                        delegate: Rectangle {
                            id: chip
                            required property string modelData
                            required property int    index

                            property bool active: {
                                if (chip.modelData === "DEBUG") return root.showDebug
                                if (chip.modelData === "INFO")  return root.showInfo
                                if (chip.modelData === "WARN")  return root.showWarning
                                return root.showError
                            }
                            property color levelCol: {
                                if (chip.modelData === "DEBUG") return Theme.textMuted
                                if (chip.modelData === "INFO")  return Theme.text
                                if (chip.modelData === "WARN")  return Theme.warning
                                return Theme.danger
                            }
                            width: 52; height: 22; radius: 3
                            color:        chip.active ? Qt.rgba(chip.levelCol.r, chip.levelCol.g, chip.levelCol.b, 0.15) : "transparent"
                            border.color: chip.active ? chip.levelCol : Theme.border
                            border.width: 1

                            Text {
                                anchors.centerIn: parent
                                text: chip.modelData
                                color: chip.active ? chip.levelCol : Theme.textMuted
                                font.pixelSize: Theme.fontSizeSmall
                                font.family: "Consolas, Courier New, monospace"
                                font.weight: Font.DemiBold
                            }
                            MouseArea {
                                anchors.fill: parent
                                onClicked: {
                                    if (chip.modelData === "DEBUG") root.showDebug   = !root.showDebug
                                    if (chip.modelData === "INFO")  root.showInfo    = !root.showInfo
                                    if (chip.modelData === "WARN")  root.showWarning = !root.showWarning
                                    if (chip.modelData === "ERROR") root.showError   = !root.showError
                                }
                            }
                        }
                    }
                }

                Item { Layout.fillWidth: true }

                Rectangle {
                    implicitWidth: 100; implicitHeight: 22; radius: 3
                    color: autoScrollMouse.containsMouse ? Theme.surfaceRaised : "transparent"
                    Text {
                        anchors.centerIn: parent
                        text: scrollToggle.checked ? "Auto-scroll ON" : "Auto-scroll OFF"
                        color: scrollToggle.checked ? Theme.accent : Theme.textMuted
                        font.pixelSize: Theme.fontSizeSmall
                        font.family: "Consolas, Courier New, monospace"
                    }
                    MouseArea {
                        id: autoScrollMouse; anchors.fill: parent; hoverEnabled: true
                        onClicked: scrollToggle.checked = !scrollToggle.checked
                    }
                    CheckBox { id: scrollToggle; checked: true; visible: false }
                }

                Rectangle {
                    implicitWidth: 48; implicitHeight: 22; radius: 3
                    color: clearMouse.containsMouse ? Theme.surfaceRaised : "transparent"
                    Text {
                        anchors.centerIn: parent; text: "Clear"
                        color: Theme.textMuted
                        font.pixelSize: Theme.fontSizeSmall
                        font.family: "Consolas, Courier New, monospace"
                    }
                    MouseArea {
                        id: clearMouse; anchors.fill: parent; hoverEnabled: true
                        onClicked: { logModel.clear(); LogViewModel.clear() }
                    }
                }
            }
        }

        // ── Category filter bar — dev mode toggle + per-category chips ────────
        Rectangle {
            Layout.fillWidth: true
            implicitHeight: 30
            color: Theme.surface

            Rectangle {
                anchors.bottom: parent.bottom
                width: parent.width; height: 1
                color: Theme.border
            }

            Flickable {
                anchors.fill: parent
                contentWidth: catChips.implicitWidth + 16
                contentHeight: height
                clip: true
                flickableDirection: Flickable.HorizontalFlick
                ScrollBar.horizontal: ScrollBar { policy: ScrollBar.AsNeeded; height: 4 }

                Row {
                    id: catChips
                    x: 8
                    height: parent.height
                    spacing: 4

                    // ── All-categories master toggle ──────────────────────────
                    Rectangle {
                        anchors.verticalCenter: parent.verticalCenter
                        width: 44; height: 20; radius: 3
                        readonly property bool on: LogSettingsViewModel
                                                   ? LogSettingsViewModel.allCategoriesEnabled : false
                        color:        on ? Theme.withAlpha(Theme.accent, 0.18)
                                         : "transparent"
                        border.color: on ? Theme.accent : Theme.border
                        border.width: 1

                        Text {
                            anchors.centerIn: parent
                            text: "ALL"
                            color: parent.on ? Theme.accent : Theme.textMuted
                            font.pixelSize: 10
                            font.family: "Consolas, Courier New, monospace"
                            font.weight: Font.Bold
                        }
                        MouseArea {
                            anchors.fill: parent
                            onClicked: {
                                if (LogSettingsViewModel)
                                    LogSettingsViewModel.setDevMode(!LogSettingsViewModel.allCategoriesEnabled)
                            }
                        }
                    }

                    // Divider
                    Rectangle {
                        anchors.verticalCenter: parent.verticalCenter
                        width: 1; height: 14
                        color: Theme.border
                    }

                    // ── Per-category chips ────────────────────────────────────
                    Repeater {
                        model: LogSettingsViewModel ? LogSettingsViewModel.categories : []

                        delegate: Rectangle {
                            id: catChip
                            required property var modelData
                            anchors.verticalCenter: parent.verticalCenter
                            implicitWidth: catLabel.implicitWidth + 12
                            height: 20; radius: 3

                            readonly property bool catOn: catChip.modelData.enabled

                            color:        catChip.catOn ? Theme.withAlpha(Theme.accent, 0.12)
                                                        : "transparent"
                            border.color: catChip.catOn ? Theme.accent : Theme.border
                            border.width: 1

                            Text {
                                id: catLabel
                                anchors.centerIn: parent
                                text: catChip.modelData.name
                                color: catChip.catOn ? Theme.accent : Theme.textMuted
                                font.pixelSize: 10
                                font.family: "Consolas, Courier New, monospace"
                            }
                            MouseArea {
                                anchors.fill: parent
                                onClicked: {
                                    if (LogSettingsViewModel)
                                        LogSettingsViewModel.setCategoryEnabled(
                                            catChip.modelData.name, !catChip.modelData.enabled)
                                }
                            }
                        }
                    }
                }
            }
        }

        // ── Log list ──────────────────────────────────────────────────────────
        ListView {
            id: logList
            Layout.fillWidth: true; Layout.fillHeight: true
            clip: true; model: logModel; spacing: 0
            ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

            delegate: Item {
                id: logRow
                required property string level
                required property string time
                required property string name
                required property string message

                width: logList.width
                visible: root.levelVisible(logRow.level)
                height: visible ? row.implicitHeight + 2 : 0

                RowLayout {
                    id: row
                    anchors { left: parent.left; right: parent.right; leftMargin: 8; rightMargin: 8 }
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 0

                    Text {
                        text: logRow.time; color: Theme.textMuted
                        font.pixelSize: 11; font.family: "Consolas, Courier New, monospace"
                        rightPadding: 8
                    }
                    Rectangle {
                        implicitWidth: 52; implicitHeight: 16; radius: 2
                        color: Qt.rgba(root.levelColor(logRow.level).r,
                                       root.levelColor(logRow.level).g,
                                       root.levelColor(logRow.level).b, 0.15)
                        Layout.rightMargin: 8
                        Text {
                            anchors.centerIn: parent
                            text: logRow.level === "CRITICAL" ? "CRIT" : logRow.level
                            color: root.levelColor(logRow.level)
                            font.pixelSize: 10; font.family: "Consolas, Courier New, monospace"
                            font.weight: Font.Bold
                        }
                    }
                    Text {
                        text: logRow.name; color: Theme.textSecondary
                        font.pixelSize: 11; font.family: "Consolas, Courier New, monospace"
                        leftPadding: 6; rightPadding: 8; elide: Text.ElideRight
                        Layout.preferredWidth: 200
                    }
                    Text {
                        text: logRow.message; color: root.levelColor(logRow.level)
                        font.pixelSize: 11; font.family: "Consolas, Courier New, monospace"
                        Layout.fillWidth: true; wrapMode: Text.NoWrap; elide: Text.ElideRight
                    }
                }
            }

            onCountChanged: { if (scrollToggle.checked) logList.positionViewAtEnd() }
        }
    }

    // ── Receive new log records ───────────────────────────────────────────────
    Connections {
        target: LogViewModel
        function onRecordAdded(time, level, name, message) { logModel.append({ time, level, name, message }) }
        function onCleared() { logModel.clear() }
    }
}
