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
import QtQuick.Window

Rectangle {
    id: root

    property var hostWindow: Window.window
    property var pluginRead: hostWindow && hostWindow.pluginRead ? hostWindow.pluginRead : null
    property var pluginState: hostWindow && hostWindow.pluginState ? hostWindow.pluginState : null
    property var settingsRead: hostWindow && hostWindow.settingsRead ? hostWindow.settingsRead : null
    property var connectorRead: hostWindow && hostWindow.connectorRead ? hostWindow.connectorRead : null
    property var connectorActions: hostWindow && hostWindow.connectorActions ? hostWindow.connectorActions : null
    property var theme: hostWindow && hostWindow.theme ? hostWindow.theme : null
    property var pluginRows: []
    property var settingRows: []
    property var connectorRows: []

    anchors.fill: parent
    color: theme ? theme.surface : "#17181c"

    property int currentTab: 0
    readonly property var tabs: ["Plugins", "Settings", "Connectors"]

    function rebuildRows() {
        var plugins = pluginRead ? pluginRead.plugins : []
        var states = pluginState ? pluginState.states : ({})
        var errors = pluginState ? pluginState.errors : ({})

        var pluginItems = []
        for (var i = 0; i < plugins.length; i++) {
            var info = plugins[i]
            var state = states[info.id] || "disabled"
            var error = errors[info.id] || ""
            var stateIndicator = ""
            if (state === "active") {
                stateIndicator = "[active]"
            } else if (state === "enabling" || state === "loading") {
                stateIndicator = "[loading]"
            } else if (state === "error") {
                stateIndicator = "[error]"
            }

            pluginItems.push({
                "rowType": "section",
                "label": info.id,
                "sublabel": (info.type + " " + stateIndicator).trim()
            })
            pluginItems.push({
                "rowType": "row",
                "key": "state",
                "value": state,
                "tag": "status"
            })
            if (error !== "") {
                pluginItems.push({
                    "rowType": "row",
                    "key": "error",
                    "value": error,
                    "tag": "error"
                })
            }
            for (var j = 0; j < info.windows.length; j++) {
                pluginItems.push({
                    "rowType": "row",
                    "key": "window",
                    "value": info.windows[j],
                    "tag": "window"
                })
            }
            pluginItems.push({
                "rowType": "row",
                "key": "settings",
                "value": info.settingCount ? String(info.settingCount) + " declared" : "none",
                "tag": ""
            })

            var history = pluginState ? pluginState.histories[info.id] : []
            for (var h = 0; h < history.length; h++) {
                var item = history[h]
                pluginItems.push({
                    "rowType": "row",
                    "key": "history",
                    "value": item.from + " -> " + item.to + " (" + item.reason + ")",
                    "tag": "history"
                })
            }
        }

        var settingsItems = []
        var currentNs = ""
        var settings = settingsRead ? settingsRead.settings : []
        for (var k = 0; k < settings.length; k++) {
            var setting = settings[k]
            if (setting.namespace !== currentNs) {
                currentNs = setting.namespace
                settingsItems.push({
                    "rowType": "section",
                    "label": setting.namespace,
                    "sublabel": ""
                })
            }
            settingsItems.push({
                "rowType": "row",
                "key": setting.key,
                "value": setting.currentValue,
                "tag": setting.type
            })
        }

        root.pluginRows = pluginItems
        root.settingRows = settingsItems
        root.connectorRows = root.buildConnectorRows()
    }

    function buildConnectorRows() {
        var rows = []
        var providers = connectorRead ? connectorRead.providers : []
        for (var i = 0; i < providers.length; i++) {
            var provider = providers[i]
            rows.push({
                "rowType": "section",
                "label": provider.label,
                "sublabel": provider.id
            })
            rows.push({
                "rowType": "row",
                "key": "plugin",
                "value": provider.pluginId,
                "tag": "provider"
            })
            var inspectionRows = connectorRead ? connectorRead.inspectionRows(provider.id) : []
            for (var j = 0; j < inspectionRows.length; j++) {
                rows.push({
                    "rowType": "row",
                    "key": inspectionRows[j].key,
                    "value": inspectionRows[j].value,
                    "tag": inspectionRows[j].key.indexOf("provider.") === 0 ? "provider" : "snapshot"
                })
            }
        }
        return rows
    }

    Column {
        anchors.fill: parent
        spacing: 0
        
        Connections {
            target: root.pluginRead
            function onPluginsChanged() { root.rebuildRows() }
        }

        Connections {
            target: root.pluginState
            function onStateDataChanged() { root.rebuildRows() }
        }

        Connections {
            target: root.settingsRead
            function onSettingsChanged() { root.rebuildRows() }
        }

        Connections {
            target: root.connectorRead
            function onProvidersChanged() { root.connectorRows = root.buildConnectorRows() }
            function onProviderDataChanged(providerId) { root.connectorRows = root.buildConnectorRows() }
        }

        // Tab strip
        Rectangle {
            width: parent.width
            height: 32
            color: root.theme ? root.theme.surfaceAlt : "#2f343e"

            Rectangle {
                anchors.bottom: parent.bottom
                width: parent.width
                height: 1
                color: root.theme ? root.theme.border : "#464b57"
            }

            Row {
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.leftMargin: 8
                spacing: 0

                Repeater {
                    model: root.tabs

                    delegate: Rectangle {
                        id: tabDelegate
                        required property string modelData
                        required property int index
                        width: tabLabel.implicitWidth + 24
                        height: parent.height
                        color: "transparent"

                        readonly property bool active: root.currentTab === tabDelegate.index

                        Rectangle {
                            anchors.bottom: parent.bottom
                            width: parent.width
                            height: 2
                            color: tabDelegate.active ? (root.theme ? root.theme.accent : "#4a9eff") : "transparent"
                        }

                        Text {
                            id: tabLabel
                            anchors.centerIn: parent
                            text: tabDelegate.modelData
                            color: tabDelegate.active
                                ? (root.theme ? root.theme.accent : "#4a9eff")
                                : (root.theme ? root.theme.textMuted : "#878a98")
                            font.pixelSize: root.theme ? root.theme.fontSizeSmall : 11
                            font.family: root.theme ? root.theme.fontFamily : "sans-serif"
                            font.weight: tabDelegate.active ? Font.DemiBold : Font.Normal
                        }

                        MouseArea {
                            anchors.fill: parent
                            onClicked: root.currentTab = tabDelegate.index
                        }
                    }
                }
            }
        }

        // Plugins tab
        SchemaList {
            id: pluginsTab
            visible: root.currentTab === 0
            width: parent.width
            height: parent.height - 32
            theme: root.theme
            model: root.pluginRows
            keyLabel: "property"
            valueLabel: "value"
            emptyText: "No plugins loaded."
        }

        // Settings tab
        SchemaList {
            id: settingsTab
            visible: root.currentTab === 1
            width: parent.width
            height: parent.height - 32
            theme: root.theme
            model: root.settingRows
            keyLabel: "key"
            valueLabel: "value"
            emptyText: "No settings declared."
        }

        SchemaList {
            id: connectorsTab
            visible: root.currentTab === 2
            width: parent.width
            height: parent.height - 32
            theme: root.theme
            model: root.connectorRows
            keyLabel: "property"
            valueLabel: "value"
            emptyText: "No connectors active."
        }
    }

    Timer {
        interval: 1000
        running: root.connectorActions !== null
        repeat: true
        onTriggered: {
            if (!root.connectorRead || !root.connectorActions)
                return
            var providers = root.connectorRead.providers
            for (var i = 0; i < providers.length; i++) {
                root.connectorActions.updateProvider(providers[i].id)
            }
        }
    }

    Component.onCompleted: rebuildRows()
}
