import QtQuick

Rectangle {
    id: root

    property int tabIndex: 0
    property string tabLabel: ""
    property int currentIndex: 0

    signal pressed(int index, string label)

    width: Math.max(96, buttonLabel.implicitWidth + 28)
    height: 36
    radius: 9
    color: root.currentIndex === root.tabIndex ? "#e8edf5" : "transparent"
    border.width: root.currentIndex === root.tabIndex ? 0 : 1
    border.color: "#353c46"

    Text {
        id: buttonLabel
        anchors.centerIn: parent
        text: root.tabLabel
        color: root.currentIndex === root.tabIndex ? "#14171b" : "#c5ccd8"
        font.pixelSize: 14
    }

    MouseArea {
        anchors.fill: parent
        onClicked: root.pressed(root.tabIndex, root.tabLabel)
    }
}
