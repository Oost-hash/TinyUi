import QtQuick
import QtQuick.Window
import "../tinyqt_main/qml/components" as MainComponents

Rectangle {
    id: root

    readonly property var hostWindow: Window.window
    readonly property var hostTheme: hostWindow && hostWindow.theme ? hostWindow.theme : null
    property var settingsController: hostWindow && hostWindow.settingsController ? hostWindow.settingsController : null
    property var devToolsController: hostWindow && hostWindow.devToolsController ? hostWindow.devToolsController : null
    property var chromePolicy: hostWindow && hostWindow.chromePolicy ? hostWindow.chromePolicy : ({
        showMenuButton: true,
        showTitleText: true,
        showCaptionButtons: true
    })
    property string titleText: hostWindow && typeof hostWindow.windowTitle === "string"
                               ? hostWindow.windowTitle
                               : ""
    property bool menuOpen: false
    readonly property var menuItems: hostWindow && hostWindow.menuItems ? hostWindow.menuItems : [
        { "label": "Settings", "action": "settings", "separator": false, "visible": true },
        { "label": "Dev Tools", "action": "devtools", "separator": false, "visible": hostWindow && hostWindow.devToolsAvailable },
        { "label": "", "action": null, "separator": true, "visible": true },
        { "label": "Close", "action": "close", "separator": false, "visible": true }
    ]
    readonly property url menuIconSource: Qt.resolvedUrl("../assets/icons/" + (root.menuOpen ? "menu-open.svg" : "menu.svg"))
    readonly property url minimizeIconSource: Qt.resolvedUrl("../assets/icons/window-minimize.svg")
    readonly property url maximizeIconSource: Qt.resolvedUrl("../assets/icons/window-maximize.svg")
    readonly property url restoreIconSource: Qt.resolvedUrl("../assets/icons/window-restore.svg")
    readonly property url closeIconSource: Qt.resolvedUrl("../assets/icons/window-close.svg")

    height: 32
    z: 20
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
        visible: !!root.chromePolicy.showMenuButton
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        width: menuRow.width + 28
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
            visible: !!root.chromePolicy.showMenuButton
            anchors.verticalCenter: parent.verticalCenter
            source: root.menuIconSource
            sourceSize.width: 18
            sourceSize.height: 18
            width: 18
            height: 18
            smooth: true
        }

        Text {
            visible: !!root.chromePolicy.showTitleText
            text: root.titleText
            color: menuArea.containsMouse || root.menuOpen
                ? "#FFFFFF"
                : (hostTheme ? hostTheme.textMuted : "#878a98")
            font.pixelSize: 12
            font.weight: Font.Medium
        }
    }

    Item {
        id: menuDropdown
        z: 10
        x: 0
        y: root.height
        width: 160
        height: menuColumn.implicitHeight
        visible: !!root.chromePolicy.showMenuButton && root.menuOpen

        Rectangle { anchors.fill: parent; color: hostTheme ? hostTheme.surfaceAlt : "#2f343e" }
        Rectangle { anchors.left: parent.left; width: 1; height: parent.height; color: hostTheme ? hostTheme.border : "#464b57" }
        Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: hostTheme ? hostTheme.border : "#464b57" }
        Rectangle { anchors.right: parent.right; width: 1; height: parent.height; color: hostTheme ? hostTheme.border : "#464b57" }

        Column {
            id: menuColumn
            width: parent.width
            spacing: 0

            Repeater {
                model: root.menuItems

                delegate: Rectangle {
                    required property var modelData
                    visible: modelData.visible === undefined ? true : !!modelData.visible
                    width: menuDropdown.width
                    height: visible ? (modelData.separator ? 9 : 28) : 0
                    color: menuItemMouse.containsMouse
                        ? (hostTheme ? hostTheme.surfaceRaised : "#3b414d")
                        : "transparent"

                    Rectangle {
                        visible: !!modelData.separator
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.leftMargin: 8
                        anchors.rightMargin: 8
                        height: 1
                        color: hostTheme ? hostTheme.border : "#464b57"
                    }

                    Text {
                        visible: !modelData.separator
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
                        enabled: !modelData.separator
                        onClicked: {
                            root.menuOpen = false
                            if (!hostWindow)
                                return
                            if (modelData.action === "settings" && root.settingsController)
                                root.settingsController.toggle()
                            else if (modelData.action === "devtools" && root.devToolsController)
                                root.devToolsController.toggle()
                            else if (modelData.action === "close")
                                hostWindow.close()
                        }
                    }
                }
            }
        }
    }

    Row {
        visible: !!root.chromePolicy.showCaptionButtons && hostWindow && !hostWindow.nativeChrome
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        spacing: 0

        MainComponents.WindowButton {
            iconSource: root.minimizeIconSource
            onClicked: WindowController.minimize()
        }

        MainComponents.WindowButton {
            iconSource: hostWindow && hostWindow.visibility === Window.Maximized
                ? root.restoreIconSource
                : root.maximizeIconSource
            onClicked: WindowController.toggleMaximize()
        }

        MainComponents.WindowButton {
            iconSource: root.closeIconSource
            isCloseButton: true
            onClicked: hostWindow.close()
        }
    }
}
