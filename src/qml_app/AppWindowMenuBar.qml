import QtQuick
import QtQuick.Window

Rectangle {
    id: root

    readonly property var hostWindow: Window.window
    property string titleText: hostWindow && typeof hostWindow.windowTitle === "string"
                               ? hostWindow.windowTitle
                               : ""

    height: 32
    color: "#3b414d"

    Rectangle {
        anchors.bottom: parent.bottom
        width: parent.width
        height: 1
        color: "#464b57"
    }

    Rectangle {
        id: menuChip
        anchors.left: parent.left
        anchors.leftMargin: 0
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        width: menuRow.width + 24
        color: "transparent"
    }

    Row {
        id: menuRow
        anchors.left: menuChip.left
        anchors.leftMargin: 12
        anchors.verticalCenter: parent.verticalCenter
        spacing: 8

        Text {
            text: "\u2261"
            color: "#a9afbc"
            font.pixelSize: 13
        }

        Text {
            text: root.titleText
            color: "#dce0e5"
            font.pixelSize: 12
            font.weight: Font.Medium
        }
    }
}
