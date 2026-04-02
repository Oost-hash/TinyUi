//  TinyUI
//  Copyright (C) 2026 Oost-hash
//
//  This file is part of TinyUI.
//
//  TinyUI is free software: you can redistribute it and/or modify
//  it under the terms of the GNU General Public License as published by
//  the Free Software Foundation, either version 3 of the License, or
//  (at your option) any later version.
//
//  TinyUI is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU General Public License for more details.
//
//  You should have received a copy of the GNU General Public License
//  along with this program.  If not, see <https://www.gnu.org/licenses/>.
//
//  TinyUI builds on TinyPedal by s-victor (https://github.com/s-victor/TinyPedal),
//  licensed under GPLv3.

import QtQuick
import QtQuick.Window
import QtQuick.Layouts

Item {
    id: root

    readonly property var hostWindow: Window.window
    readonly property var hostRuntime: hostWindow && hostWindow.hostRuntime ? hostWindow.hostRuntime : null
    readonly property var theme: hostWindow && hostWindow.theme ? hostWindow.theme : null
    readonly property var hostActions: hostWindow && hostWindow.hostActions ? hostWindow.hostActions : null
    readonly property var windowController: hostWindow && hostWindow.windowController ? hostWindow.windowController : null

    property string windowTitle: hostWindow && typeof hostWindow.windowTitle === "string" ? hostWindow.windowTitle : ""
    
    // UI state from hostWindow (set by HostedWindow from hostRuntime signals)
    property var menuItems: hostWindow ? hostWindow.menuItems : []
    property var pluginMenuItems: hostWindow ? hostWindow.pluginMenuItems : []
    property var pluginMenuLabel: hostWindow ? hostWindow.pluginMenuLabel : ""
    property var tabModel: hostWindow ? hostWindow.tabModel : []
    property var activePlugin: hostWindow ? hostWindow.activePluginId : ""
    
    property int currentTab: hostWindow && typeof hostWindow.currentTab === "number" ? hostWindow.currentTab : 0
    property bool showTabBar: hostWindow && typeof hostWindow.showTabBar === "boolean" ? hostWindow.showTabBar : false
    property bool showStatusBar: hostWindow && typeof hostWindow.showStatusBar === "boolean" ? hostWindow.showStatusBar : false
    property var statusItems: hostWindow ? hostWindow.statusItems : []
    property var chromePolicy: hostWindow && hostWindow.chromePolicy ? hostWindow.chromePolicy : ({
        showMenuButton: true,
        showTitleText: true,
        showCaptionButtons: true,
        showStatusLeftItems: true
    })
    property bool menuOpen: false

    readonly property url menuIconSource: Qt.resolvedUrl("../../app_assets/icons/" + (root.menuOpen ? "menu-open.svg" : "menu.svg"))
    readonly property url minimizeIconSource: Qt.resolvedUrl("../../app_assets/icons/window-minimize.svg")
    readonly property url maximizeIconSource: Qt.resolvedUrl("../../app_assets/icons/window-maximize.svg")
    readonly property url restoreIconSource: Qt.resolvedUrl("../../app_assets/icons/window-restore.svg")
    readonly property url closeIconSource: Qt.resolvedUrl("../../app_assets/icons/window-close.svg")
    
    // Export menu button width for HostChromeShell to position plugin menu
    readonly property real menuButtonWidth: menuButton.width

    // Close menu when clicking anywhere in the window (behind other content)
    MouseArea {
        anchors.fill: parent
        enabled: root.menuOpen
        onClicked: root.menuOpen = false
        z: 15  // Below menu dropdown (z:40) but above content
    }

    Rectangle {
        id: titleBar
        z: 20
        x: 0
        y: 0
        width: root.width
        height: 32
        color: root.theme ? root.theme.surfaceRaised : "#3b414d"

        Rectangle {
            anchors.bottom: parent.bottom
            width: parent.width
            height: 1
            color: root.theme ? root.theme.border : "#464b57"
        }

        Rectangle {
            id: menuButton
            visible: !!root.chromePolicy.showMenuButton
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            width: menuRow.width + 28
            color: menuArea.containsMouse || root.menuOpen
                ? (root.theme ? root.theme.surfaceAlt : "#2f343e")
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
                anchors.verticalCenter: parent.verticalCenter
                text: root.windowTitle
                color: menuArea.containsMouse || root.menuOpen
                    ? "#FFFFFF"
                    : (root.theme ? root.theme.textMuted : "#878a98")
                font.pixelSize: 12
            }
        }

        MouseArea {
            anchors.left: menuButton.visible ? menuButton.right : parent.left
            anchors.right: captionButtons.visible ? captionButtons.left : parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            acceptedButtons: Qt.LeftButton
            onPressed: {
                if (root.windowController)
                    root.windowController.startMove()
            }
        }

        Item {
            id: menuDropdown
            z: 40
            x: 0
            y: titleBar.height
            width: 160
            height: menuColumn.implicitHeight
            visible: !!root.chromePolicy.showMenuButton && root.menuOpen

            Rectangle { anchors.fill: parent; color: root.theme ? root.theme.surfaceAlt : "#2f343e" }
            Rectangle { anchors.left: parent.left; width: 1; height: parent.height; color: root.theme ? root.theme.border : "#464b57" }
            Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: root.theme ? root.theme.border : "#464b57" }
            Rectangle { anchors.right: parent.right; width: 1; height: parent.height; color: root.theme ? root.theme.border : "#464b57" }

            // Prevent clicks from closing the menu immediately
            MouseArea {
                anchors.fill: parent
                onClicked: mouse.accepted = true
            }

            Column {
                id: menuColumn
                width: parent.width
                spacing: 0

                Repeater {
                    model: root.menuItems

                    delegate: Item {
                        required property var modelData
                        visible: modelData.visible === undefined ? true : !!modelData.visible
                        width: menuDropdown.width
                        height: visible ? (modelData.separator ? 9 : 28) : 0

                        // Separator line
                        Rectangle {
                            visible: !!modelData.separator
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.leftMargin: 8
                            anchors.rightMargin: 8
                            height: 1
                            color: root.theme ? root.theme.border : "#464b57"
                        }

                        // Clickable/hoverable area for non-separator items
                        Rectangle {
                            visible: !modelData.separator
                            anchors.fill: parent
                            color: menuItemMouse.containsMouse
                                ? (root.theme ? root.theme.surfaceRaised : "#3b414d")
                                : "transparent"

                            Text {
                                anchors.left: parent.left
                                anchors.leftMargin: 12
                                anchors.verticalCenter: parent.verticalCenter
                                text: modelData.label
                                color: root.theme ? root.theme.text : "#dce0e5"
                                font.pixelSize: root.theme ? root.theme.fontSizeSmall : 11
                            }

                            MouseArea {
                                id: menuItemMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                onClicked: {
                                    root.menuOpen = false
                                    if (root.hostActions)
                                        root.hostActions.trigger(modelData.action)
                                    else if (modelData.action === "close" && root.hostWindow)
                                        root.hostWindow.close()
                                }
                            }
                        }
                    }
                }
            }
        }

        Row {
            id: captionButtons
            visible: !!root.chromePolicy.showCaptionButtons && root.hostWindow && !root.hostWindow.nativeChrome
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            spacing: 0

            Repeater {
                model: [
                    { "icon": root.minimizeIconSource, "close": false, "action": "minimize" },
                    {
                        "icon": root.hostWindow && root.hostWindow.visibility === Window.Maximized
                            ? root.restoreIconSource
                            : root.maximizeIconSource,
                        "close": false,
                        "action": "maximize"
                    },
                    { "icon": root.closeIconSource, "close": true, "action": "close" }
                ]

                delegate: Rectangle {
                    required property var modelData
                    width: 46
                    height: titleBar.height
                    color: titleButtonArea.containsMouse
                        ? (modelData.close
                            ? (root.theme ? root.theme.danger : "#d15b5b")
                            : (root.theme ? root.theme.surfaceFloating : "#20242b"))
                        : "transparent"

                    Image {
                        anchors.centerIn: parent
                        width: 16
                        height: 16
                        source: modelData.icon
                        sourceSize.width: width
                        sourceSize.height: height
                        fillMode: Image.PreserveAspectFit
                        smooth: true
                    }

                    MouseArea {
                        id: titleButtonArea
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: {
                            if (modelData.action === "minimize" && root.windowController) {
                                root.windowController.minimize()
                            } else if (modelData.action === "maximize" && root.windowController) {
                                root.windowController.toggleMaximize()
                            } else if (modelData.action === "close" && root.hostWindow) {
                                root.hostWindow.close()
                            }
                        }
                    }
                }
            }
        }
    }

    // Tab bar with runtime tabs
    Rectangle {
        id: tabBar
        x: 0
        y: titleBar.height
        width: root.width
        height: 42
        visible: root.showTabBar && hostWindow && hostWindow.tabModel && hostWindow.tabModel.length > 0 && !(hostWindow && hostWindow.showPluginPanel)
        color: root.theme ? root.theme.surfaceAlt : "#2f343e"
        z: 5
        

        Rectangle {
            anchors.bottom: parent.bottom
            width: parent.width
            height: 1
            color: root.theme ? root.theme.border : "#3a4452"
        }

        Row {
            anchors.fill: parent
            spacing: -1

            Repeater {
                model: hostWindow ? hostWindow.tabModel : []

                delegate: Rectangle {
                    required property var modelData
                    required property int index

                    width: Math.max(tabLabel.implicitWidth + 40, 88)
                    height: tabBar.height
                    color: hostWindow.currentTab === index
                        ? (root.theme ? root.theme.surface : "#282c33")
                        : (root.theme ? root.theme.surfaceAlt : "#2f343e")

                    // Left border
                    Rectangle {
                        anchors.left: parent.left
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        width: 1
                        color: root.theme ? root.theme.border : "#3a4452"
                    }

                    // Right border
                    Rectangle {
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        width: 1
                        color: root.theme ? root.theme.border : "#3a4452"
                    }

                    // Bottom border (only for inactive tabs)
                    Rectangle {
                        anchors.bottom: parent.bottom
                        anchors.left: parent.left
                        anchors.right: parent.right
                        height: 1
                        visible: hostWindow.currentTab !== index
                        color: root.theme ? root.theme.border : "#464b57"
                    }

                    Text {
                        id: tabLabel
                        anchors.centerIn: parent
                        text: modelData.label
                        color: hostWindow.currentTab === index
                            ? (root.theme ? root.theme.text : "#dce0e5")
                            : (root.theme ? root.theme.textSecondary : "#a9afbc")
                        font.pixelSize: root.theme ? root.theme.fontSizeBase : 13
                    }

                    MouseArea {
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: {
                            if (hostWindow)
                                hostWindow.currentTab = index
                        }
                    }
                }
            }
        }
    }

    // Content area with tab switching or direct surface
    Item {
        id: contentPane
        objectName: "surfaceHost"
        x: 0
        y: titleBar.height + (tabBar.visible ? tabBar.height : 0)
        width: root.width
        height: root.height - y - (statusBar.visible ? statusBar.height : 0)

        // Use tab model if available, otherwise use surfaceComponent directly
        Loader {
            anchors.fill: parent
            sourceComponent: {
                if (hostWindow && hostWindow.tabModel && hostWindow.tabModel.length > 0) {
                    return tabContentComponent
                }
                return hostWindow ? hostWindow.surfaceComponent : null
            }
        }

        Component {
            id: tabContentComponent
            StackLayout {
                currentIndex: hostWindow ? hostWindow.currentTab : 0

                Repeater {
                    model: hostWindow ? hostWindow.tabModel : []

                    delegate: Item {
                        required property var modelData
                        
                        Loader {
                            anchors.fill: parent
                            source: modelData.surface || ""
                        }
                    }
                }
            }
        }
    }

    Rectangle {
        id: statusBar
        x: 0
        y: root.height - height
        width: root.width
        height: 32
        visible: root.showStatusBar
        color: root.theme ? root.theme.surfaceRaised : "#3b414d"

        Rectangle {
            anchors.top: parent.top
            width: parent.width
            height: 1
            color: root.theme ? root.theme.border : "#464b57"
        }

        Row {
            visible: !!root.chromePolicy.showStatusLeftItems
            anchors.left: parent.left
            anchors.leftMargin: 6
            anchors.verticalCenter: parent.verticalCenter
            spacing: 6

            Repeater {
                model: root.statusItems

                delegate: Rectangle {
                    required property var modelData
                    width: Math.max(label.implicitWidth + 12, 24)
                    height: 20
                    radius: 3
                    color: itemMouse.containsMouse
                        ? (root.theme ? root.theme.surfaceFloating : "#20242b")
                        : "transparent"

                    Text {
                        id: label
                        anchors.centerIn: parent
                        text: typeof modelData === "string" ? modelData : ""
                        color: root.theme ? root.theme.textMuted : "#c8ccd4"
                        font.pixelSize: root.theme ? root.theme.fontSizeSmall : 11
                    }

                    MouseArea {
                        id: itemMouse
                        anchors.fill: parent
                        hoverEnabled: true
                    }
                }
            }
        }

        // Plugin picker placeholder - host chrome can override this
        Item {
            id: pluginPickerPlaceholder
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            width: 0
            visible: false
        }
    }
}
