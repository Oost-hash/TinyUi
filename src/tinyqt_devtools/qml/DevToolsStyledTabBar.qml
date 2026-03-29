import QtQuick

Rectangle {
    id: root

    property var tabs: []
    property int currentIndex: 0

    signal tabSelected(int index, string label)

    implicitHeight: 44
    radius: 12
    color: "#1e2228"
    border.width: 1
    border.color: "#2b313a"

    function labelAt(index) {
        return index >= 0 && index < tabs.length && typeof tabs[index] === "string" ? tabs[index] : ""
    }

    function selectTab(index) {
        const label = root.labelAt(index)
        if (label === "")
            return
        root.currentIndex = index
        root.tabSelected(index, label)
    }

    Row {
        id: tabRow
        anchors.fill: parent
        anchors.margins: 4
        spacing: 4

        Repeater {
            model: Array.isArray(root.tabs) ? root.tabs : []

            delegate: Rectangle {
                required property string modelData
                required property int index

                width: Math.max(96, tabLabel.implicitWidth + 28)
                height: tabRow.height
                radius: 9
                color: root.currentIndex === index ? "#e8edf5" : "transparent"
                border.width: root.currentIndex === index ? 0 : 1
                border.color: "#353c46"

                Text {
                    id: tabLabel
                    anchors.centerIn: parent
                    text: modelData
                    color: root.currentIndex === index ? "#14171b" : "#c5ccd8"
                    font.pixelSize: 14
                }

                MouseArea {
                    anchors.fill: parent
                    onClicked: root.selectTab(index)
                }
            }
        }
    }
}
