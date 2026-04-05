import QtQuick
import QtQuick.Window

Window {
    id: root

    property var widgetData: ({})

    width: 180
    height: 72
    visible: widgetData && widgetData.visible !== undefined ? widgetData.visible : true
    color: "transparent"
    flags: Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
    title: widgetData && widgetData.widgetId ? widgetData.widgetId : "widget"

    TextWidget {
        anchors.fill: parent
        widgetData: root.widgetData
    }
}
