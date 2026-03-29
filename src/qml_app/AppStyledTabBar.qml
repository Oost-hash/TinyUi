import QtQuick

Rectangle {
    id: root

    property var tabs: []
    property int currentIndex: 0

    signal tabSelected(int index, string label)

    implicitHeight: 42
    color: "#2f343e"

    Rectangle {
        anchors.bottom: parent.bottom
        width: parent.width
        height: 1
        color: "#464b57"
    }

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
        anchors.leftMargin: 4
        anchors.rightMargin: 4
        spacing: 0

        Repeater {
            model: Array.isArray(root.tabs) ? root.tabs : []

            delegate: Rectangle {
                required property string modelData
                required property int index

                width: Math.max(96, tabLabel.implicitWidth + 28)
                height: tabRow.height
                color: root.currentIndex === index ? "#3b414d" : "transparent"

                Text {
                    id: tabLabel
                    anchors.centerIn: parent
                    text: modelData
                    color: root.currentIndex === index ? "#74ade8" : "#dce0e5"
                    font.pixelSize: 12
                    font.weight: root.currentIndex === index ? Font.DemiBold : Font.Normal
                }

                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: root.selectTab(index)
                }
            }
        }
    }
}
