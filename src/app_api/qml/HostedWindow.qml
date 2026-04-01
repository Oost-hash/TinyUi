import QtQuick
import QtQuick.Window

Window {
    id: root

    property var hostActions: null
    property var theme: null
    property var windowController: null
    property var surfaceComponent: null
    property string windowTitle: ""
    property var menuItems: []
    property var pluginMenuItems: []
    property var tabLabels: []
    property int currentTab: 0
    property bool showTabBar: false
    property bool showStatusBar: false
    property bool globalShortcutsEnabled: false
    property var statusItems: []
    property string statusActiveLabel: ""
    property var inspector: null
    property var chromePolicy: ({
        showMenuButton: true,
        showTitleText: true,
        showCaptionButtons: true,
        showStatusLeftItems: true,
        showStatusPluginPicker: true
    })
    width: 960
    height: 640
    minimumWidth: 480
    minimumHeight: 320
    visible: true

    title: windowTitle
    readonly property bool nativeChrome: Qt.platform.os === "linux" || Qt.platform.os === "osx"
    flags: nativeChrome ? Qt.Window : Qt.Window | Qt.FramelessWindowHint
    color: root.theme ? root.theme.surface : "#17181c"

    Shortcut {
        enabled: root.globalShortcutsEnabled
        sequence: "F12"
        onActivated: {
            if (root.hostActions)
                root.hostActions.trigger("open:devtools.main")
        }
    }

    AppChromeShell {
        anchors.fill: parent
    }
}
