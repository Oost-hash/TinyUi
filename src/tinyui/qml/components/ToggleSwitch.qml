import QtQuick
import QtQuick.Window

Item {
    id: root

    readonly property var hostWindow: Window.window
    readonly property var hostTheme: hostWindow && hostWindow.theme ? hostWindow.theme : null

    property bool checked: false
    property bool enabled: true

    readonly property color accentColor: hostTheme ? hostTheme.accent : "#74ADE8"
    readonly property color surfaceFloating: hostTheme ? hostTheme.surfaceFloating : "#20242b"
    readonly property color borderColor: hostTheme ? hostTheme.border : "#464B57"

    signal toggled(bool newValue)

    implicitWidth: 34
    implicitHeight: 18

    Rectangle {
        anchors.fill: parent
        radius: 9
        color: !root.enabled ? surfaceFloating : (root.checked ? accentColor : surfaceFloating)
        border.width: 1
        border.color: !root.enabled ? borderColor : (root.checked ? "transparent" : borderColor)
        Behavior on color { ColorAnimation { duration: 140 } }
        Behavior on border.color { ColorAnimation { duration: 140 } }

        Rectangle {
            anchors.verticalCenter: parent.verticalCenter
            x: root.checked ? parent.width - width - 2 : 2
            width: 14
            height: 14
            radius: 7
            color: "#FFFFFF"
            opacity: root.enabled ? 1.0 : 0.5
            Behavior on x { NumberAnimation { duration: 140; easing.type: Easing.OutCubic } }
        }
    }

    MouseArea {
        anchors.fill: parent
        enabled: root.enabled
        onClicked: root.toggled(!root.checked)
    }
}
