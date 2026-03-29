import QtQuick
import QtQuick.Window

Rectangle {
    id: root

    readonly property var hostWindow: Window.window
    property string titleText: hostWindow && typeof hostWindow.windowTitle === "string"
                               ? hostWindow.windowTitle
                               : ""
    property var menuItems: []
    property bool nativeChrome: hostWindow && typeof hostWindow.nativeChrome === "boolean"
                                ? hostWindow.nativeChrome
                                : false
    property int windowVisibility: hostWindow ? hostWindow.visibility : Window.Windowed
    property string minimizeIconSource: ""
    property string maximizeIconSource: ""
    property string restoreIconSource: ""
    property string closeIconSource: ""
    property bool showMenuButton: true
    readonly property bool menuOpen: false

    signal closeRequested()
    signal menuClosed()

    function closeMenu() {
        root.menuClosed()
    }

    function toggleMenu() {
    }

    height: 32
    color: "transparent"
}
