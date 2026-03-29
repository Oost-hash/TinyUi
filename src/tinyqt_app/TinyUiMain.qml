import QtQuick
import QtQuick.Window
import TinyUI 1.0

Window {
    id: root
    property var theme: null
    property string windowTitle: "TinyUI"
    property var tabLabels: ["Widgets"]
    property int currentTab: 0
    property bool showTabBar: true
    property bool showStatusBar: true
    property var statusItems: ["LMU", "Overlay", "F12 DevTools"]
    property string statusActiveLabel: "demo"
    property var widgetEditorItems: []
    property bool devToolsAvailable: false
    property var devToolsController: null
    property bool settingsAvailable: false
    property var settingsController: null
    property var chromePolicy: ({
        showMenuButton: true,
        showTitleText: true,
        showCaptionButtons: true,
        showStatusLeftItems: true,
        showStatusPluginPicker: true
    })

    width: 900
    height: 600
    minimumWidth: 480
    minimumHeight: 320
    visible: true

    title: windowTitle
    readonly property bool nativeChrome: Qt.platform.os === "linux" || Qt.platform.os === "osx"
    flags: nativeChrome ? Qt.Window : Qt.Window | Qt.FramelessWindowHint
    color: root.theme ? root.theme.surface : "#17181c"

    function toggleDevTools() {
        if (!root.devToolsAvailable || !root.devToolsController)
            return
        root.devToolsController.toggle()
    }

    function toggleSettings() {
        if (!root.settingsAvailable || !root.settingsController)
            return
        root.settingsController.toggle()
    }

    Shortcut {
        sequence: "F12"
        onActivated: root.toggleDevTools()
    }

    Shortcut {
        sequence: "Ctrl+,"
        onActivated: root.toggleSettings()
    }

    AppWindowMenuBar {
        x: 0
        y: 0
        width: root.width
        settingsController: root.settingsController
        devToolsController: root.devToolsController
        chromePolicy: root.chromePolicy
    }

    Item {
        x: 0
        y: 32
        width: root.width
        height: root.height - 32

        AppStyledTabBar {
            id: tabBar
            x: 0
            y: 0
            width: parent.width
            visible: root.showTabBar
            tabs: root.tabLabels
            currentIndex: root.currentTab
            onTabSelected: (index) => root.currentTab = index
        }

        Item {
            id: contentPane
            x: 0
            y: root.showTabBar ? tabBar.y + tabBar.height : 0
            width: parent.width
            height: parent.height - y - (statusBar.visible ? statusBar.height : 0)

            WidgetTab {
                anchors.fill: parent
                sectionTitle: "Widgets"
                widgetItems: root.widgetEditorItems
            }
        }

        AppStatusBar {
            id: statusBar
            visible: root.showStatusBar
            x: 0
            y: parent.height - height
            width: parent.width
            leftItems: root.statusItems
            activeLabel: root.statusActiveLabel
            chromePolicy: root.chromePolicy
        }
    }
}
