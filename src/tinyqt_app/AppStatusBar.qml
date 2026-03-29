import QtQuick
import QtQuick.Window
import TinyUI 1.0

Rectangle {
    id: root
    readonly property var hostWindow: Window.window
    readonly property var hostTheme: hostWindow && hostWindow.theme ? hostWindow.theme : null

    property string activeLabel: ""
    property var leftItems: []
    readonly property var statusBarController: hostWindow && hostWindow.statusBarController ? hostWindow.statusBarController : null
    readonly property var pluginNames: hostWindow && hostWindow.pluginNames ? hostWindow.pluginNames : []
    property bool pluginOpen: statusBarController ? statusBarController.pluginDropdownOpen : false

    height: 32
    color: hostTheme ? hostTheme.surfaceRaised : "#3b414d"

    Rectangle {
        anchors.top: parent.top
        width: parent.width
        height: 1
        color: hostTheme ? hostTheme.border : "#464b57"
    }

    Row {
        anchors.left: parent.left
        anchors.leftMargin: 4
        anchors.verticalCenter: parent.verticalCenter
        spacing: 0

        Repeater {
            model: root.leftItems

            delegate: Item {
                required property var modelData
                width: 28
                height: parent.height

                Rectangle {
                    anchors.fill: parent
                    color: leftMouse.containsMouse
                        ? (hostTheme ? hostTheme.surfaceFloating : "#20242b")
                        : "transparent"
                }

                StatusBarIconButton {
                    anchors.fill: parent
                    iconText: typeof modelData === "string" && modelData.length > 0 ? modelData.charAt(0).toUpperCase() : ""
                }

                MouseArea {
                    id: leftMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: {
                        if (hostWindow && hostWindow.settingsController)
                            hostWindow.settingsController.toggle()
                    }
                }
            }
        }
    }

    Rectangle {
        id: pluginButton
        anchors.right: parent.right
        anchors.rightMargin: 10
        anchors.verticalCenter: parent.verticalCenter
        width: activeText.implicitWidth + 20
        height: 22
        color: root.pluginOpen
            ? (hostTheme ? hostTheme.surfaceAlt : "#2f343e")
            : pluginMouse.containsMouse
                ? (hostTheme ? hostTheme.surfaceFloating : "#20242b")
                : "transparent"
        border.width: root.pluginOpen ? 1 : 0
        border.color: hostTheme ? hostTheme.border : "#464b57"

        Text {
            id: activeText
            anchors.centerIn: parent
            text: root.activeLabel
            color: hostTheme ? hostTheme.text : "#f4f7fb"
            font.pixelSize: 12
        }

        MouseArea {
            id: pluginMouse
            anchors.fill: parent
            hoverEnabled: true
            onClicked: {
                if (statusBarController)
                    statusBarController.togglePluginDropdown()
            }
        }
    }

    Item {
        id: pluginDropdown
        z: 10
        width: Math.max(pluginButton.width, 140)
        height: dropdownColumn.implicitHeight
        x: pluginButton.x + pluginButton.width - width
        y: -height
        visible: root.pluginOpen

        Rectangle { anchors.fill: parent; color: hostTheme ? hostTheme.surfaceAlt : "#2f343e" }
        Rectangle { anchors.left: parent.left; width: 1; height: parent.height; color: hostTheme ? hostTheme.border : "#464b57" }
        Rectangle { anchors.top: parent.top; width: parent.width; height: 1; color: hostTheme ? hostTheme.border : "#464b57" }
        Rectangle { anchors.right: parent.right; width: 1; height: parent.height; color: hostTheme ? hostTheme.border : "#464b57" }

        Column {
            id: dropdownColumn
            width: parent.width
            spacing: 0

            Repeater {
                model: root.pluginNames

                delegate: Rectangle {
                    required property var modelData
                    required property int index

                    width: pluginDropdown.width
                    height: 28
                    color: pluginItemMouse.containsMouse
                        ? (hostTheme ? hostTheme.surfaceRaised : "#3b414d")
                        : "transparent"

                    Text {
                        anchors.left: parent.left
                        anchors.leftMargin: 12
                        anchors.verticalCenter: parent.verticalCenter
                        text: typeof modelData === "string" ? modelData : ""
                        color: statusBarController && statusBarController.activePluginIndex === index
                            ? (hostTheme ? hostTheme.accent : "#74ADE8")
                            : (hostTheme ? hostTheme.text : "#dce0e5")
                        font.pixelSize: hostTheme ? hostTheme.fontSizeSmall : 11
                        font.weight: statusBarController && statusBarController.activePluginIndex === index ? Font.DemiBold : Font.Normal
                    }

                    MouseArea {
                        id: pluginItemMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: {
                            if (statusBarController)
                                statusBarController.selectPlugin(index)
                        }
                    }
                }
            }
        }
    }
}
