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
    readonly property var connectorApi: hostWindow && hostWindow.connectorApi ? hostWindow.connectorApi : null
    readonly property string providerId: "LMU_RF2_Connector"
    property var providerRows: []

    function refreshProviderRows() {
        if (!connectorApi) {
            root.providerRows = []
            return
        }
        root.connectorApi.updateProvider(root.providerId)
        root.providerRows = root.connectorApi.inspectionRows(root.providerId)
    }

    Component.onCompleted: {
        if (connectorApi) {
            connectorApi.requestSource(providerId, "dummy_plugin.widgets", "mock")
            refreshProviderRows()
        }
    }

    Component.onDestruction: {
        if (connectorApi) {
            connectorApi.releaseSource(providerId, "dummy_plugin.widgets")
        }
    }

    Connections {
        target: root.connectorApi
        function onProviderDataChanged(changedProviderId) {
            if (changedProviderId === root.providerId) {
                root.providerRows = root.connectorApi.inspectionRows(root.providerId)
            }
        }
    }

    Timer {
        interval: 1000
        running: root.connectorApi !== null
        repeat: true
        onTriggered: root.refreshProviderRows()
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
            text: root.providerRows.length > 0
                ? "Telemetry from LMU_RF2_Connector (mock source)"
                : "Provider not active"
            color: "#c8ccd4"
            font.pixelSize: 12
        }

        Repeater {
            model: root.providerRows

            delegate: Row {
                id: providerRowDelegate
                required property var modelData
                spacing: 12
                visible: String(providerRowDelegate.modelData.key).indexOf("provider.") === 0
                    || String(providerRowDelegate.modelData.key).indexOf("tyre.") === 0

                Text {
                    text: providerRowDelegate.modelData.key
                    color: "#878a98"
                    font.pixelSize: 12
                }

                Text {
                    text: providerRowDelegate.modelData.value
                    color: "#ffffff"
                    font.pixelSize: 12
                }
            }
        }
    }
}
