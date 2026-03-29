import QtQuick
import QtQuick.Window

Rectangle {
    id: root

    readonly property var hostWindow: Window.window
    readonly property var hostTheme: hostWindow && hostWindow.theme ? hostWindow.theme : null

    property string text: ""

    readonly property color surfaceAlt: hostTheme ? hostTheme.surfaceAlt : "#2F343E"
    readonly property color borderColor: hostTheme ? hostTheme.border : "#464B57"
    readonly property color textSecondary: hostTheme ? hostTheme.textSecondary : "#A9AFBC"
    readonly property int fontSmall: hostTheme ? hostTheme.fontSizeSmall : 11
    readonly property string fontFamily: hostTheme ? hostTheme.fontFamily : "Segoe UI"

    width: parent ? parent.width : 0
    height: 28
    color: surfaceAlt

    Text {
        anchors.left: parent.left
        anchors.leftMargin: 16
        anchors.verticalCenter: parent.verticalCenter
        text: root.text
        color: textSecondary
        font.pixelSize: fontSmall
        font.family: fontFamily
        font.weight: Font.Medium
    }

    Rectangle {
        anchors.bottom: parent.bottom
        width: parent.width
        height: 1
        color: borderColor
    }
}
