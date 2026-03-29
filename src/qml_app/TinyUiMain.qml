import QtQuick
import QtQuick.Window
import TinyQt 1.0
import TinyUI 1.0

Window {
    id: root
    property string windowTitle: "TinyUI"
    property var tabLabels: ["Widgets"]
    property int currentTab: 0
    property bool showTabBar: true
    property bool showStatusBar: true
    property var statusItems: ["LMU", "Overlay", "F12 DevTools"]
    property string statusActiveLabel: "demo"
    property bool devToolsAvailable: false
    property var devToolsController: null

    width: 900
    height: 600
    minimumWidth: 480
    minimumHeight: 320
    visible: true

    title: windowTitle
    readonly property bool nativeChrome: Qt.platform.os === "linux" || Qt.platform.os === "osx"
    flags: nativeChrome ? Qt.Window : Qt.Window | Qt.FramelessWindowHint
    color: "#17181c"

    function toggleDevTools() {
        if (!root.devToolsAvailable || !root.devToolsController)
            return
        root.devToolsController.toggle()
    }

    Shortcut {
        sequence: "F12"
        onActivated: root.toggleDevTools()
    }

    WindowMenuBar {
        x: 0
        y: 0
        width: root.width
    }

    Rectangle {
        x: 0
        y: 32
        width: root.width
        height: root.height - 32
        color: "#17181c"

        StyledTabBar {
            id: tabBar
            x: 24
            y: 24
            width: parent.width - 48
            visible: root.showTabBar
            tabs: root.tabLabels
            currentIndex: root.currentTab
            onTabSelected: (index) => root.currentTab = index
        }

        Rectangle {
            x: 24
            y: root.showTabBar ? tabBar.y + tabBar.height + 18 : 24
            width: parent.width - 48
            height: parent.height - y - (root.showStatusBar ? 58 : 24)
            color: "transparent"

            WidgetTab {
                anchors.fill: parent
                sectionTitle: "Widgets"
                widgetItems: [
                    {
                        "title": "Speed",
                        "description": "Speed widget.",
                        "enabled": true,
                        "value": 132,
                        "label": "SPD",
                        "positionX": 96,
                        "positionY": 42,
                        "flashBelow": 80,
                        "thresholds": [
                            { "value": 60, "color": "#ff5252", "flash": true, "flashTarget": "value", "flashSpeed": 6 },
                            { "value": 120, "color": "#f4b400", "flash": false, "flashTarget": "text", "flashSpeed": 4 },
                            { "value": 180, "color": "#34a853", "flash": false, "flashTarget": "widget", "flashSpeed": 4 }
                        ]
                    },
                    {
                        "title": "Fuel",
                        "description": "Fuel widget.",
                        "enabled": false,
                        "value": 41,
                        "label": "FUEL",
                        "positionX": 124,
                        "positionY": 84,
                        "flashBelow": 15,
                        "thresholds": [
                            { "value": 10, "color": "#ff5252", "flash": true, "flashTarget": "widget", "flashSpeed": 8 },
                            { "value": 25, "color": "#f4b400", "flash": false, "flashTarget": "value", "flashSpeed": 4 }
                        ]
                    },
                    {
                        "title": "Tyres",
                        "description": "Tyre widget.",
                        "enabled": true,
                        "value": 87,
                        "label": "TYRES",
                        "positionX": 188,
                        "positionY": 136,
                        "flashBelow": -1,
                        "thresholds": []
                    }
                ]
            }
        }

        StatusBar {
            visible: root.showStatusBar
            x: 24
            y: parent.height - height - 16
            width: parent.width - 48
            leftItems: root.statusItems
            activeLabel: root.statusActiveLabel
        }
    }
}
