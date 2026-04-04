import QtQuick
import QtQuick.Window

Window {
    id: root

    property var widgets: []
    readonly property int widgetCount: widgets ? widgets.length : 0

    width: 420
    height: 220
    visible: true
    color: "#101114"
    title: "Widget API Preview"

    Rectangle {
        anchors.fill: parent
        color: "#101114"
    }

    Flow {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12

        Repeater {
            model: root.widgets

            delegate: TextWidget {
                widgetData: modelData
            }
        }
    }
}
