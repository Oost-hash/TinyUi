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

    readonly property var _vm: RuntimeViewModel ?? null
    property real unitColumnWidth: 280
    property real stateColumnWidth: 82
    property real kindColumnWidth: 78
    property real policyColumnWidth: 96
    property real activationColumnWidth: 96
    property real stageColumnWidth: 76
    property real pidColumnWidth: 84
    property real parentColumnWidth: 220
    readonly property real tableWidth:
        unitColumnWidth + stateColumnWidth + kindColumnWidth
        + policyColumnWidth + activationColumnWidth + stageColumnWidth
        + pidColumnWidth + parentColumnWidth + 48

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // ── Toolbar ───────────────────────────────────────────────────────────
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
                spacing: 12

                Text {
                    width: parent.width - 96
                    height: parent.height
                    verticalAlignment: Text.AlignVCenter
                    text: root._vm ? root._vm.summary : "No runtime data"
                    color: Theme.textMuted
                    font.pixelSize: Theme.fontSizeSmall
                    font.family: "Consolas, Courier New, monospace"
                    elide: Text.ElideRight
                }

                Rectangle {
                    width: 84
                    height: 22
                    radius: 3
                    anchors.verticalCenter: parent.verticalCenter
                    color: runtimeCopyMouse.containsMouse ? Theme.surfaceRaised : "transparent"
                    border.color: Theme.border
                    border.width: 1
                    opacity: root._vm && root._vm.units.length > 0 ? 1 : 0.45

                    Text {
                        anchors.centerIn: parent
                        text: "Copy all"
                        color: Theme.textMuted
                        font.pixelSize: Theme.fontSizeSmall
                        font.family: "Consolas, Courier New, monospace"
                    }

                    MouseArea {
                        id: runtimeCopyMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        enabled: root._vm && root._vm.units.length > 0
                        onClicked: {
                            if (root._vm)
                                root._vm.copyOverview()
                        }
                    }
                }
            }
        }

        // ── State filter bar ──────────────────────────────────────────────────
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
                contentWidth: runtimeFilterRow.implicitWidth + 16
                contentHeight: height
                clip: true
                flickableDirection: Flickable.HorizontalFlick
                ScrollBar.horizontal: ScrollBar { policy: ScrollBar.AsNeeded; height: 4 }

                Row {
                    id: runtimeFilterRow
                    x: 8
                    height: parent.height
                    spacing: 4

                    Rectangle {
                        anchors.verticalCenter: parent.verticalCenter
                        width: 44; height: 20; radius: 3
                        readonly property bool on: root._vm && root._vm.stateFilters.length === root._vm.availableStateFilters.length
                        color: on ? Theme.withAlpha(Theme.accent, 0.18) : "transparent"
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
                            enabled: root._vm
                            onClicked: {
                                if (root._vm)
                                    root._vm.resetStateFilters()
                            }
                        }
                    }

                    Rectangle {
                        anchors.verticalCenter: parent.verticalCenter
                        width: 1; height: 14
                        color: Theme.border
                    }

                    Repeater {
                        model: root._vm ? root._vm.availableStateFilters : []

                        delegate: Rectangle {
                            id: filterChip
                            required property string modelData
                            anchors.verticalCenter: parent.verticalCenter
                            implicitWidth: filterLabel.implicitWidth + 12
                            height: 20; radius: 3

                            readonly property bool active: root._vm && root._vm.stateFilters.indexOf(filterChip.modelData) >= 0

                            color: filterChip.active ? Theme.withAlpha(Theme.accent, 0.12) : "transparent"
                            border.color: filterChip.active ? Theme.accent : Theme.border
                            border.width: 1

                            Text {
                                id: filterLabel
                                anchors.centerIn: parent
                                text: filterChip.modelData
                                color: filterChip.active ? Theme.accent : Theme.textMuted
                                font.pixelSize: 10
                                font.family: "Consolas, Courier New, monospace"
                            }

                            MouseArea {
                                anchors.fill: parent
                                enabled: root._vm
                                onClicked: {
                                    if (root._vm)
                                        root._vm.toggleStateFilter(filterChip.modelData)
                                }
                            }
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

            Flickable {
                anchors.fill: parent
                contentWidth: root.tableWidth
                contentHeight: height
                clip: true
                flickableDirection: Flickable.HorizontalFlick
                ScrollBar.horizontal: ScrollBar { policy: ScrollBar.AsNeeded; height: 4 }

                Row {
                    x: 10
                    width: root.tableWidth - 20
                    height: parent.height
                    spacing: 8

                    Rectangle {
                        width: root.unitColumnWidth; height: parent.height; color: "transparent"
                        Text {
                            anchors.fill: parent
                            verticalAlignment: Text.AlignVCenter
                            text: "Unit" + (root._vm && root._vm.sortKey === "id" ? (root._vm.sortDescending ? " ▼" : " ▲") : "")
                            color: Theme.textMuted
                            font.pixelSize: 10
                            font.family: "Consolas, Courier New, monospace"
                            font.weight: Font.DemiBold
                        }
                        MouseArea {
                            anchors.fill: parent
                            enabled: root._vm
                            onClicked: {
                                if (root._vm)
                                    root._vm.setSort("id")
                            }
                        }

                        Rectangle {
                            anchors.top: parent.top
                            anchors.bottom: parent.bottom
                            anchors.right: parent.right
                            width: 6
                            color: unitResize.containsMouse || unitResize.drag.active ? Theme.withAlpha(Theme.accent, 0.22) : "transparent"

                            MouseArea {
                                id: unitResize
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.SizeHorCursor
                                property real startWidth: 0
                                property real startX: 0
                                drag.target: null
                                onPressed: function(mouse) {
                                    startWidth = root.unitColumnWidth
                                    startX = mouse.x
                                }
                                onPositionChanged: function(mouse) {
                                    if (!pressed)
                                        return
                                    root.unitColumnWidth = Math.max(180, startWidth + (mouse.x - startX))
                                }
                            }
                        }
                    }

                    Rectangle {
                        width: root.stateColumnWidth; height: parent.height; color: "transparent"
                        Text {
                            anchors.fill: parent
                            verticalAlignment: Text.AlignVCenter
                            text: "State" + (root._vm && root._vm.sortKey === "state" ? (root._vm.sortDescending ? " ▼" : " ▲") : "")
                            color: Theme.textMuted
                            font.pixelSize: 10
                            font.family: "Consolas, Courier New, monospace"
                            font.weight: Font.DemiBold
                        }
                        MouseArea {
                            anchors.fill: parent
                            enabled: root._vm
                            onClicked: {
                                if (root._vm)
                                    root._vm.setSort("state")
                            }
                        }
                    }

                    Text { width: root.kindColumnWidth; height: parent.height; verticalAlignment: Text.AlignVCenter; text: "Kind"; color: Theme.textMuted; font.pixelSize: 10; font.family: "Consolas, Courier New, monospace"; font.weight: Font.DemiBold }
                    Text { width: root.policyColumnWidth; height: parent.height; verticalAlignment: Text.AlignVCenter; text: "Policy"; color: Theme.textMuted; font.pixelSize: 10; font.family: "Consolas, Courier New, monospace"; font.weight: Font.DemiBold }
                    Text { width: root.activationColumnWidth; height: parent.height; verticalAlignment: Text.AlignVCenter; text: "Activation"; color: Theme.textMuted; font.pixelSize: 10; font.family: "Consolas, Courier New, monospace"; font.weight: Font.DemiBold }
                    Text { width: root.stageColumnWidth; height: parent.height; verticalAlignment: Text.AlignVCenter; text: "Stage"; color: Theme.textMuted; font.pixelSize: 10; font.family: "Consolas, Courier New, monospace"; font.weight: Font.DemiBold }
                    Text { width: root.pidColumnWidth; height: parent.height; verticalAlignment: Text.AlignVCenter; text: "PID"; color: Theme.textMuted; font.pixelSize: 10; font.family: "Consolas, Courier New, monospace"; font.weight: Font.DemiBold }

                    Rectangle {
                        width: root.parentColumnWidth; height: parent.height; color: "transparent"
                        Text {
                            anchors.fill: parent
                            verticalAlignment: Text.AlignVCenter
                            text: "Parent"
                            color: Theme.textMuted
                            font.pixelSize: 10
                            font.family: "Consolas, Courier New, monospace"
                            font.weight: Font.DemiBold
                        }

                        Rectangle {
                            anchors.top: parent.top
                            anchors.bottom: parent.bottom
                            anchors.right: parent.right
                            width: 6
                            color: parentResize.containsMouse || parentResize.drag.active ? Theme.withAlpha(Theme.accent, 0.22) : "transparent"

                            MouseArea {
                                id: parentResize
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.SizeHorCursor
                                property real startWidth: 0
                                property real startX: 0
                                drag.target: null
                                onPressed: function(mouse) {
                                    startWidth = root.parentColumnWidth
                                    startX = mouse.x
                                }
                                onPositionChanged: function(mouse) {
                                    if (!pressed)
                                        return
                                    root.parentColumnWidth = Math.max(140, startWidth + (mouse.x - startX))
                                }
                            }
                        }
                    }
                }
            }
        }

        // ── Runtime list ──────────────────────────────────────────────────────
        Flickable {
            Layout.fillWidth: true
            Layout.fillHeight: true
            contentWidth: root.tableWidth
            contentHeight: height
            clip: true
            flickableDirection: Flickable.HorizontalFlick
            ScrollBar.horizontal: ScrollBar { policy: ScrollBar.AsNeeded; height: 6 }

            ListView {
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                width: root.tableWidth
                clip: true
                model: root._vm ? root._vm.rowsModel : null
                spacing: 0
                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

                delegate: Rectangle {
                    id: unitRow
                    required property int index
                    required property var modelData
                    width: ListView.view.width
                    height: 24
                    color: unitRow.index % 2 === 0 ? "transparent" : Qt.rgba(1, 1, 1, 0.02)

                    Row {
                        anchors.fill: parent
                        anchors.leftMargin: 10
                        anchors.rightMargin: 10
                        spacing: 8

                        Item {
                            width: root.unitColumnWidth
                            height: parent.height

                            Row {
                                anchors.fill: parent
                                spacing: 0

                                Item {
                                    width: (unitRow.modelData.depth || 0) * 14
                                    height: parent.height
                                }

                                Text {
                                    width: 16
                                    height: parent.height
                                    verticalAlignment: Text.AlignVCenter
                                    text: unitRow.modelData.hasChildren ? (unitRow.modelData.expanded ? "▾" : "▸") : ""
                                    color: Theme.textMuted
                                    font.pixelSize: 10
                                    font.family: "Consolas, Courier New, monospace"
                                }

                                Text {
                                    width: Math.max(48, root.unitColumnWidth - 16 - ((unitRow.modelData.depth || 0) * 14))
                                    height: parent.height
                                    verticalAlignment: Text.AlignVCenter
                                    text: unitRow.modelData.displayId
                                    color: Theme.text
                                    font.pixelSize: 11
                                    font.family: "Consolas, Courier New, monospace"
                                    elide: Text.ElideRight
                                }
                            }

                            MouseArea {
                                anchors.fill: parent
                                enabled: unitRow.modelData.hasChildren
                                onClicked: {
                                    if (root._vm)
                                        root._vm.toggleExpanded(unitRow.modelData.id)
                                }
                            }
                        }
                        Text { width: root.stateColumnWidth; height: parent.height; verticalAlignment: Text.AlignVCenter; text: unitRow.modelData.state; color: unitRow.modelData.state === "failed" ? Theme.danger : (unitRow.modelData.state === "running" ? Theme.accent : Theme.textMuted); font.pixelSize: 11; font.family: "Consolas, Courier New, monospace" }
                        Text { width: root.kindColumnWidth; height: parent.height; verticalAlignment: Text.AlignVCenter; text: unitRow.modelData.kind; color: Theme.textMuted; font.pixelSize: 11; font.family: "Consolas, Courier New, monospace" }
                        Text { width: root.policyColumnWidth; height: parent.height; verticalAlignment: Text.AlignVCenter; text: unitRow.modelData.execution; color: Theme.textMuted; font.pixelSize: 11; font.family: "Consolas, Courier New, monospace" }
                        Text { width: root.activationColumnWidth; height: parent.height; verticalAlignment: Text.AlignVCenter; text: unitRow.modelData.activation; color: Theme.textMuted; font.pixelSize: 11; font.family: "Consolas, Courier New, monospace" }
                        Text { width: root.stageColumnWidth; height: parent.height; verticalAlignment: Text.AlignVCenter; text: unitRow.modelData.stage; color: Theme.textMuted; font.pixelSize: 11; font.family: "Consolas, Courier New, monospace"; elide: Text.ElideRight }
                        Text { width: root.pidColumnWidth; height: parent.height; verticalAlignment: Text.AlignVCenter; text: unitRow.modelData.pid; color: Theme.textMuted; font.pixelSize: 11; font.family: "Consolas, Courier New, monospace"; elide: Text.ElideRight }
                        Text { width: root.parentColumnWidth; height: parent.height; verticalAlignment: Text.AlignVCenter; text: unitRow.modelData.parent; color: Theme.textMuted; font.pixelSize: 11; font.family: "Consolas, Courier New, monospace"; elide: Text.ElideRight }
                    }
                }

                Text {
                    anchors.centerIn: parent
                    visible: !root._vm || root._vm.units.length === 0
                    text: "No runtime units available."
                    color: Theme.textMuted
                    font.pixelSize: Theme.fontSizeSmall
                    font.family: Theme.fontFamily
                }
            }
        }

        // ── Tasks footer ──────────────────────────────────────────────────────
        Rectangle {
            Layout.fillWidth: true
            implicitHeight: 28
            color: Theme.surfaceAlt
            visible: root._vm && root._vm.taskIds.length > 0

            Rectangle {
                anchors.top: parent.top
                width: parent.width; height: 1
                color: Theme.border
            }

            Text {
                anchors.fill: parent
                anchors.leftMargin: 10
                anchors.rightMargin: 10
                verticalAlignment: Text.AlignVCenter
                text: root._vm ? ("Tasks: " + root._vm.taskIds.join(", ")) : ""
                color: Theme.textMuted
                font.pixelSize: 10
                font.family: "Consolas, Courier New, monospace"
                elide: Text.ElideRight
            }
        }
    }
}
