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
import "components"

BaseDialog {
    id: devTools
    dialogTitle: "Dev Tools"
    width:  800
    height: 500

    onCloseRequested: devTools.hide()

    // ── Tab bar ───────────────────────────────────────────────────────────────

    property int currentTab: 0

    readonly property var _tabs: ["State", "Console"]

    // ── Layout ────────────────────────────────────────────────────────────────

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // Tab strip
        Rectangle {
            Layout.fillWidth: true
            height: 32
            color: theme.surfaceAlt

            Rectangle {
                anchors.bottom: parent.bottom
                width: parent.width; height: 1
                color: theme.border
            }

            Row {
                anchors.left:   parent.left
                anchors.top:    parent.top
                anchors.bottom: parent.bottom
                anchors.leftMargin: 8
                spacing: 0

                Repeater {
                    model: devTools._tabs

                    delegate: Rectangle {
                        required property string modelData
                        required property int    index

                        width:  tabLabel.implicitWidth + 24
                        height: parent.height
                        color: "transparent"

                        readonly property bool active: devTools.currentTab === index

                        Rectangle {
                            anchors.bottom: parent.bottom
                            width: parent.width; height: 2
                            color: parent.active ? theme.accent : "transparent"
                        }

                        Text {
                            id: tabLabel
                            anchors.centerIn: parent
                            text: modelData
                            color: parent.active ? theme.accent : theme.textMuted
                            font.pixelSize: theme.fontSizeSmall
                            font.family: theme.fontFamily
                            font.weight: parent.active ? Font.DemiBold : Font.Normal
                        }

                        MouseArea {
                            anchors.fill: parent
                            onClicked: devTools.currentTab = index
                        }
                    }
                }
            }
        }

        // ── State tab ─────────────────────────────────────────────────────────

        Item {
            id: stateTab
            Layout.fillWidth: true
            Layout.fillHeight: true
            visible: devTools.currentTab === 0

            // Refreshes "active" dot colors without requiring Python to re-emit
            property real currentTime: Date.now()
            Timer { interval: 500; running: true; repeat: true; onTriggered: parent.currentTime = Date.now() }

            readonly property var _vm: stateMonitorViewModel ?? null

            ColumnLayout {
                anchors.fill: parent
                spacing: 0

                // ── Source selector ───────────────────────────────────────────
                Rectangle {
                    Layout.fillWidth: true
                    height: 34
                    color: theme.surfaceAlt

                    Rectangle {
                        anchors.bottom: parent.bottom
                        width: parent.width; height: 1
                        color: theme.border
                    }

                    Flickable {
                        anchors.fill: parent
                        contentWidth: sourceRow.implicitWidth + 16
                        contentHeight: height
                        clip: true
                        flickableDirection: Flickable.HorizontalFlick
                        ScrollBar.horizontal: ScrollBar { policy: ScrollBar.AsNeeded; height: 3 }

                        Row {
                            id: sourceRow
                            x: 8
                            height: parent.height
                            spacing: 4

                            Repeater {
                                model: stateTab._vm ? stateTab._vm.sources : []

                                delegate: Rectangle {
                                    required property var modelData

                                    anchors.verticalCenter: parent.verticalCenter
                                    implicitWidth: srcLabel.implicitWidth + 16
                                    height: 22; radius: 3

                                    readonly property bool active:
                                        stateTab._vm && stateTab._vm.selectedIndex === modelData.index

                                    color: active
                                           ? Qt.rgba(theme.accent.r, theme.accent.g, theme.accent.b, 0.15)
                                           : (srcArea.containsMouse ? theme.surfaceRaised : "transparent")
                                    border.width: 1
                                    border.color: active ? theme.accent : theme.border

                                    Behavior on color        { ColorAnimation { duration: 80 } }
                                    Behavior on border.color { ColorAnimation { duration: 80 } }

                                    Text {
                                        id: srcLabel
                                        anchors.centerIn: parent
                                        text: modelData.label
                                        color: parent.active ? theme.accent : theme.textMuted
                                        font.pixelSize: theme.fontSizeSmall
                                        font.family: theme.fontFamily
                                        Behavior on color { ColorAnimation { duration: 80 } }
                                    }

                                    MouseArea {
                                        id: srcArea
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        onClicked: {
                                            if (stateTab._vm)
                                                stateTab._vm.selectSource(modelData.index)
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                // ── Column headers ────────────────────────────────────────────
                Rectangle {
                    Layout.fillWidth: true
                    height: 24
                    color: theme.surfaceAlt

                    Rectangle {
                        anchors.bottom: parent.bottom
                        width: parent.width; height: 1
                        color: theme.border
                    }

                    Row {
                        anchors.fill: parent
                        anchors.leftMargin: 26
                        anchors.rightMargin: 12

                        Text {
                            width: parent.width * 0.60
                            height: parent.height
                            verticalAlignment: Text.AlignVCenter
                            text: "Property"
                            color: theme.textMuted
                            font.pixelSize: 10
                            font.family: "Consolas, Courier New, monospace"
                            font.weight: Font.DemiBold
                        }
                        Text {
                            width: parent.width * 0.40
                            height: parent.height
                            verticalAlignment: Text.AlignVCenter
                            text: "Value"
                            color: theme.textMuted
                            font.pixelSize: 10
                            font.family: "Consolas, Courier New, monospace"
                            font.weight: Font.DemiBold
                        }
                    }
                }

                // ── Property list ─────────────────────────────────────────────
                ListView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    model: stateTab._vm ? stateTab._vm.entries : []
                    spacing: 0
                    ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

                    delegate: Item {
                        id: stateRow
                        required property var modelData
                        required property int index

                        width: ListView.view.width
                        height: 22

                        // Flash overlay — fades from yellow on change
                        Rectangle {
                            id: flashRect
                            anchors.fill: parent
                            color: "#50FFD700"
                            opacity: 0
                        }

                        Rectangle {
                            anchors.fill: parent
                            color: index % 2 === 0 ? "transparent" : Qt.rgba(1,1,1,0.02)
                            z: -1
                        }

                        Row {
                            anchors.fill: parent
                            anchors.leftMargin: 12
                            anchors.rightMargin: 12
                            spacing: 6

                            // Heartbeat dot — green within 2 s of last change
                            Rectangle {
                                width: 6; height: 6; radius: 3
                                anchors.verticalCenter: parent.verticalCenter
                                color: (stateTab.currentTime - stateRow.modelData.changedAt) < 2000
                                       ? "#44FF88" : theme.border
                                Behavior on color { ColorAnimation { duration: 300 } }
                            }

                            Text {
                                width: parent.width * 0.60
                                height: parent.height
                                verticalAlignment: Text.AlignVCenter
                                text: stateRow.modelData.key
                                color: theme.textMuted
                                font.pixelSize: 11
                                font.family: "Consolas, Courier New, monospace"
                                elide: Text.ElideLeft
                            }
                            Text {
                                width: parent.width * 0.35
                                height: parent.height
                                verticalAlignment: Text.AlignVCenter
                                text: stateRow.modelData.value
                                color: theme.text
                                font.pixelSize: 11
                                font.family: "Consolas, Courier New, monospace"
                                elide: Text.ElideRight
                            }
                        }

                        NumberAnimation {
                            id: flashAnim
                            target: flashRect; property: "opacity"
                            from: 1.0; to: 0.0
                            duration: 600; easing.type: Easing.OutQuad
                        }

                        Component.onCompleted: {
                            if (stateRow.modelData.changed) flashAnim.start()
                        }
                    }

                    // Empty state
                    Text {
                        anchors.centerIn: parent
                        visible: !stateTab._vm || stateTab._vm.entries.length === 0
                        text: stateTab._vm && stateTab._vm.sources.length === 0
                              ? "No sources — load a plugin with widgets to start monitoring."
                              : "Select a source above."
                        color: theme.textMuted
                        font.pixelSize: theme.fontSizeSmall
                        font.family: theme.fontFamily
                    }
                }
            }
        }

        // ── Console tab ───────────────────────────────────────────────────────

        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true
            visible: devTools.currentTab === 1

            // Level filter state — local to this item
            property bool showDebug:   true
            property bool showInfo:    true
            property bool showWarning: true
            property bool showError:   true

            function levelVisible(level) {
                if (level === "DEBUG")   return showDebug
                if (level === "INFO")    return showInfo
                if (level === "WARNING") return showWarning
                return showError
            }

            function levelColor(level) {
                if (level === "DEBUG")   return theme.textMuted
                if (level === "INFO")    return theme.text
                if (level === "WARNING") return theme.warning
                return theme.danger
            }

            id: consolePane

            ListModel { id: logModel }

            ColumnLayout {
                anchors.fill: parent
                spacing: 0

                // Toolbar
                Rectangle {
                    Layout.fillWidth: true
                    height: 36
                    color: theme.surfaceAlt

                    Rectangle {
                        anchors.bottom: parent.bottom
                        width: parent.width; height: 1
                        color: theme.border
                    }

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 8; anchors.rightMargin: 8

                        Row {
                            spacing: 4
                            Repeater {
                                model: ["DEBUG", "INFO", "WARN", "ERROR"]
                                delegate: Rectangle {
                                    required property string modelData
                                    required property int    index

                                    property bool active: {
                                        if (modelData === "DEBUG") return consolePane.showDebug
                                        if (modelData === "INFO")  return consolePane.showInfo
                                        if (modelData === "WARN")  return consolePane.showWarning
                                        return consolePane.showError
                                    }
                                    property color levelCol: {
                                        if (modelData === "DEBUG") return theme.textMuted
                                        if (modelData === "INFO")  return theme.text
                                        if (modelData === "WARN")  return theme.warning
                                        return theme.danger
                                    }
                                    width: 52; height: 22; radius: 3
                                    color:        active ? Qt.rgba(levelCol.r, levelCol.g, levelCol.b, 0.15) : "transparent"
                                    border.color: active ? levelCol : theme.border
                                    border.width: 1

                                    Text {
                                        anchors.centerIn: parent
                                        text: modelData
                                        color: parent.active ? parent.levelCol : theme.textMuted
                                        font.pixelSize: theme.fontSizeSmall
                                        font.family: "Consolas, Courier New, monospace"
                                        font.weight: Font.DemiBold
                                    }
                                    MouseArea {
                                        anchors.fill: parent
                                        onClicked: {
                                            if (modelData === "DEBUG") consolePane.showDebug   = !consolePane.showDebug
                                            if (modelData === "INFO")  consolePane.showInfo    = !consolePane.showInfo
                                            if (modelData === "WARN")  consolePane.showWarning = !consolePane.showWarning
                                            if (modelData === "ERROR") consolePane.showError   = !consolePane.showError
                                        }
                                    }
                                }
                            }
                        }

                        Item { Layout.fillWidth: true }

                        Rectangle {
                            width: 100; height: 22; radius: 3
                            color: autoScrollMouse.containsMouse ? theme.surfaceRaised : "transparent"
                            Text {
                                anchors.centerIn: parent
                                text: scrollToggle.checked ? "Auto-scroll ON" : "Auto-scroll OFF"
                                color: scrollToggle.checked ? theme.accent : theme.textMuted
                                font.pixelSize: theme.fontSizeSmall
                                font.family: "Consolas, Courier New, monospace"
                            }
                            MouseArea {
                                id: autoScrollMouse; anchors.fill: parent; hoverEnabled: true
                                onClicked: scrollToggle.checked = !scrollToggle.checked
                            }
                            CheckBox { id: scrollToggle; checked: true; visible: false }
                        }

                        Rectangle {
                            width: 48; height: 22; radius: 3
                            color: clearMouse.containsMouse ? theme.surfaceRaised : "transparent"
                            Text {
                                anchors.centerIn: parent; text: "Clear"
                                color: theme.textMuted
                                font.pixelSize: theme.fontSizeSmall
                                font.family: "Consolas, Courier New, monospace"
                            }
                            MouseArea {
                                id: clearMouse; anchors.fill: parent; hoverEnabled: true
                                onClicked: { logModel.clear(); logViewModel.clear() }
                            }
                        }
                    }
                }

                // Category filter bar — dev mode toggle + per-category chips
                Rectangle {
                    Layout.fillWidth: true
                    height: 30
                    color: theme.surface

                    Rectangle {
                        anchors.bottom: parent.bottom
                        width: parent.width; height: 1
                        color: theme.border
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

                            // ── Dev mode master toggle ─────────────────────────
                            Rectangle {
                                anchors.verticalCenter: parent.verticalCenter
                                width: 44; height: 20; radius: 3
                                readonly property bool on: logSettingsViewModel
                                                           ? logSettingsViewModel.devMode : false
                                color:        on ? Qt.rgba(theme.accent.r, theme.accent.g, theme.accent.b, 0.18)
                                                 : "transparent"
                                border.color: on ? theme.accent : theme.border
                                border.width: 1

                                Text {
                                    anchors.centerIn: parent
                                    text: "DEV"
                                    color: parent.on ? theme.accent : theme.textMuted
                                    font.pixelSize: 10
                                    font.family: "Consolas, Courier New, monospace"
                                    font.weight: Font.Bold
                                }
                                MouseArea {
                                    anchors.fill: parent
                                    onClicked: {
                                        if (logSettingsViewModel)
                                            logSettingsViewModel.setDevMode(!logSettingsViewModel.devMode)
                                    }
                                }
                            }

                            // Divider
                            Rectangle {
                                anchors.verticalCenter: parent.verticalCenter
                                width: 1; height: 14
                                color: theme.border
                            }

                            // ── Per-category chips ─────────────────────────────
                            Repeater {
                                model: logSettingsViewModel ? logSettingsViewModel.categories : []

                                delegate: Rectangle {
                                    required property var modelData
                                    anchors.verticalCenter: parent.verticalCenter
                                    implicitWidth:  catLabel.implicitWidth + 12
                                    height: 20; radius: 3

                                    readonly property bool devOn: logSettingsViewModel
                                                                  ? logSettingsViewModel.devMode : false
                                    readonly property bool catOn: modelData.enabled && devOn

                                    color:        catOn ? Qt.rgba(theme.accent.r, theme.accent.g, theme.accent.b, 0.12)
                                                        : "transparent"
                                    border.color: catOn ? theme.accent : theme.border
                                    border.width: 1
                                    opacity: devOn ? 1.0 : 0.4

                                    Behavior on opacity { NumberAnimation { duration: 120 } }

                                    Text {
                                        id: catLabel
                                        anchors.centerIn: parent
                                        text: modelData.name
                                        color: parent.catOn ? theme.accent : theme.textMuted
                                        font.pixelSize: 10
                                        font.family: "Consolas, Courier New, monospace"
                                    }
                                    MouseArea {
                                        anchors.fill: parent
                                        enabled: parent.devOn
                                        onClicked: {
                                            if (logSettingsViewModel)
                                                logSettingsViewModel.setCategoryEnabled(
                                                    modelData.name, !modelData.enabled)
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                // Log list
                ListView {
                    id: logList
                    Layout.fillWidth: true; Layout.fillHeight: true
                    clip: true; model: logModel; spacing: 0
                    ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

                    delegate: Item {
                        width: logList.width
                        visible: consolePane.levelVisible(model.level)
                        height:  visible ? row.implicitHeight + 2 : 0

                        RowLayout {
                            id: row
                            anchors { left: parent.left; right: parent.right; leftMargin: 8; rightMargin: 8 }
                            anchors.verticalCenter: parent.verticalCenter
                            spacing: 0

                            Text {
                                text: model.time; color: theme.textMuted
                                font.pixelSize: 11; font.family: "Consolas, Courier New, monospace"
                                rightPadding: 8
                            }
                            Rectangle {
                                width: 52; height: 16; radius: 2
                                color: Qt.rgba(consolePane.levelColor(model.level).r,
                                               consolePane.levelColor(model.level).g,
                                               consolePane.levelColor(model.level).b, 0.15)
                                Layout.rightMargin: 8
                                Text {
                                    anchors.centerIn: parent
                                    text: model.level === "CRITICAL" ? "CRIT" : model.level
                                    color: consolePane.levelColor(model.level)
                                    font.pixelSize: 10; font.family: "Consolas, Courier New, monospace"
                                    font.weight: Font.Bold
                                }
                            }
                            Text {
                                text: model.name; color: theme.textSecondary
                                font.pixelSize: 11; font.family: "Consolas, Courier New, monospace"
                                leftPadding: 6; rightPadding: 8; elide: Text.ElideRight
                                Layout.preferredWidth: 200
                            }
                            Text {
                                text: model.message; color: consolePane.levelColor(model.level)
                                font.pixelSize: 11; font.family: "Consolas, Courier New, monospace"
                                Layout.fillWidth: true; wrapMode: Text.NoWrap; elide: Text.ElideRight
                            }
                        }
                    }

                    onCountChanged: { if (scrollToggle.checked) logList.positionViewAtEnd() }
                }
            }

            Connections {
                target: logViewModel
                function onRecordAdded(time, level, name, message) { logModel.append({ time, level, name, message }) }
                function onCleared() { logModel.clear() }
            }
        }
    }
}
