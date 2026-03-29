import QtQuick
import QtQuick.Window
import TinyUI 1.0

Rectangle {
    id: root

    readonly property var hostWindow: Window.window
    readonly property var hostTheme: hostWindow && hostWindow.theme ? hostWindow.theme : null
    property string titleText: hostWindow && typeof hostWindow.windowTitle === "string"
                               ? hostWindow.windowTitle
                               : ""
    property bool menuOpen: false
    readonly property url menuIconSource: Qt.resolvedUrl("../tinyui/assets/icons/" + (root.menuOpen ? "menu-open.svg" : "menu.svg"))
    readonly property url minimizeIconSource: Qt.resolvedUrl("../tinyui/assets/icons/window-minimize.svg")
    readonly property url maximizeIconSource: Qt.resolvedUrl("../tinyui/assets/icons/window-maximize.svg")
    readonly property url restoreIconSource: Qt.resolvedUrl("../tinyui/assets/icons/window-restore.svg")
    readonly property url closeIconSource: Qt.resolvedUrl("../tinyui/assets/icons/window-close.svg")

    height: 32
    color: hostTheme ? hostTheme.surfaceRaised : "#3b414d"

    DragHandler {
        target: null
        onActiveChanged: if (active) WindowController.startMove()
    }

    Rectangle {
        anchors.bottom: parent.bottom
        width: parent.width
        height: 1
        color: hostTheme ? hostTheme.border : "#464b57"
    }

    Rectangle {
        id: menuButton
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        width: menuRow.width + 24
        color: menuArea.containsMouse || root.menuOpen
            ? (hostTheme ? hostTheme.surfaceAlt : "#2f343e")
            : "transparent"

        MouseArea {
            id: menuArea
            anchors.fill: parent
            hoverEnabled: true
            onClicked: root.menuOpen = !root.menuOpen
        }
    }

    Row {
        id: menuRow
        anchors.left: menuButton.left
        anchors.leftMargin: 12
        anchors.verticalCenter: parent.verticalCenter
        spacing: 10

        Image {
            anchors.verticalCenter: parent.verticalCenter
            source: root.menuIconSource
            sourceSize.width: 18
            sourceSize.height: 18
            width: 18
            height: 18
            smooth: true
        }

        Text {
            text: root.titleText
            color: hostTheme ? hostTheme.textMuted : "#878a98"
            font.pixelSize: 12
            font.weight: Font.Medium
        }
    }

    Item {
        id: menuDropdown
        z: 20
        x: 0
        y: root.height
        width: 164
        height: menuColumn.implicitHeight
        visible: root.menuOpen

        Rectangle {
            anchors.fill: parent
            color: hostTheme ? hostTheme.surfaceAlt : "#2f343e"
            border.width: 1
            border.color: hostTheme ? hostTheme.border : "#464b57"
        }

        Column {
            id: menuColumn
            width: parent.width
            spacing: 0

            Repeater {
                model: [
                    { "label": "Settings", "action": "settings" },
                    { "label": "Dev Tools", "action": "devtools", "visible": hostWindow && hostWindow.devToolsAvailable },
                    { "label": "Close", "action": "close" }
                ]

                delegate: Rectangle {
                    required property var modelData
                    visible: modelData.visible === undefined ? true : !!modelData.visible
                    width: parent.width
                    height: visible ? 28 : 0
                    color: menuItemMouse.containsMouse
                        ? (hostTheme ? hostTheme.surfaceRaised : "#3b414d")
                        : "transparent"

                    Text {
                        anchors.left: parent.left
                        anchors.leftMargin: 12
                        anchors.verticalCenter: parent.verticalCenter
                        text: modelData.label
                        color: hostTheme ? hostTheme.text : "#dce0e5"
                        font.pixelSize: hostTheme ? hostTheme.fontSizeSmall : 11
                    }

                    MouseArea {
                        id: menuItemMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: {
                            root.menuOpen = false
                            if (!hostWindow)
                                return
                            if (modelData.action === "settings" && hostWindow.settingsController)
                                hostWindow.settingsController.toggle()
                            else if (modelData.action === "devtools" && hostWindow.devToolsController)
                                hostWindow.devToolsController.toggle()
                            else if (modelData.action === "close")
                                hostWindow.close()
                        }
                    }
                }
            }
        }
    }

    MouseArea {
        anchors.fill: parent
        visible: root.menuOpen
        z: -1
        propagateComposedEvents: true
        acceptedButtons: Qt.AllButtons
        onPressed: (mouse) => {
            if (mouse.x > menuDropdown.width || mouse.y > root.height + menuDropdown.height) {
                root.menuOpen = false
                mouse.accepted = false
            }
        }
    }

    Row {
        visible: hostWindow && !hostWindow.nativeChrome
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        spacing: 0

        WindowButton {
            iconSource: root.minimizeIconSource
            onClicked: WindowController.minimize()
        }

        WindowButton {
            iconSource: hostWindow && hostWindow.visibility === Window.Maximized
                ? root.restoreIconSource
                : root.maximizeIconSource
            onClicked: WindowController.toggleMaximize()
        }

        WindowButton {
            iconSource: root.closeIconSource
            isCloseButton: true
            onClicked: hostWindow.close()
        }
    }
}
