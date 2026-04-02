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

    property var hostWindow: Window.window
    property var inspector: hostWindow && hostWindow.inspector ? hostWindow.inspector : null
    property var theme: hostWindow && hostWindow.theme ? hostWindow.theme : null
    
    // Signal to request plugin activation
    signal requestActivatePlugin(string pluginId)
    property var hostActions: hostWindow && hostWindow.hostActions ? hostWindow.hostActions : null
    property var selectedPlugin: null
    property string pluginToActivate: ""  // Plugin waiting to be activated on close
    
    // Track plugin states locally for live updates
    property var pluginStates: ({})  // Map pluginId -> state

    // Listen to state changes from runtime
    Connections {
        target: hostWindow ? hostWindow.hostRuntime : null
        function onPluginStateChanged(pluginId, state) {
            root.pluginStates[pluginId] = state
            // Force update
            var temp = root.pluginStates
            root.pluginStates = {}
            root.pluginStates = temp
        }
    }

    // Function to call when panel is closing - activates selected plugin
    function onPanelClosing() {
        if (pluginToActivate !== "" && hostWindow && hostWindow.hostRuntime) {
            hostWindow.hostRuntime.setActivePlugin(pluginToActivate)
            pluginToActivate = ""  // Reset
        }
    }
    
    // Check if a connector is used by the active plugin
    function isConnectorUsed(connectorId: string) : bool {
        if (!hostWindow || !hostWindow.activePluginId || !inspector) return false
        
        // Find the active plugin
        for (var i = 0; i < inspector.pluginList.length; i++) {
            var group = inspector.pluginList[i]
            for (var j = 0; j < group.plugins.length; j++) {
                var plugin = group.plugins[j]
                if (plugin.id === hostWindow.activePluginId) {
                    // Check if this plugin requires the connector
                    if (plugin.requires && plugin.requires.indexOf(connectorId) >= 0) {
                        return true
                    }
                }
            }
        }
        return false
    }

    anchors.fill: parent
    color: theme ? theme.surface : "#17181c"

    // Select active plugin when panel opens
    Component.onCompleted: {
        if (hostWindow && hostWindow.activePluginId && inspector) {
            // Find the active plugin in the list
            for (var i = 0; i < inspector.pluginList.length; i++) {
                var group = inspector.pluginList[i]
                for (var j = 0; j < group.plugins.length; j++) {
                    if (group.plugins[j].id === hostWindow.activePluginId) {
                        selectedPlugin = group.plugins[j]
                        return
                    }
                }
            }
        }
    }

    // ── Content: 70/30 split ─────────────────────────────────────────────────
    Row {
        anchors.fill: parent

        // ── Left pane (70%) ── Plugin details
        Item {
            width: parent.width * 0.70
            height: parent.height

            // Hero card header
            Rectangle {
                id: detailHeader
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: parent.right
                height: selectedPlugin ? 64 : 0
                visible: height > 0
                color: theme ? Qt.rgba(0, 0, 0, 0.2) : "#121316"

                Item {
                    anchors.fill: parent
                    anchors.leftMargin: 20
                    anchors.rightMargin: 20

                    Row {
                        id: heroRow
                        anchors.left: parent.left
                        anchors.verticalCenter: parent.verticalCenter
                        spacing: 16

                        // Large type icon/badge
                        Rectangle {
                            width: 48
                            height: 48
                            radius: 8
                            color: {
                                if (!selectedPlugin) return "#666"
                                if (selectedPlugin.type === "host") return theme ? theme.accent : "#4a9eff"
                                if (selectedPlugin.type === "connector") return theme ? theme.success : "#2ecc71"
                                return theme ? theme.warning : "#f39c12"
                            }

                            Text {
                                anchors.centerIn: parent
                                text: selectedPlugin ? selectedPlugin.type.charAt(0).toUpperCase() : "?"
                                color: "#FFFFFF"
                                font.pixelSize: 24
                                font.family: theme ? theme.fontFamily : "sans-serif"
                                font.weight: Font.Bold
                            }
                        }

                        Column {
                            spacing: 4

                            // Plugin name (hero style - large and bold)
                            Text {
                                text: selectedPlugin ? selectedPlugin.id : ""
                                color: theme ? theme.text : "#ffffff"
                                font.pixelSize: 20
                                font.family: theme ? theme.fontFamily : "sans-serif"
                                font.weight: Font.Bold
                            }

                            // Version and author row
                            Row {
                                spacing: 8

                                Text {
                                    visible: selectedPlugin && selectedPlugin.version !== ""
                                    text: selectedPlugin ? "v" + selectedPlugin.version : ""
                                    color: theme ? theme.accent : "#4a9eff"
                                    font.pixelSize: theme ? theme.fontSizeSmall : 11
                                    font.family: theme ? theme.fontFamily : "sans-serif"
                                }

                                Text {
                                    visible: selectedPlugin && selectedPlugin.author !== ""
                                    text: "•"
                                    color: theme ? theme.textMuted : "#878a98"
                                    font.pixelSize: theme ? theme.fontSizeSmall : 11
                                }

                                Text {
                                    visible: selectedPlugin && selectedPlugin.author !== ""
                                    text: selectedPlugin ? selectedPlugin.author : ""
                                    color: theme ? theme.textSecondary : "#a9afbc"
                                    font.pixelSize: theme ? theme.fontSizeSmall : 11
                                    font.family: theme ? theme.fontFamily : "sans-serif"
                                }
                            }
                        }
                    }

                    // Toggle and settings in header
                    Row {
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        spacing: 12
                        visible: selectedPlugin && selectedPlugin.type !== "host"

                        // Toggle (smaller in hero)
                        Rectangle {
                            width: 36
                            height: 20
                            radius: 10
                            color: theme ? theme.accent : "#4a9eff"

                            Rectangle {
                                anchors.verticalCenter: parent.verticalCenter
                                x: parent.width - width - 2
                                width: 16
                                height: 16
                                radius: 8
                                color: "#FFFFFF"
                            }

                            MouseArea {
                                anchors.fill: parent
                                hoverEnabled: true
                                onClicked: console.log("Toggle:", selectedPlugin.id)
                            }
                        }

                        // Settings icon (SVG) - white icon, controlled via opacity
                        Image {
                            width: 18
                            height: 18
                            source: "../../../../app_assets/icons/cog.svg"
                            sourceSize.width: 18
                            sourceSize.height: 18
                            fillMode: Image.PreserveAspectFit
                            opacity: settingsMouse.containsMouse ? 1.0 : 0.7

                            MouseArea {
                                id: settingsMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                onClicked: console.log("Settings:", selectedPlugin.id)
                            }
                        }
                    }
                }

                Rectangle {
                    anchors.bottom: parent.bottom
                    width: parent.width
                    height: 1
                    color: theme ? theme.border : "#464b57"
                }
            }

            // Detail content
            Flickable {
                anchors.top: detailHeader.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                contentHeight: detailColumn.implicitHeight + 32
                clip: true

                Column {
                    id: detailColumn
                    anchors.left: parent.left
                    anchors.right: parent.right
                    spacing: 0

                    // Description (if present)
                    DetailRow {
                        label: "Description"
                        description: selectedPlugin ? selectedPlugin.description : ""
                        visible: selectedPlugin && selectedPlugin.description !== ""
                    }

                    SectionHeader { text: "Info"; visible: selectedPlugin }

                    DetailRow {
                        label: "Windows"
                        value: selectedPlugin ? String(selectedPlugin.windowCount) : "0"
                        visible: selectedPlugin
                    }

                    DetailRow {
                        label: "Settings"
                        value: selectedPlugin ? String(selectedPlugin.settingCount) : "0"
                        visible: selectedPlugin
                    }

                    DetailRow {
                        label: "Dependencies"
                        value: selectedPlugin && selectedPlugin.requires.length > 0
                            ? selectedPlugin.requires.join(", ")
                            : "None"
                        visible: selectedPlugin
                    }

                    // Empty state
                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        y: 100
                        visible: selectedPlugin === null
                        text: "Select a plugin from the list"
                        color: theme ? theme.textMuted : "#878a98"
                        font.pixelSize: theme ? theme.fontSizeBase : 13
                        font.family: theme ? theme.fontFamily : "sans-serif"
                    }
                }
            }
        }

        // ── Divider ─────────────────────────────────────────────────────────
        Rectangle {
            width: 1
            height: parent.height
            color: theme ? theme.border : "#464b57"
        }

        // ── Right pane (30%) ── Plugin list
        Item {
            width: parent.width * 0.30
            height: parent.height

            // List header
            Rectangle {
                id: listHeader
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: parent.right
                height: 32
                color: "transparent"

                Text {
                    anchors.left: parent.left; anchors.leftMargin: 16
                    anchors.verticalCenter: parent.verticalCenter
                    text: "Plugins"
                    color: theme ? theme.text : "#ffffff"
                    font.pixelSize: theme ? theme.fontSizeSmall : 11
                    font.family: theme ? theme.fontFamily : "sans-serif"
                }

                Rectangle {
                    anchors.bottom: parent.bottom
                    width: parent.width
                    height: 1
                    color: theme ? theme.border : "#464b57"
                }
            }

            ListView {
                anchors.top: listHeader.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                clip: true
                spacing: 0
                model: root.inspector ? root.inspector.pluginList : []

                delegate: Column {
                    width: parent.width
                    spacing: 0

                    // Group header (Host / Plugins / Connectors)
                    Rectangle {
                        width: parent.width
                        height: 28
                        color: theme ? theme.surfaceAlt : "#2f343e"

                        Text {
                            anchors.left: parent.left; anchors.leftMargin: 12
                            anchors.verticalCenter: parent.verticalCenter
                            text: modelData.label
                            color: theme ? theme.textSecondary : "#a9afbc"
                            font.pixelSize: theme ? theme.fontSizeSmall : 11
                            font.family: theme ? theme.fontFamily : "sans-serif"
                            font.weight: Font.Medium
                        }

                        Rectangle {
                            anchors.bottom: parent.bottom
                            width: parent.width
                            height: 1
                            color: theme ? theme.border : "#464b57"
                        }
                    }

                    // Plugins in this group — alternating colors starting with dark
                    Repeater {
                        model: modelData.plugins

                        delegate: Rectangle {
                            required property var modelData
                            required property int index

                            readonly property bool isSelected:
                                root.selectedPlugin !== null
                                && root.selectedPlugin.id === modelData.id

                            width: parent.width
                            height: 40
                            // Alternating colors
                            color: index % 2 === 0 ? (theme ? theme.surface : "#17181c") : (theme ? theme.surfaceAlt : "#2f343e")

                            // Selected indicator (accent color)
                            Rectangle {
                                width: 3
                                height: parent.height
                                color: theme ? theme.accent : "#4a9eff"
                                visible: isSelected
                            }

                            // Hover gradient
                            Rectangle {
                                anchors.fill: parent
                                opacity: rowHover.hovered && !isSelected ? 1 : 0
                                Behavior on opacity { NumberAnimation { duration: 120 } }
                                gradient: Gradient {
                                    orientation: Gradient.Horizontal
                                    GradientStop { position: 0.0; color: "transparent" }
                                    GradientStop { position: 0.5; color: "transparent" }
                                    GradientStop { position: 1.0; color: "#20dec184" }
                                }
                            }

                            Rectangle {
                                anchors.bottom: parent.bottom
                                width: parent.width
                                height: 1
                                color: theme ? theme.border : "#464b57"
                                opacity: 0.4
                            }

                            Row {
                                anchors.fill: parent
                                leftPadding: 16
                                rightPadding: 12
                                spacing: 8

                                // Status indicator dot based on plugin state and selection
                                Rectangle {
                                    anchors.verticalCenter: parent.verticalCenter
                                    width: 8
                                    height: 8
                                    radius: 4
                                    color: {
                                        // Selection (orange) has highest priority
                                        if (isSelected) return theme ? theme.warning : "#ff9800"
                                        
                                        // Then check live state from pluginStates, fallback to modelData
                                        var liveState = root.pluginStates[modelData.id]
                                        var state = liveState || modelData.state || "disabled"
                                        if (state === "active") return theme ? theme.success : "#4caf50"
                                        if (state === "enabling" || state === "loading") return theme ? theme.warning : "#ff9800"
                                        if (state === "error") return theme ? theme.danger : "#f44336"
                                        if (state === "unloading") return theme ? theme.warning : "#ff9800"
                                        return theme ? theme.danger : "#f44336"  // disabled
                                    }
                                    
                                    // Pulse animation for loading states
                                    SequentialAnimation on opacity {
                                        running: {
                                            var liveS = root.pluginStates[modelData.id]
                                            var s = liveS || modelData.state || "disabled"
                                            return s === "enabling" || s === "loading" || s === "unloading"
                                        }
                                        loops: Animation.Infinite
                                        NumberAnimation { from: 1.0; to: 0.3; duration: 500 }
                                        NumberAnimation { from: 0.3; to: 1.0; duration: 500 }
                                    }
                                }

                                // Plugin name (bold)
                                Text {
                                    anchors.verticalCenter: parent.verticalCenter
                                    text: modelData.id
                                    color: theme ? theme.text : "#ffffff"
                                    font.pixelSize: theme ? theme.fontSizeBase : 13
                                    font.family: theme ? theme.fontFamily : "sans-serif"
                                    font.weight: Font.DemiBold
                                }

                                // Version
                                Text {
                                    anchors.verticalCenter: parent.verticalCenter
                                    visible: modelData.version !== ""
                                    text: modelData.version
                                    color: theme ? theme.textMuted : "#878a98"
                                    font.pixelSize: theme ? theme.fontSizeSmall : 11
                                    font.family: theme ? theme.fontFamily : "sans-serif"
                                }

                                Item { width: parent.width - 200 }  // Spacer

                                // Toggle switch (not for host)
                                Rectangle {
                                    visible: modelData.type !== "host"
                                    anchors.verticalCenter: parent.verticalCenter
                                    width: 36
                                    height: 20
                                    radius: 10
                                    color: theme ? theme.accent : "#4a9eff"

                                    // White disk/knob
                                    Rectangle {
                                        anchors.verticalCenter: parent.verticalCenter
                                        x: parent.width - width - 2  // Right side = ON
                                        width: 16
                                        height: 16
                                        radius: 8
                                        color: "#FFFFFF"
                                    }

                                    MouseArea {
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        onClicked: {
                                            console.log("Toggle:", modelData.id)
                                        }
                                    }
                                }

                                // Settings icon (SVG) - white icon via opacity
                                Image {
                                    anchors.verticalCenter: parent.verticalCenter
                                    width: 14
                                    height: 14
                                    source: "../../../../app_assets/icons/cog.svg"
                                    sourceSize.width: 14
                                    sourceSize.height: 14
                                    fillMode: Image.PreserveAspectFit
                                    opacity: cogMouse.containsMouse ? 1.0 : 0.6
                                    Behavior on opacity { NumberAnimation { duration: 80 } }

                                    MouseArea {
                                        id: cogMouse
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        onClicked: {
                                            console.log("Settings:", modelData.id)
                                        }
                                    }
                                }
                            }

                            MouseArea {
                                anchors.fill: parent
                                anchors.rightMargin: 80  // Don't trigger when clicking toggle/settings
                                onClicked: {
                                    root.selectedPlugin = modelData
                                    // Mark for activation on panel close (not immediate)
                                    if (modelData.type === "plugin") {
                                        root.pluginToActivate = modelData.id
                                    }
                                }
                            }
                            HoverHandler { id: rowHover }
                        }
                    }
                }
            }
        }
    }

    // ── Components ───────────────────────────────────────────────────────────

    component SectionHeader: Rectangle {
        property string text: ""
        anchors.left: parent ? parent.left : undefined
        anchors.right: parent ? parent.right : undefined
        height: visible ? 28 : 0
        color: theme ? theme.surfaceAlt : "#2f343e"
        visible: text !== ""

        Text {
            anchors.left: parent.left; anchors.leftMargin: 16
            anchors.verticalCenter: parent.verticalCenter
            text: parent.text
            color: theme ? theme.textSecondary : "#a9afbc"
            font.pixelSize: theme ? theme.fontSizeSmall : 11
            font.family: theme ? theme.fontFamily : "sans-serif"
            font.weight: Font.Medium
        }
        Rectangle {
            anchors.bottom: parent.bottom
            width: parent.width
            height: 1
            color: theme ? theme.border : "#464b57"
        }
    }

    component DetailRow: Rectangle {
        property string label: ""
        property string value: ""
        property string description: ""

        anchors.left: parent ? parent.left : undefined
        anchors.right: parent ? parent.right : undefined
        height: visible ? (description !== "" ? 52 : 44) : 0
        color: "transparent"
        visible: true

        Rectangle {
            anchors.fill: parent
            opacity: rowHover.hovered ? 1 : 0
            Behavior on opacity { NumberAnimation { duration: 120 } }
            gradient: Gradient {
                orientation: Gradient.Horizontal
                GradientStop { position: 0.0; color: "transparent" }
                GradientStop { position: 0.5; color: "transparent" }
                GradientStop { position: 1.0; color: "#20dec184" }
            }
        }

        Rectangle {
            anchors.bottom: parent.bottom
            width: parent.width
            height: 1
            color: theme ? theme.border : "#464b57"
            opacity: 0.4
        }

        Column {
            anchors.left: parent.left; anchors.leftMargin: 16
            anchors.right: parent.right; anchors.rightMargin: 16
            anchors.verticalCenter: parent.verticalCenter
            spacing: 3

            Text {
                text: label
                color: theme ? theme.text : "#ffffff"
                font.pixelSize: theme ? theme.fontSizeBase : 13
                font.family: theme ? theme.fontFamily : "sans-serif"
            }
            Text {
                visible: description !== ""
                text: description
                color: rowHover.hovered ? "#dec184" : (theme ? theme.textMuted : "#878a98")
                font.pixelSize: theme ? theme.fontSizeSmall : 11
                font.family: theme ? theme.fontFamily : "sans-serif"
                Behavior on color { ColorAnimation { duration: 120 } }
            }
            Text {
                visible: description === "" && value !== ""
                text: value
                color: theme ? theme.textSecondary : "#a9afbc"
                font.pixelSize: theme ? theme.fontSizeSmall : 11
                font.family: theme ? theme.fontFamily : "sans-serif"
            }
        }

        HoverHandler { id: rowHover }
    }
}
