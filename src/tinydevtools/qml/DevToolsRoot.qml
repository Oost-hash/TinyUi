import QtQuick
import QtQuick.Window
import TinyDevTools 1.0

Item {
    id: root

    readonly property var hostWindow: Window.window
    property var tabLabels: hostWindow && Array.isArray(hostWindow.tabLabels)
                            ? hostWindow.tabLabels
                            : ["State", "Runtime", "Console"]
    property int currentTab: hostWindow && typeof hostWindow.currentTab === "number"
                             ? hostWindow.currentTab
                             : 0
    property bool showTabBar: hostWindow && typeof hostWindow.showTabBar === "boolean"
                              ? hostWindow.showTabBar
                              : true
    property bool lazyPanelLoading: hostWindow && typeof hostWindow.lazyPanelLoading === "boolean"
                                    ? hostWindow.lazyPanelLoading
                                    : true
    property var eagerPanelIndexes: hostWindow && Array.isArray(hostWindow.eagerPanelIndexes)
                                     ? hostWindow.eagerPanelIndexes
                                     : []
    property bool loadPanels: hostWindow && typeof hostWindow.loadPanels === "boolean"
                              ? hostWindow.loadPanels
                              : false

    function shouldLoadPanel(index) {
        if (!root.loadPanels)
            return false
        if (!root.lazyPanelLoading)
            return true
        if (index === root.currentTab)
            return true
        return Array.isArray(root.eagerPanelIndexes) && root.eagerPanelIndexes.indexOf(index) >= 0
    }

    anchors.fill: parent

    Rectangle {
        anchors.fill: parent
        color: "#17181c"
    }

    DevToolsStyledTabBar {
        id: tabBar
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.leftMargin: 16
        anchors.rightMargin: 16
        anchors.topMargin: 14
        visible: root.showTabBar
        tabs: Array.isArray(root.tabLabels) ? root.tabLabels : []
        currentIndex: root.currentTab
        onTabSelected: (index) => {
            if (root.hostWindow)
                root.hostWindow.currentTab = index
            else
                root.currentTab = index
        }
    }

    Item {
        id: panelHost
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: tabBar.visible ? tabBar.bottom : parent.top
        anchors.bottom: parent.bottom
        anchors.margins: 16
        anchors.topMargin: tabBar.visible ? 12 : 16

        Loader {
            anchors.fill: parent
            active: root.shouldLoadPanel(0)
            visible: root.currentTab === 0
            sourceComponent: DevToolsStateTab {
                anchors.fill: parent
            }
        }

        Loader {
            anchors.fill: parent
            active: root.shouldLoadPanel(1)
            visible: root.currentTab === 1
            sourceComponent: DevToolsRuntimeTab {
                anchors.fill: parent
            }
        }

        Loader {
            anchors.fill: parent
            active: root.shouldLoadPanel(2)
            visible: root.currentTab === 2
            sourceComponent: ConsolePane {
                anchors.fill: parent
            }
        }
    }
}
