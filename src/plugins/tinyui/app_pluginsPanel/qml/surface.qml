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
    property var theme: hostWindow && hostWindow.theme ? hostWindow.theme : null
    property var pluginGroups: []
    
    property var appActions: hostWindow && hostWindow.appActions ? hostWindow.appActions : null
    property var selectedPlugin: null
    property string pluginToActivate: ""  // Plugin waiting to be activated on close
    readonly property bool selectedPluginHasIcon: root.selectedPlugin && root.selectedPlugin.iconUrl !== ""
    
    // Track plugin states locally for live updates
    property var pluginStates: ({})  // Map pluginId -> state

    // Listen to state changes from runtime
    Connections {
        target: root.hostWindow ? root.hostWindow.pluginState : null
        function onPluginStateChanged(pluginId, state) {
            root.pluginStates[pluginId] = state
            // Force update
            var temp = root.pluginStates
            root.pluginStates = {}
            root.pluginStates = temp
        }
        function onStateDataChanged() {
            if (!root.hostWindow || !root.hostWindow.pluginState)
                return
            root.pluginStates = root.hostWindow.pluginState.states
        }
    }

    Connections {
        target: root.pluginRead
        function onPluginsChanged() {
            root.pluginGroups = root.buildPluginGroups()
        }
    }

    function buildPluginGroups() : var {
        var groups = [
            { "type": "host", "label": "Host", "plugins": [] },
            { "type": "plugin", "label": "Plugins", "plugins": [] },
            { "type": "connector", "label": "Connectors", "plugins": [] }
        ]
        var plugins = pluginRead ? pluginRead.plugins : []
        for (var i = 0; i < plugins.length; i++) {
            var plugin = plugins[i]
            for (var j = 0; j < groups.length; j++) {
                if (groups[j].type === plugin.type) {
                    groups[j].plugins.push(plugin)
                    break
                }
            }
        }
        return groups
    }

    // Check if a connector is used by the active plugin
    function isConnectorUsed(connectorId: string) : bool {
        if (!hostWindow || !hostWindow.activePluginId || !pluginRead) return false
        
        // Find the active plugin
        for (var i = 0; i < pluginGroups.length; i++) {
            var group = pluginGroups[i]
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

    function isConnectorPending(connectorId: string) : bool {
        if (!root.pluginToActivate || !pluginRead) return false

        for (var i = 0; i < pluginGroups.length; i++) {
            var group = pluginGroups[i]
            for (var j = 0; j < group.plugins.length; j++) {
                var plugin = group.plugins[j]
                if (plugin.id === root.pluginToActivate) {
                    return plugin.requires && plugin.requires.indexOf(connectorId) >= 0
                }
            }
        }
        return false
    }

    function isOutgoingPlugin(pluginId: string) : bool {
        return root.pluginToActivate !== ""
            && root.hostWindow
            && root.hostWindow.activePluginId === pluginId
            && root.pluginToActivate !== pluginId
    }

    anchors.fill: parent
    color: theme ? theme.surface : "#17181c"

    // Select active plugin when panel opens
    Component.onCompleted: {
        if (hostWindow && hostWindow.pluginState) {
            root.pluginStates = hostWindow.pluginState.states
        }
        root.pluginGroups = root.buildPluginGroups()
        if (hostWindow && hostWindow.activePluginId && pluginRead) {
            // Find the active plugin in the list
            for (var i = 0; i < pluginGroups.length; i++) {
                var group = pluginGroups[i]
                for (var j = 0; j < group.plugins.length; j++) {
                    if (group.plugins[j].id === hostWindow.activePluginId) {
                        selectedPlugin = group.plugins[j]
                        pluginToActivate = ""
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
                height: root.selectedPlugin ? 152 : 0
                visible: height > 0
                color: root.theme ? Qt.rgba(0, 0, 0, 0.2) : "#121316"

                Item {
                    anchors.fill: parent
                    anchors.leftMargin: 20
                    anchors.rightMargin: 20

                    Row {
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.rightMargin: 140
                        anchors.verticalCenter: parent.verticalCenter
                        spacing: root.selectedPluginHasIcon ? 8 : 0

                        Item {
                            width: root.selectedPluginHasIcon ? 128 : 0
                            height: root.selectedPluginHasIcon ? 128 : 0
                            visible: root.selectedPluginHasIcon

                            Image {
                                anchors.fill: parent
                                source: root.selectedPlugin ? root.selectedPlugin.iconUrl : ""
                                sourceSize.width: width
                                sourceSize.height: height
                                fillMode: Image.PreserveAspectFit
                                smooth: true
                                horizontalAlignment: Image.AlignLeft
                                verticalAlignment: Image.AlignVCenter
                            }
                        }

                        Column {
                            id: heroInfoColumn
                            width: parent.width - (root.selectedPluginHasIcon ? 136 : 0)
                            anchors.verticalCenter: parent.verticalCenter
                            spacing: 8

                            Text {
                                text: root.selectedPlugin ? root.selectedPlugin.id : ""
                                color: root.theme ? root.theme.text : "#ffffff"
                                font.pixelSize: 24
                                font.family: root.theme ? root.theme.fontFamily : "sans-serif"
                                font.weight: Font.Bold
                                elide: Text.ElideRight
                                width: parent.width
                            }

                            Row {
                                id: heroMetaRow
                                spacing: 8

                                Text {
                                    id: heroVersionText
                                    visible: root.selectedPlugin && root.selectedPlugin.version !== ""
                                    text: root.selectedPlugin ? "v" + root.selectedPlugin.version : ""
                                    color: root.theme ? root.theme.accent : "#4a9eff"
                                    font.pixelSize: root.theme ? root.theme.fontSizeSmall : 11
                                    font.family: root.theme ? root.theme.fontFamily : "sans-serif"
                                }

                                Text {
                                    id: heroAuthorDot
                                    visible: root.selectedPlugin && root.selectedPlugin.author !== ""
                                    text: "\u2022"
                                    color: root.theme ? root.theme.textMuted : "#878a98"
                                    font.pixelSize: root.theme ? root.theme.fontSizeSmall : 11
                                }

                                Text {
                                    id: heroAuthorText
                                    visible: root.selectedPlugin && root.selectedPlugin.author !== ""
                                    text: root.selectedPlugin ? root.selectedPlugin.author : ""
                                    color: root.theme ? root.theme.textSecondary : "#a9afbc"
                                    font.pixelSize: root.theme ? root.theme.fontSizeSmall : 11
                                    font.family: root.theme ? root.theme.fontFamily : "sans-serif"
                                    elide: Text.ElideRight
                                    width: Math.max(
                                        0,
                                        heroInfoColumn.width
                                        - (heroVersionText.visible ? heroVersionText.implicitWidth : 0)
                                        - (heroAuthorDot.visible ? heroAuthorDot.implicitWidth : 0)
                                        - 24
                                    )
                                }
                            }

                            Text {
                                visible: root.selectedPlugin && root.selectedPlugin.description !== ""
                                text: root.selectedPlugin ? root.selectedPlugin.description : ""
                                color: root.theme ? root.theme.textSecondary : "#a9afbc"
                                font.pixelSize: root.theme ? root.theme.fontSizeBase : 13
                                font.family: root.theme ? root.theme.fontFamily : "sans-serif"
                                wrapMode: Text.WordWrap
                                width: parent.width
                                maximumLineCount: 2
                                elide: Text.ElideRight
                            }
                        }
                    }

                    // Toggle and settings in header
                    Row {
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        spacing: 12
                        visible: root.selectedPlugin && root.selectedPlugin.type !== "host"

                        // Toggle (smaller in hero)
                        Rectangle {
                            width: 28
                            height: 16
                            radius: 8
                            color: root.theme ? root.theme.accent : "#4a9eff"

                            Rectangle {
                                anchors.verticalCenter: parent.verticalCenter
                                x: parent.width - width - 2
                                width: 12
                                height: 12
                                radius: 6
                                color: "#FFFFFF"
                            }

                            MouseArea {
                                anchors.fill: parent
                                hoverEnabled: true
                                onClicked: console.log("Toggle:", root.selectedPlugin.id)
                            }
                        }

                        // Settings icon (SVG) - white icon, controlled via opacity
                        Image {
                            width: 18
                            height: 18
                            source: "../../assets/images/ui/cog.svg"
                            sourceSize.width: 18
                            sourceSize.height: 18
                            fillMode: Image.PreserveAspectFit
                            opacity: settingsMouse.containsMouse ? 1.0 : 0.7

                            MouseArea {
                                id: settingsMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                onClicked: console.log("Settings:", root.selectedPlugin.id)
                            }
                        }
                    }
                }

                Rectangle {
                    anchors.bottom: parent.bottom
                    width: parent.width
                    height: 1
                    color: root.theme ? root.theme.border : "#464b57"
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
                        description: root.selectedPlugin ? root.selectedPlugin.description : ""
                        visible: false
                    }

                    SectionHeader { text: "Info"; visible: root.selectedPlugin }

                    DetailRow {
                        label: "Windows"
                        value: root.selectedPlugin ? String(root.selectedPlugin.windowCount) : "0"
                        visible: root.selectedPlugin
                    }

                    DetailRow {
                        label: "Settings"
                        value: root.selectedPlugin ? String(root.selectedPlugin.settingCount) : "0"
                        visible: root.selectedPlugin
                    }

                    DetailRow {
                        label: "Dependencies"
                        value: root.selectedPlugin && root.selectedPlugin.requires.length > 0
                            ? root.selectedPlugin.requires.join(", ")
                            : "None"
                        visible: root.selectedPlugin
                    }

                    // Empty state
                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        y: 100
                        visible: root.selectedPlugin === null
                        text: "Select a plugin from the list"
                        color: root.theme ? root.theme.textMuted : "#878a98"
                        font.pixelSize: root.theme ? root.theme.fontSizeBase : 13
                        font.family: root.theme ? root.theme.fontFamily : "sans-serif"
                    }
                }
            }
        }

        // ── Divider ─────────────────────────────────────────────────────────
        Rectangle {
            width: 1
            height: parent.height
            color: root.theme ? root.theme.border : "#464b57"
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
                    color: root.theme ? root.theme.text : "#ffffff"
                    font.pixelSize: root.theme ? root.theme.fontSizeSmall : 11
                    font.family: root.theme ? root.theme.fontFamily : "sans-serif"
                }

                Rectangle {
                    anchors.bottom: parent.bottom
                    width: parent.width
                    height: 1
                    color: root.theme ? root.theme.border : "#464b57"
                }
            }

            ListView {
                anchors.top: listHeader.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: pendingActivationFooter.visible ? pendingActivationFooter.top : parent.bottom
                clip: true
                spacing: 0
                model: root.pluginGroups

                delegate: Column {
                    id: pluginGroupDelegate
                    required property var modelData
                    width: parent.width
                    spacing: 0

                    // Group header (Host / Plugins / Connectors)
                    Rectangle {
                        width: parent.width
                        height: 28
                        color: root.theme ? root.theme.surfaceAlt : "#2f343e"

                        Text {
                            anchors.left: parent.left; anchors.leftMargin: 12
                            anchors.verticalCenter: parent.verticalCenter
                            text: pluginGroupDelegate.modelData.label
                            color: root.theme ? root.theme.textSecondary : "#a9afbc"
                            font.pixelSize: root.theme ? root.theme.fontSizeSmall : 11
                            font.family: root.theme ? root.theme.fontFamily : "sans-serif"
                            font.weight: Font.Medium
                        }

                        Rectangle {
                            anchors.bottom: parent.bottom
                            width: parent.width
                            height: 1
                            color: root.theme ? root.theme.border : "#464b57"
                        }
                    }

                    // Plugins in this group — alternating colors starting with dark
                    Repeater {
                        model: pluginGroupDelegate.modelData.plugins

                        delegate: Rectangle {
                            id: pluginRowDelegate
                            required property var modelData
                            required property int index

                            readonly property bool isSelected:
                                root.selectedPlugin !== null
                                && root.selectedPlugin.id === pluginRowDelegate.modelData.id
                            readonly property bool isPendingActivation:
                                root.pluginToActivate !== ""
                                && root.pluginToActivate === pluginRowDelegate.modelData.id
                            readonly property bool isPendingConnector:
                                pluginRowDelegate.modelData.type === "connector"
                                && root.isConnectorPending(pluginRowDelegate.modelData.id)
                            readonly property bool isOutgoingActivation:
                                pluginRowDelegate.modelData.type === "plugin"
                                && root.isOutgoingPlugin(pluginRowDelegate.modelData.id)

                            width: parent.width
                            height: 40
                            // Alternating colors
                            color: pluginRowDelegate.index % 2 === 0
                                ? (root.theme ? root.theme.surface : "#17181c")
                                : (root.theme ? root.theme.surfaceAlt : "#2f343e")

                            // Selected indicator (accent color)
                            Rectangle {
                                width: 3
                                height: parent.height
                                color: pluginRowDelegate.isOutgoingActivation
                                    ? (root.theme ? root.theme.warningAlt : "#B05CFF")
                                    : ((pluginRowDelegate.isPendingActivation || pluginRowDelegate.isPendingConnector)
                                        ? (root.theme ? root.theme.warning : "#ff9800")
                                        : (root.theme ? root.theme.accent : "#4a9eff"))
                                visible: pluginRowDelegate.isSelected
                            }

                            // Hover gradient
                            Rectangle {
                                anchors.fill: parent
                                opacity: rowHover.hovered && !pluginRowDelegate.isSelected ? 1 : 0
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
                                color: root.theme ? root.theme.border : "#464b57"
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
                                        // Pending activation takes precedence until the panel closes
                                        if (pluginRowDelegate.isOutgoingActivation) return root.theme ? root.theme.warningAlt : "#B05CFF"
                                        if (pluginRowDelegate.isPendingActivation || pluginRowDelegate.isPendingConnector) return root.theme ? root.theme.warning : "#ff9800"
                                        
                                        // Then check live state from pluginStates, fallback to modelData
                                        var liveState = root.pluginStates[pluginRowDelegate.modelData.id]
                                        var state = liveState || pluginRowDelegate.modelData.state || "disabled"
                                        if (state === "active") return root.theme ? root.theme.success : "#4caf50"
                                        if (state === "enabling" || state === "loading") return root.theme ? root.theme.warning : "#ff9800"
                                        if (state === "error") return root.theme ? root.theme.danger : "#f44336"
                                        if (state === "unloading") return root.theme ? root.theme.warningAlt : "#B05CFF"
                                        return root.theme ? root.theme.danger : "#f44336"  // disabled
                                    }
                                    
                                    // Pulse animation for loading states
                                    SequentialAnimation on opacity {
                                        running: {
                                            var liveS = root.pluginStates[pluginRowDelegate.modelData.id]
                                            var s = liveS || pluginRowDelegate.modelData.state || "disabled"
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
                                    text: pluginRowDelegate.modelData.id
                                    color: root.theme ? root.theme.text : "#ffffff"
                                    font.pixelSize: root.theme ? root.theme.fontSizeBase : 13
                                    font.family: root.theme ? root.theme.fontFamily : "sans-serif"
                                    font.weight: Font.DemiBold
                                }

                                // Version
                                Text {
                                    anchors.verticalCenter: parent.verticalCenter
                                    visible: pluginRowDelegate.modelData.version !== ""
                                    text: pluginRowDelegate.modelData.version
                                    color: root.theme ? root.theme.textMuted : "#878a98"
                                    font.pixelSize: root.theme ? root.theme.fontSizeSmall : 11
                                    font.family: root.theme ? root.theme.fontFamily : "sans-serif"
                                }

                                Item { width: parent.width - 200 }  // Spacer that pushes right items to edge

                                // Toggle switch (not for host)
                                Rectangle {
                                    visible: pluginRowDelegate.modelData.type !== "host"
                                    anchors.verticalCenter: parent.verticalCenter
                                    width: 28
                                    height: 16
                                    radius: 8
                                    color: root.theme ? root.theme.accent : "#4a9eff"

                                    // White disk/knob
                                    Rectangle {
                                        anchors.verticalCenter: parent.verticalCenter
                                        x: parent.width - width - 2  // Right side = ON
                                        width: 12
                                        height: 12
                                        radius: 6
                                        color: "#FFFFFF"
                                    }

                                    MouseArea {
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        onClicked: {
                                            console.log("Toggle:", pluginRowDelegate.modelData.id)
                                        }
                                    }
                                }

                                // Settings icon (SVG) - white icon via opacity
                                Image {
                                    anchors.verticalCenter: parent.verticalCenter
                                    width: 14
                                    height: 14
                                    source: "../../assets/images/ui/cog.svg"
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
                                            console.log("Settings:", pluginRowDelegate.modelData.id)
                                        }
                                    }
                                }
                            }

                            MouseArea {
                                anchors.fill: parent
                                anchors.rightMargin: 80  // Don't trigger when clicking toggle/settings
                                onClicked: {
                                    root.selectedPlugin = pluginRowDelegate.modelData
                                    if (pluginRowDelegate.modelData.type === "plugin") {
                                        root.pluginToActivate = pluginRowDelegate.modelData.id !== root.hostWindow.activePluginId
                                            ? pluginRowDelegate.modelData.id
                                            : ""
                                    } else {
                                        root.pluginToActivate = ""
                                    }
                                }
                            }
                            HoverHandler { id: rowHover }
                        }
                    }
                }
            }

            Rectangle {
                id: pendingActivationFooter
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                height: 30
                visible: root.pluginToActivate !== ""
                color: root.theme ? root.theme.surfaceAlt : "#2f343e"

                Rectangle {
                    anchors.top: parent.top
                    width: parent.width
                    height: 1
                    color: root.theme ? root.theme.border : "#464b57"
                }

                Text {
                    anchors.left: parent.left
                    anchors.leftMargin: 16
                    anchors.verticalCenter: parent.verticalCenter
                    text: "Close to load plugin"
                    color: root.theme ? root.theme.warning : "#ff9800"
                    font.pixelSize: root.theme ? root.theme.fontSizeSmall : 11
                    font.family: root.theme ? root.theme.fontFamily : "sans-serif"
                    font.weight: Font.Medium
                }
            }
        }
    }

    // ── Components ───────────────────────────────────────────────────────────

            component SectionHeader: Rectangle {
        id: sectionHeaderRoot
        property string text: ""
        anchors.left: parent ? parent.left : undefined
        anchors.right: parent ? parent.right : undefined
        height: visible ? 28 : 0
        color: root.theme ? root.theme.surfaceAlt : "#2f343e"
        visible: text !== ""

        Text {
            anchors.left: parent.left; anchors.leftMargin: 16
            anchors.verticalCenter: parent.verticalCenter
            text: parent.text
            color: root.theme ? root.theme.textSecondary : "#a9afbc"
            font.pixelSize: root.theme ? root.theme.fontSizeSmall : 11
            font.family: root.theme ? root.theme.fontFamily : "sans-serif"
            font.weight: Font.Medium
        }
        Rectangle {
            anchors.bottom: parent.bottom
            width: parent.width
            height: 1
            color: root.theme ? root.theme.border : "#464b57"
        }
    }

    component DetailRow: Rectangle {
        id: detailRowRoot
        property string label: ""
        property string value: ""
        property string description: ""
        property bool heroStyle: false

        anchors.left: parent ? parent.left : undefined
        anchors.right: parent ? parent.right : undefined
        height: visible ? (heroStyle ? 58 : (description !== "" ? 52 : 44)) : 0
        color: heroStyle
            ? (root.theme ? Qt.rgba(0, 0, 0, 0.2) : "#121316")
            : "transparent"
        visible: true

        Rectangle {
            anchors.fill: parent
            visible: !detailRowRoot.heroStyle
            opacity: detailRowHover.hovered ? 1 : 0
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
            color: root.theme ? root.theme.border : "#464b57"
            opacity: 0.4
        }

        Column {
            anchors.left: parent.left; anchors.leftMargin: 16
            anchors.right: parent.right; anchors.rightMargin: 16
            anchors.verticalCenter: parent.verticalCenter
            spacing: 3

            Text {
                visible: !detailRowRoot.heroStyle
                text: detailRowRoot.label
                color: root.theme ? root.theme.text : "#ffffff"
                font.pixelSize: root.theme ? root.theme.fontSizeBase : 13
                font.family: root.theme ? root.theme.fontFamily : "sans-serif"
            }
            Text {
                visible: detailRowRoot.description !== ""
                text: detailRowRoot.description
                color: detailRowRoot.heroStyle
                    ? (root.theme ? root.theme.textSecondary : "#a9afbc")
                    : (detailRowHover.hovered ? "#dec184" : (root.theme ? root.theme.textMuted : "#878a98"))
                font.pixelSize: detailRowRoot.heroStyle
                    ? (root.theme ? root.theme.fontSizeBase : 13)
                    : (root.theme ? root.theme.fontSizeSmall : 11)
                font.family: root.theme ? root.theme.fontFamily : "sans-serif"
                Behavior on color { ColorAnimation { duration: 120 } }
                wrapMode: Text.WordWrap
            }
            Text {
                visible: detailRowRoot.description === "" && detailRowRoot.value !== ""
                text: detailRowRoot.value
                color: root.theme ? root.theme.textSecondary : "#a9afbc"
                font.pixelSize: root.theme ? root.theme.fontSizeSmall : 11
                font.family: root.theme ? root.theme.fontFamily : "sans-serif"
            }
        }

        HoverHandler { id: detailRowHover }
    }
}
