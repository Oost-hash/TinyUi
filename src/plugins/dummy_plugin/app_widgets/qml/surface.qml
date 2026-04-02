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
    readonly property var providerHub: hostWindow && hostWindow.providerHub ? hostWindow.providerHub : null
    readonly property string providerId: "LMU_RF2_Connector"
    property var providerRows: []

    function refreshProviderRows() {
        if (!providerHub) {
            providerRows = []
            return
        }
        providerHub.updateProvider(providerId)
        providerRows = providerHub.inspectionRows(providerId)
    }

    Component.onCompleted: {
        if (providerHub) {
            providerHub.requestSource(providerId, "dummy_plugin.widgets", "mock")
            refreshProviderRows()
        }
    }

    Component.onDestruction: {
        if (providerHub) {
            providerHub.releaseSource(providerId, "dummy_plugin.widgets")
        }
    }

    Connections {
        target: providerHub
        function onProviderDataChanged(changedProviderId) {
            if (changedProviderId === root.providerId) {
                root.providerRows = providerHub.inspectionRows(root.providerId)
            }
        }
    }

    Timer {
        interval: 1000
        running: root.providerHub !== null
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
            text: providerRows.length > 0
                ? "Telemetry from LMU_RF2_Connector (mock source)"
                : "Provider not active"
            color: "#c8ccd4"
            font.pixelSize: 12
        }

        Repeater {
            model: providerRows

            delegate: Row {
                required property var modelData
                spacing: 12
                visible: String(modelData.key).indexOf("provider.") === 0 || String(modelData.key).indexOf("tyre.") === 0

                Text {
                    text: modelData.key
                    color: "#878a98"
                    font.pixelSize: 12
                }

                Text {
                    text: modelData.value
                    color: "#ffffff"
                    font.pixelSize: 12
                }
            }
        }
    }
}
