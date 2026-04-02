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
import QtQuick.Layouts

import "../../../../app_api/qml" as AppApi

Item {
    id: root

    readonly property var hostWindow: Window.window
    readonly property var theme: hostWindow && hostWindow.theme ? hostWindow.theme : null
    readonly property var hostActions: hostWindow && hostWindow.hostActions ? hostWindow.hostActions : null
    readonly property var windowController: hostWindow && hostWindow.windowController ? hostWindow.windowController : null

    property string windowTitle: hostWindow && typeof hostWindow.windowTitle === "string" ? hostWindow.windowTitle : ""
    property var menuItems: hostWindow && hostWindow.menuItems ? hostWindow.menuItems : []
    property var tabLabels: hostWindow && hostWindow.tabLabels ? hostWindow.tabLabels : []
    property int currentTab: hostWindow && typeof hostWindow.currentTab === "number" ? hostWindow.currentTab : 0
    property bool showTabBar: hostWindow && typeof hostWindow.showTabBar === "boolean" ? hostWindow.showTabBar : false
    property bool showStatusBar: hostWindow && typeof hostWindow.showStatusBar === "boolean" ? hostWindow.showStatusBar : false
    property var statusItems: hostWindow && hostWindow.statusItems ? hostWindow.statusItems : []
    property var pluginMenuItems: hostWindow && hostWindow.pluginMenuItems ? hostWindow.pluginMenuItems : []
    property var pluginMenuLabel: hostWindow && hostWindow.pluginMenuLabel ? hostWindow.pluginMenuLabel : "Plugins"
    property string statusActiveLabel: hostWindow && typeof hostWindow.statusActiveLabel === "string" ? hostWindow.statusActiveLabel : ""
    property bool pluginMenuOpen: false

    readonly property url menuIconSource: Qt.resolvedUrl("../../../../app_assets/icons/" + (baseChrome.menuOpen ? "menu-open.svg" : "menu.svg"))

    // Base chrome
    AppApi.AppChromeShell {
        id: baseChrome
        anchors.fill: parent
    }

    // Plugin menu button
    Rectangle {
        visible: root.pluginMenuItems.length > 0
        x: 100
        y: 0
        width: pluginMenuLabelText.implicitWidth + 24
        height: 32
        color: pluginMenuMouse.containsMouse || root.pluginMenuOpen
            ? (root.theme ? root.theme.surfaceAlt : "#2f343e")
            : "transparent"
        z: 25

        Text {
            id: pluginMenuLabelText
            anchors.centerIn: parent
            text: root.pluginMenuLabel || "Plugins"
            color: pluginMenuMouse.containsMouse || root.pluginMenuOpen
                ? "#FFFFFF"
                : (root.theme ? root.theme.textMuted : "#878a98")
            font.pixelSize: 12
        }

        MouseArea {
            id: pluginMenuMouse
            anchors.fill: parent
            hoverEnabled: true
            onClicked: root.pluginMenuOpen = !root.pluginMenuOpen
        }
    }

    // Plugin menu dropdown
    Item {
        z: 40
        x: 100
        y: 32
        width: 160
        height: pluginMenuColumn.implicitHeight
        visible: root.pluginMenuOpen && root.pluginMenuItems.length > 0

        Rectangle { anchors.fill: parent; color: root.theme ? root.theme.surfaceAlt : "#2f343e" }
        Rectangle { anchors.left: parent.left; width: 1; height: parent.height; color: root.theme ? root.theme.border : "#464b57" }
        Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: root.theme ? root.theme.border : "#464b57" }
        Rectangle { anchors.right: parent.right; width: 1; height: parent.height; color: root.theme ? root.theme.border : "#464b57" }

        Column {
            id: pluginMenuColumn
            width: parent.width
            spacing: 0

            Repeater {
                model: root.pluginMenuItems

                delegate: Rectangle {
                    required property var modelData
                    visible: modelData.visible === undefined ? true : !!modelData.visible
                    width: 160
                    height: visible ? (modelData.separator ? 9 : 28) : 0
                    color: pluginItemMouse.containsMouse
                        ? (root.theme ? root.theme.surfaceRaised : "#3b414d")
                        : "transparent"

                    Rectangle {
                        visible: !!modelData.separator
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.leftMargin: 8
                        anchors.rightMargin: 8
                        height: 1
                        color: root.theme ? root.theme.border : "#464b57"
                    }

                    Text {
                        visible: !modelData.separator
                        anchors.left: parent.left
                        anchors.leftMargin: 12
                        anchors.verticalCenter: parent.verticalCenter
                        text: modelData.label
                        color: root.theme ? root.theme.text : "#dce0e5"
                        font.pixelSize: root.theme ? root.theme.fontSizeSmall : 11
                    }

                    MouseArea {
                        id: pluginItemMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        enabled: !modelData.separator
                        onClicked: {
                            root.pluginMenuOpen = false
                            if (root.hostActions)
                                root.hostActions.trigger(modelData.action)
                        }
                    }
                }
            }
        }
    }

    // Plugin panel
    Loader {
        id: pluginPanelLoader
        anchors.fill: parent
        anchors.topMargin: 74
        anchors.bottomMargin: 32
        visible: hostWindow && hostWindow.showPluginPanel
        sourceComponent: hostWindow && hostWindow.showPluginPanel 
            ? hostWindow.pluginPanelComponent 
            : null
        z: 30
        
        onLoaded: {
            if (item && hostWindow) {
                // Connect immediate activation (for backwards compatibility)
                item.requestActivatePlugin.connect(function(pluginId) {
                    if (hostWindow.hostRuntime) {
                        hostWindow.hostRuntime.setActivePlugin(pluginId)
                    }
                })
            }
        }
    }
    
    // Notify panel when it's being closed (to trigger delayed activation)
    Connections {
        target: hostWindow
        function onShowPluginPanelChanged() {
            if (!hostWindow.showPluginPanel && pluginPanelLoader.item) {
                // Panel is closing - trigger activation
                pluginPanelLoader.item.onPanelClosing()
            }
        }
    }

    // Statusbar with plugin picker
    Rectangle {
        id: statusBar
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        height: 32
        visible: root.showStatusBar
        color: root.theme ? root.theme.surfaceRaised : "#3b414d"
        z: 20

        Rectangle {
            anchors.top: parent.top
            width: parent.width
            height: 1
            color: root.theme ? root.theme.border : "#464b57"
        }

        // Left status items
        Row {
            anchors.left: parent.left
            anchors.leftMargin: 6
            anchors.verticalCenter: parent.verticalCenter
            spacing: 6

            Repeater {
                model: root.statusItems

                delegate: Rectangle {
                    required property var modelData
                    width: Math.max(label.implicitWidth + 12, 24)
                    height: 20
                    radius: 3
                    color: itemMouse.containsMouse
                        ? (root.theme ? root.theme.surfaceFloating : "#20242b")
                        : "transparent"

                    Text {
                        id: label
                        anchors.centerIn: parent
                        text: typeof modelData === "string" ? modelData : ""
                        color: root.theme ? root.theme.textMuted : "#c8ccd4"
                        font.pixelSize: root.theme ? root.theme.fontSizeSmall : 11
                    }

                    MouseArea {
                        id: itemMouse
                        anchors.fill: parent
                        hoverEnabled: true
                    }
                }
            }
        }

        // Plugin picker
        Item {
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            width: pluginNameRow.width + 20
            visible: root.statusActiveLabel !== ""

            Rectangle {
                anchors.fill: parent
                color: hostWindow && hostWindow.showPluginPanel 
                       ? (root.theme ? root.theme.surfaceAlt : "#2f343e")
                       : pluginNameHover.containsMouse 
                         ? (root.theme ? root.theme.surfaceFloating : "#20242b") 
                         : "transparent"
            }
            
            Rectangle { 
                visible: hostWindow && hostWindow.showPluginPanel
                anchors.left: parent.left
                width: 1
                height: parent.height
                color: root.theme ? root.theme.border : "#464b57"
            }
            Rectangle { 
                visible: hostWindow && hostWindow.showPluginPanel
                anchors.right: parent.right
                width: 1
                height: parent.height
                color: root.theme ? root.theme.border : "#464b57"
            }

            Row {
                id: pluginNameRow
                anchors.centerIn: parent
                spacing: 0

                Text {
                    anchors.verticalCenter: parent.verticalCenter
                    text: root.statusActiveLabel
                    color: "#FFFFFF"
                    font.pixelSize: root.theme ? root.theme.fontSizeSmall : 11
                    font.family: root.theme ? root.theme.fontFamily : "sans-serif"
                }
            }

            MouseArea {
                id: pluginNameHover
                anchors.fill: parent
                hoverEnabled: true
                onClicked: {
                    if (hostWindow)
                        hostWindow.showPluginPanel = !hostWindow.showPluginPanel
                }
            }
        }
    }
}
