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

Item {
    id: detailsPane

    readonly property var hostWindow: Window.window
    property var theme: hostWindow && hostWindow.theme ? hostWindow.theme : null
    property var runtimeContext: hostWindow && hostWindow.runtimeContext ? hostWindow.runtimeContext : null
    property var imageSources: runtimeContext && runtimeContext.imageSources ? runtimeContext.imageSources : null
    property var widget: null
    property string selectedWidgetId: ""
    property string selectedOverlayId: ""
    property bool showAdvanced: false
    property bool canWriteWidgetConfig: false
    property bool canStartFocusedMockPreview: false
    property bool focusedMockPreviewActive: false
    property bool supportsTypeDefaults: false
    property var thresholdEntries: []
    property var typeDefaultValues: ({})

    signal clearSelection()
    signal startFocusedMockPreview()
    signal stopFocusedMockPreview()
    signal setWidgetValue(string key, var value)
    signal setWidgetPosition(real x, real y)
    signal setWidgetTypeDefault(string key, var value)
    signal resetWidgetTypeDefaults()
    signal updateThreshold(int index, string key, var value)
    signal removeThreshold(int index)
    signal addThreshold()
    signal setShowAdvanced(bool value)

    clip: true

    function c(token, fallback) {
        return theme ? theme[token] : fallback;
    }

    function f(token, fallback) {
        return theme ? theme[token] : fallback;
    }

    function widgetValues() {
        return widget && widget.values ? widget.values : ({});
    }

    function widgetValue(key, fallback) {
        var values = widgetValues();
        return values[key] !== undefined ? values[key] : fallback;
    }

    function widgetTitle() {
        var values = widgetValues();
        return values.title || (widget ? widget.label : "") || selectedWidgetId || "";
    }

    function widgetLabel() {
        var values = widgetValues();
        return values.label || (widget ? widget.label : "") || selectedWidgetId || "";
    }

    function widgetDescription() {
        var values = widgetValues();
        if (values.description)
            return values.description;
        if (widget && widget.resolvedValue)
            return widget.resolvedValue;
        if (widget && widget.source)
            return widget.source;
        return widget && widget.status ? widget.status : "";
    }

    function widgetProvider() {
        if (!widget)
            return "";
        if (widget.connectorIds && widget.connectorIds.length > 0)
            return widget.connectorIds.join(", ");
        return widget.overlayId || "";
    }

    function widgetPositionX() {
        return widget && widget.position ? widget.position.x : 0;
    }

    function widgetPositionY() {
        return widget && widget.position ? widget.position.y : 0;
    }

    function typeDefaultValue(key, fallback) {
        return typeDefaultValues && typeDefaultValues[key] !== undefined ? typeDefaultValues[key] : fallback;
    }

    Rectangle {
        id: detailHeader
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 56
        color: "transparent"

        Column {
            anchors.left: parent.left
            anchors.leftMargin: 16
            anchors.right: parent.right
            anchors.rightMargin: 112
            anchors.verticalCenter: parent.verticalCenter
            spacing: 3

            Text {
                width: parent.width
                text: detailsPane.widgetTitle()
                color: detailsPane.c("text", "#dce0e5")
                font.pixelSize: detailsPane.f("fontSizeBase", 13)
                font.family: detailsPane.f("fontFamily", "sans-serif")
                font.weight: Font.DemiBold
                elide: Text.ElideRight
            }

            Text {
                width: parent.width
                text: detailsPane.widgetDescription()
                color: detailsPane.c("textMuted", "#878a98")
                font.pixelSize: detailsPane.f("fontSizeSmall", 11)
                font.family: detailsPane.f("fontFamily", "sans-serif")
                elide: Text.ElideRight
            }
        }

        Rectangle {
            id: closeButton
            anchors.right: parent.right
            anchors.rightMargin: 12
            anchors.verticalCenter: parent.verticalCenter
            width: 28
            height: 28
            radius: 4
            color: closeHover.hovered ? detailsPane.c("surfaceRaised", "#3b414d") : "transparent"
            border.width: 1
            border.color: closeHover.hovered ? detailsPane.c("accent", "#4a9eff") : detailsPane.c("border", "#464b57")

            Image {
                anchors.centerIn: parent
                width: 16
                height: 16
                source: detailsPane.imageSources ? detailsPane.imageSources.imageUrl("ui.window-close") : ""
                sourceSize.width: 16
                sourceSize.height: 16
                fillMode: Image.PreserveAspectFit
                opacity: closeHover.hovered ? 1.0 : 0.75
                Behavior on opacity {
                    NumberAnimation {
                        duration: 80
                    }
                }
            }

            MouseArea {
                anchors.fill: parent
                acceptedButtons: Qt.LeftButton
                onClicked: detailsPane.clearSelection()
            }

            HoverHandler {
                id: closeHover
            }
        }

        Row {
            anchors.right: closeButton.left
            anchors.rightMargin: 8
            anchors.verticalCenter: parent.verticalCenter
            spacing: 6

            IconButton {
                iconSource: detailsPane.imageSources ? detailsPane.imageSources.imageUrl("ui.play") : ""
                enabled: detailsPane.canStartFocusedMockPreview && !detailsPane.focusedMockPreviewActive
                onClicked: detailsPane.startFocusedMockPreview()
            }

            IconButton {
                iconSource: detailsPane.imageSources ? detailsPane.imageSources.imageUrl("ui.stop") : ""
                enabled: detailsPane.focusedMockPreviewActive
                onClicked: detailsPane.stopFocusedMockPreview()
            }
        }

        Rectangle {
            anchors.bottom: parent.bottom
            width: parent.width
            height: 1
            color: detailsPane.c("border", "#464b57")
        }
    }

    Flickable {
        anchors.top: detailHeader.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        contentHeight: editColumn.implicitHeight + 16
        clip: true

        Column {
            id: editColumn
            anchors.left: parent.left
            anchors.right: parent.right
            spacing: 0

            SectionHeader {
                text: "Identity"
            }

            EditRow {
                label: "Label"
                description: "Short text shown on the widget"
                TextInputBox {
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    textValue: detailsPane.widgetLabel()
                    enabled: detailsPane.canWriteWidgetConfig
                    onCommit: text => detailsPane.setWidgetValue("label", text)
                }
            }

            EditRow {
                label: "Name"
                description: detailsPane.widgetTitle()
            }

            EditRow {
                label: "Description"
                description: detailsPane.widgetDescription()
            }

            SectionHeader {
                text: "Position"
            }

            EditRow {
                label: "Position X"
                NumberStepper {
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    value: detailsPane.widgetPositionX()
                    enabled: detailsPane.selectedOverlayId !== "" && detailsPane.canWriteWidgetConfig
                    onCommit: v => detailsPane.setWidgetPosition(v, detailsPane.widgetPositionY())
                }
            }

            EditRow {
                label: "Position Y"
                NumberStepper {
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    value: detailsPane.widgetPositionY()
                    enabled: detailsPane.selectedOverlayId !== "" && detailsPane.canWriteWidgetConfig
                    onCommit: v => detailsPane.setWidgetPosition(detailsPane.widgetPositionX(), v)
                }
            }

            SectionHeader {
                text: "Provider"
            }

            EditRow {
                label: "Binding"
                description: detailsPane.widgetProvider()
            }

            EditRow {
                label: "Mode"
                description: detailsPane.widget ? detailsPane.widget.status : ""
            }

            SectionHeader {
                text: "Style"
            }

            SectionHeader {
                visible: detailsPane.supportsTypeDefaults
                text: "Type defaults"
            }

            EditRow {
                visible: detailsPane.supportsTypeDefaults
                label: "Default size"
                description: "Applies to text widgets in this overlay"
                Row {
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 6

                    NumberStepper {
                        width: 58
                        value: detailsPane.typeDefaultValue("width", 220)
                        step: 10
                        min: 80
                        max: 800
                        enabled: detailsPane.canWriteWidgetConfig
                        onCommit: v => detailsPane.setWidgetTypeDefault("width", Math.round(v))
                    }

                    NumberStepper {
                        width: 58
                        value: detailsPane.typeDefaultValue("height", 72)
                        step: 4
                        min: 32
                        max: 400
                        enabled: detailsPane.canWriteWidgetConfig
                        onCommit: v => detailsPane.setWidgetTypeDefault("height", Math.round(v))
                    }
                }
            }

            EditRow {
                visible: detailsPane.supportsTypeDefaults
                label: "Default font"
                description: "Text widget font size"
                NumberStepper {
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    value: detailsPane.typeDefaultValue("fontSize", 18)
                    step: 1
                    min: 8
                    max: 96
                    enabled: detailsPane.canWriteWidgetConfig
                    onCommit: v => detailsPane.setWidgetTypeDefault("fontSize", Math.round(v))
                }
            }

            EditRow {
                visible: detailsPane.supportsTypeDefaults
                label: "Text color"
                description: "Default text color"
                ColorPicker {
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    value: detailsPane.typeDefaultValue("textColor", "#E8EDF2")
                    enabled: detailsPane.canWriteWidgetConfig
                    theme: detailsPane.theme
                    onColorPicked: hex => detailsPane.setWidgetTypeDefault("textColor", hex)
                }
            }

            EditRow {
                visible: detailsPane.supportsTypeDefaults
                label: "Background"
                description: "Default background color"
                ColorPicker {
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    value: detailsPane.typeDefaultValue("backgroundColor", "#20242b")
                    enabled: detailsPane.canWriteWidgetConfig
                    theme: detailsPane.theme
                    onColorPicked: hex => detailsPane.setWidgetTypeDefault("backgroundColor", hex)
                }
            }

            EditRow {
                visible: detailsPane.supportsTypeDefaults
                label: "Reset type defaults"
                description: "Return text widgets in this overlay to manifest values"
                ActionButton {
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    label: "Reset"
                    enabled: detailsPane.canWriteWidgetConfig
                    onClicked: detailsPane.resetWidgetTypeDefaults()
                }
            }

            EditRow {
                label: "Border"
                description: "Draw an outline around the floating widget"
                ToggleSwitch {
                    anchors.centerIn: parent
                    checked: detailsPane.widgetValue("borderEnabled", true) !== false
                    enabled: detailsPane.canWriteWidgetConfig
                    onToggled: v => detailsPane.setWidgetValue("borderEnabled", v)
                }
            }

            EditRow {
                label: "Border color"
                description: "Base border color, before threshold overrides"
                TextInputBox {
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    textValue: detailsPane.widgetValue("borderColor", "#40FFFFFF")
                    enabled: detailsPane.canWriteWidgetConfig
                    onCommit: text => detailsPane.setWidgetValue("borderColor", text)
                }
            }

            EditRow {
                label: "Border width"
                description: "Base border thickness"
                NumberStepper {
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    value: detailsPane.widgetValue("borderWidth", 1)
                    step: 1
                    min: 1
                    max: 8
                    enabled: detailsPane.canWriteWidgetConfig
                    onCommit: v => detailsPane.setWidgetValue("borderWidth", Math.round(v))
                }
            }

            SectionHeader {
                text: "Thresholds"
            }

            ThresholdEditor {
                entries: detailsPane.thresholdEntries
                editable: detailsPane.canWriteWidgetConfig
                theme: detailsPane.theme
                onUpdateThreshold: (index, key, value) => detailsPane.updateThreshold(index, key, value)
                onRemoveThreshold: index => detailsPane.removeThreshold(index)
                onAddThreshold: detailsPane.addThreshold()
            }

            SectionHeader {
                text: detailsPane.showAdvanced ? "Advanced" : "Advanced (hidden)"

                MouseArea {
                    anchors.fill: parent
                    onClicked: detailsPane.setShowAdvanced(!detailsPane.showAdvanced)
                }
            }

            EditRow {
                visible: detailsPane.showAdvanced
                label: "Show source"
                description: "Show the connector source key inside the floating widget"
                ToggleSwitch {
                    anchors.centerIn: parent
                    checked: detailsPane.widgetValue("showSource", false) === true
                    enabled: detailsPane.canWriteWidgetConfig
                    onToggled: v => detailsPane.setWidgetValue("showSource", v)
                }
            }

            EditRow {
                visible: detailsPane.showAdvanced
                label: "Widget ID"
                value: detailsPane.selectedWidgetId
            }

            EditRow {
                visible: detailsPane.showAdvanced
                label: "Overlay"
                value: detailsPane.selectedOverlayId
            }

            EditRow {
                visible: detailsPane.showAdvanced
                label: "Type"
                value: detailsPane.widget ? detailsPane.widget.widgetType : ""
            }

            EditRow {
                visible: detailsPane.showAdvanced
                label: "Source"
                description: detailsPane.widget ? detailsPane.widget.source : ""
            }

            EditRow {
                visible: detailsPane.showAdvanced
                label: "Resolved"
                description: detailsPane.widget ? detailsPane.widget.resolvedValue : ""
            }
        }
    }
}
