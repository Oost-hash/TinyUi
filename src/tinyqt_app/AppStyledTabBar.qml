import QtQuick
import QtQuick.Window

Rectangle {
    id: root
    readonly property var hostWindow: Window.window
    readonly property var hostTheme: hostWindow && hostWindow.theme ? hostWindow.theme : null

    property var tabs: []
    property int currentIndex: 0

    signal tabSelected(int index, string label)

    implicitHeight: 42
    height: implicitHeight
    color: hostTheme ? hostTheme.surfaceAlt : "#242a33"

    Rectangle {
        anchors.bottom: parent.bottom
        width: parent.width
        height: 1
        color: hostTheme ? hostTheme.border : "#3a4452"
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
        anchors.leftMargin: 0
        anchors.rightMargin: 0
        spacing: -1

        Repeater {
            model: Array.isArray(root.tabs) ? root.tabs : []

            delegate: Rectangle {
                required property string modelData
                required property int index

                width: Math.max(104, tabLabel.implicitWidth + 40)
                height: tabRow.height
                color: root.currentIndex === index
                    ? (hostTheme ? hostTheme.surface : "#17181c")
                    : (hostTheme ? hostTheme.surfaceAlt : "#242a33")
                Behavior on color { ColorAnimation { duration: 90 } }

                Rectangle {
                    anchors.left: parent.left
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    width: 1
                    color: hostTheme ? hostTheme.border : "#3a4452"
                }

                Rectangle {
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    width: 1
                    color: hostTheme ? hostTheme.border : "#3a4452"
                }

                Rectangle {
                    anchors.bottom: parent.bottom
                    anchors.left: parent.left
                    anchors.right: parent.right
                    height: 1
                    color: root.currentIndex === index
                        ? (hostTheme ? hostTheme.surface : "#17181c")
                        : (hostTheme ? hostTheme.border : "#3a4452")
                }

                Text {
                    id: tabLabel
                    anchors.centerIn: parent
                    text: modelData
                    color: root.currentIndex === index
                        ? (hostTheme ? hostTheme.text : "#e6edf5")
                        : (hostTheme ? hostTheme.textSecondary : "#aeb8c6")
                    font.pixelSize: hostTheme ? hostTheme.fontSizeBase : 13
                    font.weight: root.currentIndex === index ? Font.DemiBold : Font.Normal
                    Behavior on color { ColorAnimation { duration: 90 } }
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
