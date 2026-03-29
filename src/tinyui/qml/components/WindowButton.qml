import QtQuick
import QtQuick.Controls
import QtQuick.Window

AbstractButton {
    id: btn

    readonly property var hostWindow: Window.window
    readonly property var hostTheme: hostWindow && hostWindow.theme ? hostWindow.theme : null

    readonly property color surfaceFloating: hostTheme ? hostTheme.surfaceFloating : "#20242b"
    readonly property color dangerColor: hostTheme ? hostTheme.danger : "#d15b5b"
    readonly property int titleBarHeight: hostTheme ? hostTheme.titleBarHeight : 32

    property string iconSource: ""
    property bool isCloseButton: false

    width: 46
    height: titleBarHeight
    hoverEnabled: true

    background: Rectangle {
        color: btn.hovered
               ? (btn.isCloseButton ? dangerColor : surfaceFloating)
               : "transparent"
    }

    contentItem: Item {
        Image {
            anchors.centerIn: parent
            width: 16
            height: 16
            source: btn.iconSource
            sourceSize.width: width
            sourceSize.height: height
            fillMode: Image.PreserveAspectFit
            smooth: true
        }
    }
}
