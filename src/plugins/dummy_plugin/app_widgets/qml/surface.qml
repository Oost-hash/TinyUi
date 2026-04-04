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
import QtQuick.Window

Rectangle {
    id: root
    anchors.fill: parent
    color: "transparent"

    readonly property var hostWindow: Window.window
    readonly property var connectorRead: hostWindow && hostWindow.connectorRead ? hostWindow.connectorRead : null
    readonly property var connectorActions: hostWindow && hostWindow.connectorActions ? hostWindow.connectorActions : null
    readonly property string connectorId: "LMU_RF2_Connector"
    property var connectorRows: []

    function refreshConnectorRows() {
        if (!connectorRead || !connectorActions) {
            root.connectorRows = []
            return
        }
        root.connectorActions.updateConnector(root.connectorId)
        root.connectorRows = root.connectorRead.inspectionRows(root.connectorId)
    }

    Component.onCompleted: {
        if (connectorRead && connectorActions) {
            connectorActions.requestSource(connectorId, "dummy_plugin.widgets", "mock")
            refreshConnectorRows()
        }
    }

    Component.onDestruction: {
        if (connectorActions) {
            connectorActions.releaseSource(connectorId, "dummy_plugin.widgets")
        }
    }

    Connections {
        target: root.connectorRead
        function onConnectorDataChanged(changedConnectorId) {
            if (changedConnectorId === root.connectorId) {
                root.connectorRows = root.connectorRead.inspectionRows(root.connectorId)
            }
        }
    }

    Timer {
        interval: 1000
        running: root.connectorRead !== null && root.connectorActions !== null
        repeat: true
        onTriggered: root.refreshConnectorRows()
    }

    Column {
        anchors.fill: parent
        anchors.margins: 24
        spacing: 12

        Text {
            text: "Dummy Plugin Tyres"
            color: "#ffffff"
            font.pixelSize: 20
        }

        Text {
            text: root.connectorRows.length > 0
                ? "Telemetry from LMU_RF2_Connector (mock source)"
                : "Connector not active"
            color: "#c8ccd4"
            font.pixelSize: 12
        }

        Repeater {
            model: root.connectorRows

            delegate: Row {
                id: connectorRowDelegate
                required property var modelData
                spacing: 12
                visible: String(connectorRowDelegate.modelData.key).indexOf("connector.") === 0
                    || String(connectorRowDelegate.modelData.key).indexOf("tyre.") === 0

                Text {
                    text: connectorRowDelegate.modelData.key
                    color: "#878a98"
                    font.pixelSize: 12
                }

                Text {
                    text: connectorRowDelegate.modelData.value
                    color: "#ffffff"
                    font.pixelSize: 12
                }
            }
        }
    }
}
