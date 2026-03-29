import QtQuick

Item {
    id: root

    property bool checked: false
    property bool enabled: true

    signal toggled(bool newValue)

    implicitWidth: 40
    implicitHeight: 22

    Rectangle {
        anchors.fill: parent
        radius: height / 2
        color: !root.enabled ? "#2a2f37" : (root.checked ? "#d9e3ef" : "#252b34")
        border.width: 1
        border.color: root.checked ? "#d9e3ef" : "#39414d"

        Rectangle {
            width: 16
            height: 16
            radius: 8
            x: root.checked ? parent.width - width - 3 : 3
            anchors.verticalCenter: parent.verticalCenter
            color: !root.enabled ? "#636b78" : (root.checked ? "#15191e" : "#f4f7fb")

            Behavior on x {
                NumberAnimation {
                    duration: 120
                    easing.type: Easing.OutCubic
                }
            }
        }
    }

    MouseArea {
        anchors.fill: parent
        enabled: root.enabled
        onClicked: root.toggled(!root.checked)
    }
}
