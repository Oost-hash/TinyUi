import QtQuick
import QtQuick.Controls
import TinyUI

AbstractButton {
    id: btn

    property string iconSource: ""
    property bool isCloseButton: false

    width: 46
    height: Theme.titleBarHeight
    hoverEnabled: true

    background: Rectangle {
        color: btn.hovered
               ? (btn.isCloseButton ? Theme.danger : Theme.surfaceFloating)
               : "transparent"
    }

    contentItem: Image {
        source: btn.iconSource
        sourceSize.width: 16
        sourceSize.height: 16
        fillMode: Image.PreserveAspectFit
        smooth: true

        anchors.centerIn: parent
        width: 16
        height: 16
    }
}
