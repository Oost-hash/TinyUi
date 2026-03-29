import QtQuick
import QtQuick.Window

Rectangle {
    id: root

    readonly property var hostWindow: Window.window
    readonly property var hostTheme: hostWindow && hostWindow.theme ? hostWindow.theme : null

    property string label: ""
    property string description: ""
    default property alias rightContent: rightSlot.data

    readonly property color borderColor: hostTheme ? hostTheme.border : "#464B57"
    readonly property color textColor: hostTheme ? hostTheme.text : "#DCE0E5"
    readonly property color textMuted: hostTheme ? hostTheme.textMuted : "#878A98"
    readonly property color warningColor: hostTheme ? hostTheme.warning : "#dec184"
    readonly property int fontBase: hostTheme ? hostTheme.fontSizeBase : 13
    readonly property int fontSmall: hostTheme ? hostTheme.fontSizeSmall : 11
    readonly property string fontFamily: hostTheme ? hostTheme.fontFamily : "Segoe UI"

    width: parent ? parent.width : 0
    implicitHeight: description !== "" ? 46 : 38
    color: "transparent"

    Rectangle {
        anchors.fill: parent
        opacity: editRowHover.hovered ? 1 : 0
        Behavior on opacity { NumberAnimation { duration: 120 } }
        gradient: Gradient {
            orientation: Gradient.Horizontal
            GradientStop { position: 0.0; color: "transparent" }
            GradientStop { position: 0.5; color: "transparent" }
            GradientStop { position: 1.0; color: "#20dec184" }
        }
    }

    Rectangle {
        anchors.bottom: parent.bottom
        width: parent.width
        height: 1
        color: borderColor
        opacity: 0.4
    }

    Column {
        anchors.left: parent.left
        anchors.right: rightSlot.left
        anchors.leftMargin: 16
        anchors.rightMargin: 10
        anchors.verticalCenter: parent.verticalCenter
        spacing: 1

        Text {
            text: root.label
            color: textColor
            font.pixelSize: fontSmall + 1
            font.family: fontFamily
            font.weight: Font.Medium
        }

        Text {
            visible: root.description !== ""
            text: root.description
            color: editRowHover.hovered ? warningColor : textMuted
            font.pixelSize: fontSmall
            font.family: fontFamily
            Behavior on color { ColorAnimation { duration: 120 } }
        }
    }

    Item {
        id: rightSlot
        anchors.right: parent.right
        anchors.rightMargin: 8
        anchors.verticalCenter: parent.verticalCenter
        width: 128
        height: parent.height
    }

    HoverHandler { id: editRowHover }
}
