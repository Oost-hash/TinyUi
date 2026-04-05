import QtQuick
import QtQuick.Window

Window {
    id: root

    property var appActions: null
    property var theme: null
    property var windowController: null
    property var surfaceComponent: null
    property string pluginPanelUrl: ""
    property var pluginPanelComponent: null
    property bool showPluginPanel: false
    property var menus: null
    property var statusbar: null
    property var pluginSelection: null
    property var pluginSelectionActions: null
    property var pluginState: null
    property var pluginStateWrite: null
    property var pluginRead: null
    property var settingsRead: null
    property var settingsWrite: null
    property var widgetRead: null
    property var tabs: null
    property var connectorRead: null
    property var connectorActions: null
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
    flags: nativeChrome ? Qt.Window : Qt.Window | Qt.FramelessWindowHint
    color: root.theme ? root.theme.surface : "#17181c"

    // Sync menu properties when menu model changes
    onMenusChanged: {
        if (menus) {
            root.menuItems = menus.menuItems
            root.pluginMenuItems = menus.pluginMenuItems
            root.pluginMenuLabel = menus.pluginMenuLabel
        }
    }

    // Sync statusbar properties when statusbar model changes
    onStatusbarChanged: {
        if (statusbar) {
            root.statusItems = statusbar.leftItems
        }
    }

    // Sync active plugin properties when plugin selection changes
    onPluginSelectionChanged: {
        if (pluginSelection) {
            root.activePluginId = pluginSelection.activePlugin
            root.statusActiveLabel = pluginSelection.activePlugin
        }
    }

    // Sync tab properties when tabs API changes
    onTabsChanged: {
        if (tabs) {
            root.tabModel = tabs.tabModel
        }
    }

    Shortcut {
        enabled: root.globalShortcutsEnabled
        sequence: "F12"
        onActivated: {
            if (root.appActions)
                root.appActions.trigger("open:devtools.main")
        }
    }
    
    Connections {
        target: root.menus
        function onMenuItemsChanged() {
            root.menuItems = root.menus ? root.menus.menuItems : []
        }
        function onPluginMenuItemsChanged() {
            root.pluginMenuItems = root.menus ? root.menus.pluginMenuItems : []
            root.pluginMenuLabel = root.menus ? root.menus.pluginMenuLabel : ""
        }
    }

    Connections {
        target: root.statusbar
        function onStatusbarItemsChanged() {
            root.statusItems = root.statusbar ? root.statusbar.leftItems : []
        }
    }

    Connections {
        target: root.pluginSelection
        function onActivePluginChanged(pluginId) {
            root.activePluginId = pluginId
            root.statusActiveLabel = pluginId
        }
    }

    Connections {
        target: root.tabs
        function onTabModelChanged() {
            root.tabModel = root.tabs ? root.tabs.tabModel : []
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
