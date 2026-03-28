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
import "../../tinyui/qml/components"

Item {
    id: root

    // Refreshes "active" dot colors without requiring Python to re-emit
    property real currentTime: Date.now()
    Timer { interval: 500; running: true; repeat: true; onTriggered: root.currentTime = Date.now() }

    readonly property var _vm: StateMonitorViewModel ?? null

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // ── Source selector ───────────────────────────────────────────────────
        Rectangle {
            Layout.fillWidth: true
            implicitHeight: 34
            color: Theme.surfaceAlt

            Rectangle {
                anchors.bottom: parent.bottom
                width: parent.width; height: 1
                color: Theme.border
            }

            Row {
                anchors.fill: parent
                anchors.leftMargin: 8
                anchors.rightMargin: 8
                spacing: 8

                Text {
                    width: 46
                    height: parent.height
                    verticalAlignment: Text.AlignVCenter
                    text: "Source"
                    color: Theme.textMuted
                    font.pixelSize: Theme.fontSizeSmall
                    font.family: Theme.fontFamily
                }

                ThemedComboBox {
                    id: sourceCombo
                    anchors.verticalCenter: parent.verticalCenter
                    width: Math.min(parent.width - 54, 340)
                    model: root._vm ? root._vm.sources.map(function(item) { return item.label }) : []
                    currentIndex: root._vm ? root._vm.selectedIndex : -1
                    onActivated: function(index) {
                        if (root._vm)
                            root._vm.selectSource(index)
                    }
                }

                Item { width: 1; height: 1 }

                Rectangle {
                    width: 72
                    height: 22
                    radius: 3
                    anchors.verticalCenter: parent.verticalCenter
                    color: copyAllMouse.containsMouse ? Theme.surfaceRaised : "transparent"
                    border.color: Theme.border
                    border.width: 1
                    opacity: root._vm && root._vm.hasSelectedSource && root._vm.entries.length > 0 ? 1 : 0.45

                    Text {
                        anchors.centerIn: parent
                        text: "Copy all"
                        color: Theme.textMuted
                        font.pixelSize: Theme.fontSizeSmall
                        font.family: "Consolas, Courier New, monospace"
                    }

                    MouseArea {
                        id: copyAllMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        enabled: root._vm && root._vm.hasSelectedSource && root._vm.entries.length > 0
                        onClicked: {
                            if (root._vm)
                                root._vm.copyAllEntries()
                        }
                    }
                }

                Rectangle {
                    width: 78
                    height: 22
                    radius: 3
                    anchors.verticalCenter: parent.verticalCenter
                    color: root._vm && root._vm.captureActive
                           ? Theme.withAlpha(Theme.accent, 0.16)
                           : (recordMouse.containsMouse ? Theme.surfaceRaised : "transparent")
                    border.color: root._vm && root._vm.captureActive ? Theme.accent : Theme.border
                    border.width: 1
                    opacity: root._vm && root._vm.hasSelectedSource && root._vm.entries.length > 0 ? 1 : 0.45

                    Text {
                        anchors.centerIn: parent
                        text: root._vm && root._vm.captureActive ? "Recording" : "Record"
                        color: root._vm && root._vm.captureActive ? Theme.accent : Theme.textMuted
                        font.pixelSize: Theme.fontSizeSmall
                        font.family: "Consolas, Courier New, monospace"
                    }

                    MouseArea {
                        id: recordMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        enabled: root._vm && root._vm.hasSelectedSource && root._vm.entries.length > 0
                        onClicked: {
                            if (root._vm)
                                root._vm.toggleCapture()
                        }
                    }
                }

                Rectangle {
                    width: 86
                    height: 22
                    radius: 3
                    anchors.verticalCenter: parent.verticalCenter
                    color: copyCaptureMouse.containsMouse ? Theme.surfaceRaised : "transparent"
                    border.color: Theme.border
                    border.width: 1
                    opacity: root._vm && root._vm.captureActive ? 1 : 0.45

                    Text {
                        anchors.centerIn: parent
                        text: "Copy path"
                        color: Theme.textMuted
                        font.pixelSize: Theme.fontSizeSmall
                        font.family: "Consolas, Courier New, monospace"
                    }

                    MouseArea {
                        id: copyCaptureMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        enabled: root._vm && root._vm.captureActive
                        onClicked: {
                            if (root._vm)
                                root._vm.copyCapturePath()
                        }
                    }
                }
            }
        }

        // ── Column headers ────────────────────────────────────────────────────
        Rectangle {
            Layout.fillWidth: true
            implicitHeight: 24
            color: Theme.surfaceAlt

            Rectangle {
                anchors.bottom: parent.bottom
                width: parent.width; height: 1
                color: Theme.border
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
                    color: Theme.textMuted
                    font.pixelSize: 10
                    font.family: "Consolas, Courier New, monospace"
                    font.weight: Font.DemiBold
                }
                Text {
                    width: parent.width * 0.40
                    height: parent.height
                    verticalAlignment: Text.AlignVCenter
                    text: "Value"
                    color: Theme.textMuted
                    font.pixelSize: 10
                    font.family: "Consolas, Courier New, monospace"
                    font.weight: Font.DemiBold
                }
            }
        }

        // ── Property list ─────────────────────────────────────────────────────
        ListView {
            id: stateList
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: root._vm ? root._vm.sectionModel : null
            spacing: 0
            ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

            delegate: Item {
                id: stateRow
                required property string rowType
                required property real   changedAt
                required property int    index
                required property bool   collapsed
                required property string sectionTitle
                required property int    sectionCount
                required property string sectionName
                required property string keyText
                required property string valueText

                readonly property bool isSection: stateRow.rowType === "section"
                readonly property bool recentlyChanged:
                    !stateRow.isSection && (root.currentTime - stateRow.changedAt) < 600
                property real copiedAt: 0
                readonly property bool showCopied:
                    !stateRow.isSection && (root.currentTime - stateRow.copiedAt) < 900

                width: ListView.view.width
                height: stateRow.isSection ? 28 : 22

                Rectangle {
                    anchors.fill: parent
                    color: stateRow.isSection
                           ? Theme.surfaceAlt
                           : (stateRow.recentlyChanged
                              ? "#24FFD700"
                              : (stateRow.index % 2 === 0 ? "transparent" : Qt.rgba(1,1,1,0.02)))
                    z: -1
                    Behavior on color { ColorAnimation { duration: 180 } }
                }

                Rectangle {
                    visible: stateRow.isSection
                    anchors.bottom: parent.bottom
                    width: parent.width
                    height: 1
                    color: Theme.border
                    opacity: 0.4
                }

                Row {
                    visible: stateRow.isSection
                    anchors.fill: parent
                    anchors.leftMargin: 12
                    anchors.rightMargin: 12
                    spacing: 8

                    Text {
                        width: 14
                        height: parent.height
                        verticalAlignment: Text.AlignVCenter
                        text: stateRow.collapsed ? "▸" : "▾"
                        color: Theme.textMuted
                        font.pixelSize: 10
                        font.family: "Consolas, Courier New, monospace"
                    }

                    Text {
                        width: parent.width - 72
                        height: parent.height
                        verticalAlignment: Text.AlignVCenter
                        text: stateRow.sectionTitle
                        color: Theme.textSecondary
                        font.pixelSize: Theme.fontSizeSmall
                        font.family: Theme.fontFamily
                        font.weight: Font.DemiBold
                    }

                    Text {
                        width: 40
                        height: parent.height
                        horizontalAlignment: Text.AlignRight
                        verticalAlignment: Text.AlignVCenter
                        text: stateRow.sectionCount
                        color: Theme.textMuted
                        font.pixelSize: 10
                        font.family: "Consolas, Courier New, monospace"
                    }
                }

                MouseArea {
                    visible: stateRow.isSection
                    anchors.fill: parent
                    onClicked: {
                        if (root._vm)
                            root._vm.toggleSection(stateRow.sectionName)
                    }
                }

                Row {
                    visible: !stateRow.isSection
                    anchors.fill: parent
                    anchors.leftMargin: 24
                    anchors.rightMargin: 12
                    spacing: 6

                    Rectangle {
                        width: 6; height: 6; radius: 3
                        anchors.verticalCenter: parent.verticalCenter
                        color: (root.currentTime - stateRow.changedAt) < 2000
                               ? "#44FF88" : Theme.border
                        Behavior on color { ColorAnimation { duration: 300 } }
                    }

                    Text {
                        width: parent.width * 0.58
                        height: parent.height
                        verticalAlignment: Text.AlignVCenter
                        text: stateRow.keyText
                        color: Theme.textMuted
                        font.pixelSize: 11
                        font.family: "Consolas, Courier New, monospace"
                        elide: Text.ElideLeft
                    }

                    Item {
                        width: parent.width * 0.36
                        height: parent.height

                        Text {
                            anchors.fill: parent
                            verticalAlignment: Text.AlignVCenter
                            text: stateRow.showCopied ? "Copied" : stateRow.valueText
                            color: stateRow.showCopied ? Theme.accent : Theme.text
                            font.pixelSize: 11
                            font.family: "Consolas, Courier New, monospace"
                            elide: Text.ElideRight
                        }

                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            hoverEnabled: true
                            onClicked: {
                                if (root._vm) {
                                    root._vm.copyEntry(stateRow.keyText, stateRow.valueText)
                                    stateRow.copiedAt = Date.now()
                                }
                            }
                        }
                    }
                }
            }

            // Empty state
            Text {
                anchors.centerIn: parent
                visible: !root._vm
                         || root._vm.sources.length === 0
                         || !root._vm.hasSelectedSource
                         || stateList.count === 0
                text: !root._vm || root._vm.sources.length === 0
                      ? "No sources — load a plugin with widgets to start monitoring."
                      : (!root._vm.hasSelectedSource
                         ? "Select a source above."
                         : "No state available for this source yet.")
                color: Theme.textMuted
                font.pixelSize: Theme.fontSizeSmall
                font.family: Theme.fontFamily
            }
        }
    }
}
