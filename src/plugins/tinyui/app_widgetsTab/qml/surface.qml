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
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: widgetTab

    anchors.fill: parent
    color: "transparent"

    // Column widths (matching v0.4.0)
    readonly property int colName:   200
    readonly property int colToggle:  56
    readonly property int colPad:     16

    // Capabilities from hostWindow
    readonly property var widgetRead: hostWindow?.widgetRead ?? null
    readonly property var widgetConfigRead: hostWindow?.widgetConfigRead ?? null
    readonly property var widgetConfigWrite: hostWindow?.widgetConfigWrite ?? null
    readonly property var widgetVisibilityRead: hostWindow?.widget_visibility_read ?? null
    readonly property var widgetVisibilityWrite: hostWindow?.widget_visibility_write ?? null
    
    // State
    property string selectedWidgetId: ""
    property string selectedOverlayId: ""
    
    // Helper to get enabled state for a widget
    function isWidgetEnabled(widgetId) {
        if (!widgetConfigRead) return false
        var config = widgetConfigRead.getWidget(widgetId)
        return config ? config.enabled : false
    }
    
    // Sync overlay ID and ensure widgets are visible when selection changes
    onSelectedWidgetIdChanged: {
        // Update overlay ID
        if (!selectedWidgetId || !widgetRead) {
            selectedOverlayId = ""
        } else {
            // Find the widget in the model to get its overlayId
            var widgets = widgetRead.widgets
            for (var i = 0; i < widgets.length; i++) {
                if (widgets[i].widgetId === selectedWidgetId) {
                    selectedOverlayId = widgets[i].overlayId ?? ""
                    break
                }
            }
        }
        
        // If widgets are hidden and user selects a widget, make them visible
        if (selectedWidgetId && widgetVisibilityRead && !widgetVisibilityRead.globalVisible && widgetVisibilityWrite) {
            widgetVisibilityWrite.setGlobalVisible(true)
        }
    }

    // ── Left: widget list ──────────────────────────────────────────────────────
    Item {
        id: listPane
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        width: selectedWidgetId ? parent.width * 0.4 : parent.width
        Behavior on width { NumberAnimation { duration: 180; easing.type: Easing.OutCubic } }

        // Header
        Rectangle {
            id: tableHeader
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            height: 36
            color: "#252830"

            Text {
                anchors.left: parent.left
                anchors.leftMargin: 16
                anchors.verticalCenter: parent.verticalCenter
                text: "Widget"
                color: "#8b92a8"
                font.pixelSize: 12
                font.weight: Font.DemiBold
            }

            Text {
                anchors.right: parent.right
                anchors.rightMargin: 16
                anchors.verticalCenter: parent.verticalCenter
                text: "Enabled"
                color: "#8b92a8"
                font.pixelSize: 12
                font.weight: Font.DemiBold
            }

            Rectangle {
                anchors.bottom: parent.bottom
                width: parent.width
                height: 1
                color: "#1a1c22"
            }
        }

        // Widget list
        ListView {
            id: widgetList
            anchors.top: tableHeader.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            clip: true
            model: widgetRead?.widgets ?? []

            delegate: Rectangle {
                id: widgetItem
                required property var modelData
                required property int index
                
                readonly property string widgetId: modelData.widgetId ?? ""

                width: widgetList.width
                height: 40
                color: widgetTab.selectedWidgetId === widgetId
                    ? "#2d333f"
                    : (hoverArea.containsMouse ? "#2a2d35" : "transparent")

                Behavior on color { ColorAnimation { duration: 80 } }

                // Selection indicator
                Rectangle {
                    width: 2
                    height: parent.height
                    color: "#4fc1e9"
                    visible: widgetTab.selectedWidgetId === widgetId
                }

                // Widget name
                Text {
                    anchors.left: parent.left
                    anchors.leftMargin: 16
                    anchors.verticalCenter: parent.verticalCenter
                    text: widgetItem.widgetId
                    color: "#ffffff"
                    font.pixelSize: 13
                }

                // Enabled toggle
                Switch {
                    id: enableToggle
                    anchors.right: parent.right
                    anchors.rightMargin: 8
                    anchors.verticalCenter: parent.verticalCenter
                    checked: widgetTab.isWidgetEnabled(widgetItem.widgetId)
                    enabled: widgetTab.widgetConfigWrite !== null && modelData.overlayId !== undefined

                    onClicked: {
                        if (widgetTab.widgetConfigWrite && modelData.overlayId !== undefined) {
                            widgetTab.widgetConfigWrite.setWidgetEnabled(
                                modelData.overlayId,
                                widgetItem.widgetId,
                                !checked
                            )
                        }
                    }
                }

                // Click area for selection
                MouseArea {
                    id: hoverArea
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: {
                        widgetTab.selectedWidgetId = widgetItem.widgetId
                    }
                }
            }
        }
    }

    // ── Right: detail pane ─────────────────────────────────────────────────────
    Item {
        id: detailPane
        anchors.top: parent.top
        anchors.left: listPane.right
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        visible: widgetTab.selectedWidgetId !== ""
        opacity: visible ? 1 : 0
        Behavior on opacity { NumberAnimation { duration: 120 } }

        // Separator line
        Rectangle {
            anchors.left: parent.left
            width: 1
            height: parent.height
            color: "#1a1c22"
        }

        // Content
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 16
            spacing: 16

            // Preview area
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 120
                color: "#1e2128"
                border.color: "#2d333f"
                border.width: 1
                radius: 4

                Text {
                    anchors.centerIn: parent
                    text: widgetTab.selectedWidgetId ? "Preview: " + widgetTab.selectedWidgetId : "Select a widget"
                    color: "#8b92a8"
                    font.pixelSize: 14
                }

                // TODO: Actual widget preview when available
            }

            // Position controls
            GroupBox {
                Layout.fillWidth: true
                title: "Position"

                RowLayout {
                    anchors.fill: parent
                    spacing: 16

                    Label { text: "X:"; color: "#ffffff" }
                    SpinBox {
                        id: posX
                        value: widgetTab.widgetConfigRead?.getWidget(widgetTab.selectedWidgetId)?.position?.x ?? 0
                        enabled: widgetTab.selectedOverlayId !== ""
                        onValueModified: {
                            if (widgetTab.widgetConfigWrite && widgetTab.selectedOverlayId !== "") {
                                widgetTab.widgetConfigWrite.setWidgetPosition(
                                    widgetTab.selectedOverlayId,
                                    widgetTab.selectedWidgetId,
                                    value,
                                    posY.value
                                )
                            }
                        }
                    }

                    Label { text: "Y:"; color: "#ffffff" }
                    SpinBox {
                        id: posY
                        value: widgetTab.widgetConfigRead?.getWidget(widgetTab.selectedWidgetId)?.position?.y ?? 0
                        enabled: widgetTab.selectedOverlayId !== ""
                        onValueModified: {
                            if (widgetTab.widgetConfigWrite && widgetTab.selectedOverlayId !== "") {
                                widgetTab.widgetConfigWrite.setWidgetPosition(
                                    widgetTab.selectedOverlayId,
                                    widgetTab.selectedWidgetId,
                                    posX.value,
                                    value
                                )
                            }
                        }
                    }
                }
            }

            // Size controls (not yet implemented in backend)
            // GroupBox {
            //     Layout.fillWidth: true
            //     title: "Size"
            //     ...
            // }

            // Spacer
            Item { Layout.fillHeight: true }
        }
    }
}
