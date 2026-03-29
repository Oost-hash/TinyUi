import QtQuick

Rectangle {
    id: root

    property string activeLabel: ""
    property var leftItems: []

    height: 34
    radius: 12
    color: "#1b1f25"
    border.width: 1
    border.color: "#2b313a"

    Row {
        anchors.left: parent.left
        anchors.leftMargin: 12
        anchors.verticalCenter: parent.verticalCenter
        spacing: 10

        Repeater {
            model: root.leftItems

            delegate: Rectangle {
                required property var modelData

                height: 22
                radius: 7
                color: "#252b34"
                width: label.implicitWidth + 16

                Text {
                    id: label
                    anchors.centerIn: parent
                    text: typeof modelData === "string" ? modelData : ""
                    color: "#c5ccd8"
                    font.pixelSize: 12
                }
            }
        }
    }

    Rectangle {
        anchors.right: parent.right
        anchors.rightMargin: 10
        anchors.verticalCenter: parent.verticalCenter
        width: activeText.implicitWidth + 20
        height: 22
        radius: 7
        color: "#252b34"

        Text {
            id: activeText
            anchors.centerIn: parent
            text: root.activeLabel
            color: "#f4f7fb"
            font.pixelSize: 12
        }
    }
}
