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

pragma ComponentBehavior: Bound

import QtQuick

Rectangle {
    id: root

    property var theme: null
    property var statusItems: []
    property var pluginStates: ({})
    property string statusActiveLabel: ""
    property string pendingPluginActivation: ""
    property bool widgetsVisible: true
    property bool showPluginPanel: false

    signal triggerAction(string action)
    signal activatePendingPlugin(string pluginId)
    signal clearPendingActivation()
    signal togglePluginPanel()

    height: 32
    color: root.theme ? root.theme.surfaceRaised : "#3b414d"
    z: 20

    function pluginStatusColor(pluginId: string): color {
        if (!pluginId || pluginId === "")
            return root.theme ? root.theme.textMuted : "#878a98";

        if (root.pendingPluginActivation !== "" && root.pendingPluginActivation !== pluginId)
            return root.theme ? root.theme.warningAlt : "#B05CFF";

        var state = root.pluginStates[pluginId] || "active";
        if (state === "active")
            return root.theme ? root.theme.success : "#4caf50";
        if (state === "enabling" || state === "loading" || state === "unloading")
            return state === "unloading" ? (root.theme ? root.theme.warningAlt : "#B05CFF") : (root.theme ? root.theme.warning : "#ff9800");
        if (state === "error")
            return root.theme ? root.theme.danger : "#f44336";
        return root.theme ? root.theme.danger : "#f44336";
    }

    Rectangle {
        anchors.top: parent.top
        width: parent.width
        height: 1
        color: root.theme ? root.theme.border : "#464b57"
    }

    Row {
        anchors.left: parent.left
        anchors.leftMargin: 6
        anchors.verticalCenter: parent.verticalCenter
        spacing: 6

        Repeater {
            model: root.statusItems

            delegate: Rectangle {
                id: statusItemDelegate
                required property var modelData
                width: Math.max(statusItemLabel.implicitWidth + 12, 24)
                height: 20
                radius: 3
                color: itemMouse.containsMouse ? (root.theme ? root.theme.surfaceFloating : "#20242b") : "transparent"

                Text {
                    id: statusItemLabel
                    anchors.centerIn: parent
                    text: {
                        if (typeof statusItemDelegate.modelData === "string") {
                            return statusItemDelegate.modelData;
                        } else if (statusItemDelegate.modelData && statusItemDelegate.modelData.text) {
                            return statusItemDelegate.modelData.text;
                        }
                        return "";
                    }
                    color: {
                        if (statusItemDelegate.modelData && statusItemDelegate.modelData.action === "widgetVisibility.toggle") {
                            return root.widgetsVisible ? (root.theme ? root.theme.success : "#4caf50") : (root.theme ? root.theme.textMuted : "#878a98");
                        }
                        return root.theme ? root.theme.textMuted : "#c8ccd4";
                    }
                    font.pixelSize: root.theme ? root.theme.fontSizeSmall : 11
                }

                MouseArea {
                    id: itemMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: {
                        var action = statusItemDelegate.modelData.action;
                        if (action)
                            root.triggerAction(action);
                    }
                }
            }
        }
    }

    Rectangle {
        id: pluginPickerButton
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        width: pluginNameRow.implicitWidth + 20
        visible: root.statusActiveLabel !== ""
        z: 25
        color: root.showPluginPanel ? (root.theme ? root.theme.surfaceAlt : "#2f343e") : pluginNameHover.containsMouse ? (root.theme ? root.theme.surfaceFloating : "#20242b") : "transparent"

        Rectangle {
            visible: root.showPluginPanel
            anchors.left: parent.left
            width: 1
            height: parent.height
            color: root.theme ? root.theme.border : "#464b57"
        }
        Rectangle {
            visible: root.showPluginPanel
            anchors.right: parent.right
            width: 1
            height: parent.height
            color: root.theme ? root.theme.border : "#464b57"
        }

        Row {
            id: pluginNameRow
            anchors.centerIn: parent
            spacing: 8

            Rectangle {
                anchors.verticalCenter: parent.verticalCenter
                width: 8
                height: 8
                radius: 4
                color: root.pluginStatusColor(root.statusActiveLabel)
            }

            Text {
                anchors.verticalCenter: parent.verticalCenter
                text: root.statusActiveLabel
                color: "#FFFFFF"
                font.pixelSize: root.theme ? root.theme.fontSizeSmall : 11
                font.family: root.theme ? root.theme.fontFamily : "sans-serif"
            }
        }

        MouseArea {
            id: pluginNameHover
            anchors.fill: parent
            hoverEnabled: true
            onClicked: {
                if (root.showPluginPanel && root.pendingPluginActivation !== "") {
                    root.activatePendingPlugin(root.pendingPluginActivation);
                    root.clearPendingActivation();
                }
                if (!root.showPluginPanel)
                    root.clearPendingActivation();
                root.togglePluginPanel();
            }
        }
    }
}
