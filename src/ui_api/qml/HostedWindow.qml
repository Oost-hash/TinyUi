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

Window {
    id: root

    property var appActions: null
    property var theme: null
    property var windowController: null
    property var runtimeContext: null
    property var surfaceComponent: null
    property string pluginPanelUrl: ""
    property var pluginPanelComponent: null
    property bool showPluginPanel: false
    property string windowId: ""
    property bool isMainWindow: false
    property string windowTitle: ""
    property var menuItems: []
    property var pluginMenuItems: []
    property string pluginMenuLabel: "Plugins"
    property int currentTab: 0
    property bool showTabBar: false
    property bool showStatusBar: false
    property bool globalShortcutsEnabled: false
    property var statusItems: []
    property string statusActiveLabel: ""
    property string activePluginId: ""
    property var tabModel: []
    property var chromePolicy: ({
            showMenuButton: true,
            showTitleText: true,
            showCaptionButtons: true,
            showStatusLeftItems: true,
            showStatusPluginPicker: true
        })
    property var chromeComponent: null  // Custom chrome component (null = use default)
    width: 960
    height: 640
    minimumWidth: 480
    minimumHeight: 320
    visible: true

    title: windowTitle
    readonly property bool nativeChrome: Qt.platform.os === "linux" || Qt.platform.os === "osx"
    readonly property bool runtimeShowPluginPanel: runtimeContext && runtimeContext.panelState ? runtimeContext.panelState.visible : false
    flags: nativeChrome ? Qt.Window : Qt.Window | Qt.FramelessWindowHint
    color: root.theme ? root.theme.surface : "#17181c"

    function syncRuntimeChrome() {
        var uiChrome = root.runtimeContext ? root.runtimeContext.uiChrome : null;
        var pluginActive = root.runtimeContext ? root.runtimeContext.pluginActive : null;
        root.menuItems = uiChrome ? uiChrome.menuItems : [];
        root.pluginMenuItems = uiChrome ? uiChrome.pluginMenuItems : [];
        root.pluginMenuLabel = uiChrome ? uiChrome.pluginMenuLabel : "Plugins";
        root.statusItems = uiChrome ? uiChrome.statusItems : [];
        root.tabModel = uiChrome ? uiChrome.tabModel : [];
        root.activePluginId = pluginActive ? pluginActive.activePlugin : "";
        root.statusActiveLabel = uiChrome ? uiChrome.statusActiveLabel : root.activePluginId;
    }

    onRuntimeContextChanged: syncRuntimeChrome()
    onRuntimeShowPluginPanelChanged: root.showPluginPanel = root.runtimeShowPluginPanel

    Shortcut {
        enabled: root.globalShortcutsEnabled
        sequence: "F12"
        onActivated: {
            if (root.appActions)
                root.appActions.trigger("open:devtools.main");
        }
    }

    Connections {
        target: root.runtimeContext ? root.runtimeContext.uiChrome : null
        function onMenuItemsChanged() {
            root.menuItems = root.runtimeContext && root.runtimeContext.uiChrome ? root.runtimeContext.uiChrome.menuItems : [];
        }
        function onPluginMenuItemsChanged() {
            root.pluginMenuItems = root.runtimeContext && root.runtimeContext.uiChrome ? root.runtimeContext.uiChrome.pluginMenuItems : [];
            root.pluginMenuLabel = root.runtimeContext && root.runtimeContext.uiChrome ? root.runtimeContext.uiChrome.pluginMenuLabel : "Plugins";
        }
    }

    Connections {
        target: root.runtimeContext ? root.runtimeContext.uiChrome : null
        function onStatusbarItemsChanged() {
            root.statusItems = root.runtimeContext && root.runtimeContext.uiChrome ? root.runtimeContext.uiChrome.statusItems : [];
        }
    }

    Connections {
        target: root.runtimeContext ? root.runtimeContext.pluginActive : null
        function onActivePluginChanged(pluginId) {
            root.activePluginId = pluginId;
            root.statusActiveLabel = pluginId;
        }
    }

    Connections {
        target: root.runtimeContext ? root.runtimeContext.uiChrome : null
        function onTabModelChanged() {
            root.tabModel = root.runtimeContext && root.runtimeContext.uiChrome ? root.runtimeContext.uiChrome.tabModel : [];
        }
    }

    // Chrome loader - uses custom chrome if provided, otherwise default AppChromeShell
    Loader {
        id: chromeLoader
        anchors.fill: parent
        sourceComponent: root.chromeComponent ? root.chromeComponent : defaultChromeComponent
    }

    Component {
        id: defaultChromeComponent
        AppChromeShell {}
    }
}
