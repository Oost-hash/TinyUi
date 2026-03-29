import QtQuick
import QtQuick.Window

Rectangle {
    id: root

    readonly property var hostWindow: Window.window
    property string titleText: hostWindow && typeof hostWindow.windowTitle === "string"
                               ? hostWindow.windowTitle
                               : ""

    height: 32
    color: "transparent"
}
