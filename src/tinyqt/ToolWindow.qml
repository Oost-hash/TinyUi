import QtQuick
import QtQuick.Window

Window {
    id: root

    property string windowTitle: "Tool Window"
    property var tabLabels: []
    property int currentTab: 0
    property bool showTabBar: true
    property bool lazyPanelLoading: true
    property var eagerPanelIndexes: []
    property bool loadPanels: false

    width: 960
    height: 640
    minimumWidth: 640
    minimumHeight: 420
    visible: true
    title: root.windowTitle
    color: "#17181c"
    readonly property bool nativeChrome: Qt.platform.os === "linux" || Qt.platform.os === "osx"
    flags: nativeChrome ? Qt.Window : Qt.Window
}
