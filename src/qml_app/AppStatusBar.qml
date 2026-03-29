import QtQuick

Rectangle {
    id: root

    property string activeLabel: ""
    property var leftItems: []

    height: 32
    color: "#3b414d"

    Rectangle {
        anchors.top: parent.top
        width: parent.width
        height: 1
        color: "#464b57"
    }

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
                color: "transparent"
                width: label.implicitWidth + 16

                Text {
                    id: label
                    anchors.centerIn: parent
                    text: typeof modelData === "string" ? modelData : ""
                    color: "#dce0e5"
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
        color: "transparent"

        Text {
            id: activeText
            anchors.centerIn: parent
            text: root.activeLabel
            color: "#f4f7fb"
            font.pixelSize: 12
        }
    }
}
