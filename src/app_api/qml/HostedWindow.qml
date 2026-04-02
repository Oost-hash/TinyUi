import QtQuick
import QtQuick.Window

Window {
    id: root

    property var hostActions: null
    property var theme: null
    property var windowController: null
    property var surfaceComponent: null
    property string pluginPanelUrl: ""
    property var pluginPanelComponent: null
    property bool showPluginPanel: false
    property var hostRuntime: null  // Reference to runtime bridge
    property string windowTitle: ""
    property var menuItems: []
    property var pluginMenuItems: []
    property string pluginMenuLabel: "Plugins"
    property var tabLabels: []
    property int currentTab: 0
    property bool showTabBar: false
    property bool showStatusBar: false
    property bool globalShortcutsEnabled: false
    property var statusItems: []
    property string statusActiveLabel: ""
    property string activePluginId: ""
    property var inspector: null
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

    // Sync all properties when hostRuntime changes (initial sync + updates)
    onHostRuntimeChanged: {
        if (hostRuntime) {
            root.menuItems = hostRuntime.menuItems
            root.pluginMenuItems = hostRuntime.pluginMenuItems
            root.pluginMenuLabel = hostRuntime.pluginMenuLabel
            root.tabModel = hostRuntime.tabModel
            root.statusItems = hostRuntime.statusbarLeftItems
            root.activePluginId = hostRuntime.activePlugin
            root.statusActiveLabel = hostRuntime.activePlugin  // For statusbar plugin picker
        }
    }

    Shortcut {
        enabled: root.globalShortcutsEnabled
        sequence: "F12"
        onActivated: {
            if (root.hostActions)
                root.hostActions.trigger("open:devtools.main")
        }
    }
    
    // Connect runtime signals - update properties when bridge emits signals
    Connections {
        target: root.hostRuntime
        function onActivePluginChanged(pluginId) {
            root.activePluginId = pluginId
            root.statusActiveLabel = pluginId
        }
        function onTabModelChanged() {
            root.tabModel = root.hostRuntime ? root.hostRuntime.tabModel : []
        }
        function onMenuItemsChanged() {
            root.menuItems = root.hostRuntime ? root.hostRuntime.menuItems : []
        }
        function onPluginMenuItemsChanged() {
            root.pluginMenuItems = root.hostRuntime ? root.hostRuntime.pluginMenuItems : []
            root.pluginMenuLabel = root.hostRuntime ? root.hostRuntime.pluginMenuLabel : ""
        }
        function onStatusbarItemsChanged() {
            root.statusItems = root.hostRuntime ? root.hostRuntime.statusbarLeftItems : []
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
