import QtQuick

Rectangle {
    id: root

    property var widgetData: ({})

    width: 180
    height: 72
    radius: 8
    color: widgetData && widgetData.backgroundColor ? widgetData.backgroundColor : "#CC000000"
    visible: widgetData && widgetData.visible !== undefined ? widgetData.visible : true

    readonly property string labelText: widgetData && widgetData.label ? widgetData.label : ""
    readonly property string sourceText: widgetData && widgetData.source ? widgetData.source : ""
    readonly property string displayText: widgetData && widgetData.displayText ? widgetData.displayText : ""
    readonly property string valueColor: widgetData && widgetData.textColor ? widgetData.textColor : "#E0E0E0"

    Column {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 4

        Text {
            text: root.labelText
            color: "#8F8F8F"
            font.pixelSize: 11
            font.family: "Segoe UI"
        }

        Text {
            text: root.displayText
            color: root.valueColor
            font.pixelSize: 24
            font.bold: true
            font.family: "Segoe UI"
        }

        Text {
            text: root.sourceText
            color: "#6E6E6E"
            font.pixelSize: 10
            font.family: "Segoe UI"
            visible: root.sourceText.length > 0
        }
    }
}
