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

import "../../../../ui_api/qml" as UiApi
import "HostChromeShell.js" as HostChromeShellBridge

Item {
    id: root

    readonly property var hostWindow: Window.window
    readonly property var theme: hostWindow && hostWindow.theme ? hostWindow.theme : null
    readonly property var appActions: hostWindow && hostWindow.appActions ? hostWindow.appActions : null
    readonly property var windowController: hostWindow && hostWindow.windowController ? hostWindow.windowController : null
    readonly property var runtimeContext: hostWindow && hostWindow.runtimeContext ? hostWindow.runtimeContext : null
    readonly property var uiChrome: runtimeContext && runtimeContext.uiChrome ? runtimeContext.uiChrome : null
    readonly property var imageSources: runtimeContext && runtimeContext.imageSources ? runtimeContext.imageSources : null

    property string windowTitle: hostWindow && typeof hostWindow.windowTitle === "string" ? hostWindow.windowTitle : ""
    property var menuItems: uiChrome ? uiChrome.menuItems : []
    property int currentTab: hostWindow && typeof hostWindow.currentTab === "number" ? hostWindow.currentTab : 0
    property bool showTabBar: hostWindow && typeof hostWindow.showTabBar === "boolean" ? hostWindow.showTabBar : false
    property bool showStatusBar: hostWindow && typeof hostWindow.showStatusBar === "boolean" ? hostWindow.showStatusBar : false
    property var statusItems: uiChrome ? uiChrome.statusItems : []
    property var pluginMenuItems: uiChrome ? uiChrome.pluginMenuItems : []
    property var pluginMenuLabel: uiChrome ? uiChrome.pluginMenuLabel : "Plugins"
    property string statusActiveLabel: uiChrome ? uiChrome.statusActiveLabel : ""
    property bool pluginMenuOpen: false
    property bool menuOpen: false
    property string pendingPluginActivation: ""
    property var pluginStates: ({})
    property bool widgetsVisible: runtimeContext && runtimeContext.widgetVisibility ? runtimeContext.widgetVisibility.globalVisible : true

    Connections {
        target: root.runtimeContext ? root.runtimeContext.pluginState : null
        function onStateDataChanged() {
            if (!root.runtimeContext || !root.runtimeContext.pluginState)
                return;
            root.pluginStates = root.runtimeContext.pluginState.states;
        }
    }

    Connections {
        target: root.runtimeContext && root.runtimeContext.widgetVisibility ? root.runtimeContext.widgetVisibility : null
        function onGlobalVisibleChanged() {
            root.widgetsVisible = root.runtimeContext.widgetVisibility.globalVisible;
        }
    }

    // Base chrome — menu button suppressed so HostChromeShell owns it
    UiApi.AppChromeShell {
        id: baseChrome
        anchors.fill: parent
        externalMenuButton: true
    }

    // Close menus when clicking anywhere outside them
    MouseArea {
        anchors.fill: parent
        enabled: root.menuOpen || root.pluginMenuOpen
        onClicked: {
            root.menuOpen = false;
            root.pluginMenuOpen = false;
        }
        z: 15
    }

    HostMenuButton {
        id: hostMenuButton
        x: 0
        y: 0
        theme: root.theme
        imageSources: root.imageSources
        menuItems: root.menuItems
        windowTitle: root.windowTitle
        open: root.menuOpen
        onOpenRequested: open => root.menuOpen = open
        onTriggerAction: action => {
            if (root.appActions)
                root.appActions.trigger(action);
            else if (action === "close" && root.hostWindow)
                root.hostWindow.close();
        }
    }

    HostPluginMenu {
        id: hostPluginMenu
        x: hostMenuButton.buttonWidth
        y: 0
        theme: root.theme
        pluginMenuItems: root.pluginMenuItems
        pluginMenuLabel: root.pluginMenuLabel
        open: root.pluginMenuOpen
        onOpenRequested: open => root.pluginMenuOpen = open
        onTriggerAction: action => {
            if (root.appActions)
                root.appActions.trigger(action);
        }
    }

    // Plugin panel - fills space including where tabs were
    Loader {
        id: pluginPanelLoader
        anchors.fill: parent
        anchors.topMargin: 32  // Only titlebar, tabs are hidden when panel is open
        anchors.bottomMargin: 32
        visible: root.hostWindow && root.hostWindow.showPluginPanel
        sourceComponent: root.hostWindow && root.hostWindow.showPluginPanel ? root.hostWindow.pluginPanelComponent : null
        z: 30

        onLoaded: {
            if (item && root.hostWindow) {
                // Mirror selected plugin into HostChromeShell so it survives item destruction
                HostChromeShellBridge.connectPluginToActivateChanged(item, function () {
                    root.pendingPluginActivation = HostChromeShellBridge.pluginToActivate(item);
                });
                root.pendingPluginActivation = HostChromeShellBridge.pluginToActivate(item);
            }
        }
    }

    HostStatusBar {
        id: statusBar
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        visible: root.showStatusBar
        theme: root.theme
        statusItems: root.statusItems
        pluginStates: root.pluginStates
        statusActiveLabel: root.statusActiveLabel
        pendingPluginActivation: root.pendingPluginActivation
        widgetsVisible: root.widgetsVisible
        showPluginPanel: root.hostWindow && root.hostWindow.showPluginPanel
        onTriggerAction: action => {
            if (root.appActions)
                root.appActions.trigger(action);
        }
        onActivatePendingPlugin: pluginId => {
            if (root.appActions)
                root.appActions.trigger("plugin.activate:" + pluginId);
        }
        onClearPendingActivation: root.pendingPluginActivation = ""
        onTogglePluginPanel: {
            if (root.appActions)
                root.appActions.trigger("pluginPanel.toggle");
        }
    }
}
