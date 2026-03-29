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
    color: hostTheme ? hostTheme.surfaceAlt : "#2f343e"

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
        spacing: -1

        Repeater {
            model: root.tabs && root.tabs.length !== undefined ? root.tabs : []

            delegate: Rectangle {
                required property string modelData
                required property int index

                width: Math.max(implicitWidth, tabLabel.implicitWidth + 40)
                implicitWidth: tabLabel.implicitWidth + 40
                height: tabRow.height
                radius: 0
                color: root.currentIndex === index
                    ? (hostTheme ? hostTheme.surface : "#282c33")
                    : (hostTheme ? hostTheme.surfaceAlt : "#2f343e")
                Behavior on color { ColorAnimation { duration: 90 } }

                Rectangle {
                    anchors.left: parent.left
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    width: 1
                    color: hostTheme ? hostTheme.border : "#3a4452"
                    opacity: 1
                }

                Rectangle {
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    width: 1
                    color: hostTheme ? hostTheme.border : "#3a4452"
                    opacity: 1
                }

                Rectangle {
                    anchors.bottom: parent.bottom
                    anchors.left: parent.left
                    anchors.right: parent.right
                    height: 1
                    visible: root.currentIndex !== index
                    color: hostTheme ? hostTheme.border : "#464b57"
                }

                Text {
                    id: tabLabel
                    anchors.centerIn: parent
                    text: modelData
                    color: root.currentIndex === index
                        ? (hostTheme ? hostTheme.text : "#dce0e5")
                        : (hostTheme ? hostTheme.textSecondary : "#a9afbc")
                    font.pixelSize: hostTheme ? hostTheme.fontSizeBase : 13
                    font.weight: Font.Normal
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
