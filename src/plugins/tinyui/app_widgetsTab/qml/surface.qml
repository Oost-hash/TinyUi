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
    id: widgetTab

    property var hostWindow: Window.window
    property var theme: hostWindow && hostWindow.theme ? hostWindow.theme : null
    property var widgetRecords: hostWindow && hostWindow.widgetRecords ? hostWindow.widgetRecords : null
    property var widgetConfigRead: hostWindow && hostWindow.widgetConfigRead ? hostWindow.widgetConfigRead : null
    property var widgetConfigWrite: hostWindow && hostWindow.widgetConfigWrite ? hostWindow.widgetConfigWrite : null
    property var widgetVisibility: hostWindow && hostWindow.widgetVisibility ? hostWindow.widgetVisibility : null
    property var widgetPreviewActions: hostWindow && hostWindow.widgetPreviewActions ? hostWindow.widgetPreviewActions : null
    property var widgetItems: []
    property string widgetItemsSignature: ""
    readonly property int widgetCount: widgetItems ? widgetItems.length : 0
    readonly property string diagnosticsMessage: !hostWindow ? "WidgetTab cannot see the host window." : (!widgetRecords ? "Widget records are not attached to this window." : (widgetCount === 0 ? "Widget records are attached, but no widgets are available." : ""))

    property string selectedWidgetId: ""
    property string selectedOverlayId: ""
    property bool showAdvanced: false
    property bool focusedWidgetVisibleActive: false
    property bool focusedMockPreviewActive: false

    anchors.fill: parent

    function c(token, fallback) {
        return theme ? theme[token] : fallback;
    }

    function f(token, fallback) {
        return theme ? theme[token] : fallback;
    }

    function widgets() {
        return widgetItems;
    }

    function selectedWidgetRecord() {
        var items = widgets();
        for (var i = 0; i < items.length; i++) {
            if (items[i].widgetId === selectedWidgetId && items[i].overlayId === selectedOverlayId)
                return items[i];
        }
        return null;
    }

    function selectWidget(widget) {
        if (!widget)
            return;
        if (selectedWidgetId === widget.widgetId && selectedOverlayId === widget.overlayId) {
            clearSelection();
            return;
        }

        selectedWidgetId = widget.widgetId;
        selectedOverlayId = widget.overlayId;

        if (widgetPreviewActions) {
            widgetPreviewActions.setFocusedWidgetVisible(selectedOverlayId, selectedWidgetId, true);
            focusedWidgetVisibleActive = true;
        }

        if (focusedMockPreviewActive && widgetPreviewActions)
            widgetPreviewActions.setFocusedPreviewVisible(selectedOverlayId, selectedWidgetId, true);
    }

    function isWidgetSelected(widget) {
        return widget && selectedWidgetId === widget.widgetId && selectedOverlayId === widget.overlayId;
    }

    function clearSelection() {
        stopFocusedMockPreview();
        stopFocusedWidgetVisibility();
        selectedWidgetId = "";
        selectedOverlayId = "";
    }

    function stopFocusedWidgetVisibility() {
        if (!focusedWidgetVisibleActive)
            return;
        if (widgetPreviewActions && selectedOverlayId !== "" && selectedWidgetId !== "")
            widgetPreviewActions.setFocusedWidgetVisible(selectedOverlayId, selectedWidgetId, false);
        focusedWidgetVisibleActive = false;
    }

    function startFocusedMockPreview() {
        if (!widgetPreviewActions || selectedOverlayId === "" || selectedWidgetId === "")
            return;
        widgetPreviewActions.setFocusedPreviewVisible(selectedOverlayId, selectedWidgetId, true);
        focusedMockPreviewActive = true;
    }

    function stopFocusedMockPreview() {
        if (!focusedMockPreviewActive)
            return;
        if (widgetPreviewActions)
            widgetPreviewActions.setFocusedPreviewVisible(selectedOverlayId, selectedWidgetId, false);
        focusedMockPreviewActive = false;
    }

    function widgetTitle(widget) {
        if (!widget)
            return "";
        var values = widgetValues(widget);
        return values.title || widget.label || widget.widgetId || "";
    }

    function widgetLabel(widget) {
        if (!widget)
            return "";
        var values = widgetValues(widget);
        return values.label || widget.label || widget.widgetId || "";
    }

    function widgetDescription(widget) {
        if (!widget)
            return "";
        var values = widgetValues(widget);
        if (values.description)
            return values.description;
        if (widget.resolvedValue)
            return widget.resolvedValue;
        if (widget.source)
            return widget.source;
        return widget.status || "";
    }

    function widgetProvider(widget) {
        if (!widget)
            return "";
        if (widget.connectorIds && widget.connectorIds.length > 0)
            return widget.connectorIds.join(", ");
        return widget.overlayId || "";
    }

    function widgetPositionX(widget) {
        return widget && widget.position ? widget.position.x : 0;
    }

    function widgetPositionY(widget) {
        return widget && widget.position ? widget.position.y : 0;
    }

    function widgetValues(widget) {
        return widget && widget.values ? widget.values : ({});
    }

    function widgetValue(widget, key, fallback) {
        var values = widgetValues(widget);
        return values[key] !== undefined ? values[key] : fallback;
    }

    function setWidgetValue(key, value) {
        if (!widgetConfigWrite || selectedOverlayId === "" || selectedWidgetId === "")
            return false;
        var values = {};
        values[key] = value;
        return widgetConfigWrite.setWidgetValues(selectedOverlayId, selectedWidgetId, values);
    }

    function widgetType(widget) {
        return widget && widget.widgetType ? widget.widgetType : "";
    }

    function supportsTypeDefaults(widget) {
        return widgetTypeDefaultFields(widget).length > 0;
    }

    function widgetTypeDefaultFields(widget) {
        if (!widgetConfigRead || !widget || !widget.overlayId || !widget.widgetType)
            return [];
        return widgetConfigRead.widgetTypeDefaultFields(widget.overlayId, widget.widgetType);
    }

    function widgetTypeDefaultFallbacks(widget) {
        if (!widgetConfigRead || !widget || !widget.overlayId || !widget.widgetType)
            return {};
        return widgetConfigRead.widgetTypeDefaultFallbacks(widget.overlayId, widget.widgetType);
    }

    function widgetTypeDefaults(widget) {
        if (!widgetConfigRead || !widget || !widget.overlayId || !widget.widgetType)
            return {};
        return widgetConfigRead.widgetTypeDefaults(widget.overlayId, widget.widgetType);
    }

    function widgetTypeDefaultValue(widget, key, fallback) {
        var defaults = widgetTypeDefaults(widget);
        if (defaults[key] !== undefined)
            return defaults[key];
        var fallbacks = widgetTypeDefaultFallbacks(widget);
        return fallbacks[key] !== undefined ? fallbacks[key] : fallback;
    }

    function setWidgetTypeDefault(key, value) {
        var widget = selectedWidgetRecord();
        if (!widgetConfigWrite || !widget || !widget.overlayId || !widget.widgetType)
            return false;
        var defaults = widgetTypeDefaults(widget);
        defaults[key] = value;
        return widgetConfigWrite.setWidgetTypeDefaults(widget.overlayId, widget.widgetType, defaults);
    }

    function resetWidgetTypeDefaults() {
        var widget = selectedWidgetRecord();
        if (!widgetConfigWrite || !widget || !widget.overlayId || !widget.widgetType)
            return false;
        return widgetConfigWrite.resetWidgetTypeDefaults(widget.overlayId, widget.widgetType);
    }

    function thresholdEntries(widget) {
        var raw = widgetValue(widget, "thresholds", []);
        var entries = [];
        if (!raw || raw.length === undefined)
            return entries;
        for (var i = 0; i < raw.length; i++) {
            var item = raw[i];
            if (!item)
                continue;
            entries.push({
                "value": Number(item.value !== undefined ? item.value : 0),
                "color": String(item.color !== undefined ? item.color : "#FFB000"),
                "colorTarget": String(item.colorTarget !== undefined ? item.colorTarget : (item.color_target !== undefined ? item.color_target : "value")),
                "flash": item.flash === true,
                "flashSpeed": Number(item.flashSpeed !== undefined ? item.flashSpeed : (item.flash_speed !== undefined ? item.flash_speed : 5)),
                "flashTarget": String(item.flashTarget !== undefined ? item.flashTarget : (item.flash_target !== undefined ? item.flash_target : "value"))
            });
        }
        return entries;
    }

    function setThresholdEntries(entries) {
        return setWidgetValue("thresholds", entries);
    }

    function updateThreshold(index, key, value) {
        var entries = thresholdEntries(selectedWidgetRecord());
        if (index < 0 || index >= entries.length)
            return false;
        entries[index][key] = value;
        return setThresholdEntries(entries);
    }

    function removeThreshold(index) {
        var entries = thresholdEntries(selectedWidgetRecord());
        if (index < 0 || index >= entries.length)
            return false;
        entries.splice(index, 1);
        return setThresholdEntries(entries);
    }

    function addThreshold() {
        var entries = thresholdEntries(selectedWidgetRecord());
        entries.push({
            "value": 0,
            "color": "#FFB000",
            "colorTarget": "value",
            "flash": false,
            "flashSpeed": 5,
            "flashTarget": "border"
        });
        return setThresholdEntries(entries);
    }

    function stableString(value) {
        if (value === undefined || value === null)
            return "";
        try {
            return JSON.stringify(value);
        } catch (error) {
            return String(value);
        }
    }

    function widgetListSignature(items) {
        if (!items || items.length === undefined)
            return "";

        var parts = [];
        for (var i = 0; i < items.length; i++) {
            var item = items[i];
            if (!item)
                continue;
            var position = item.position || ({});
            parts.push([item.overlayId || "", item.widgetId || "", item.widgetType || "", item.label || "", item.source || "", item.status || "", item.enabled === true ? "1" : "0", position.x !== undefined ? position.x : "", position.y !== undefined ? position.y : "", stableString(item.values || ({}))].join("|"));
        }
        return parts.join("\n");
    }

    function refreshWidgetItems() {
        var nextItems = widgetRecords ? widgetRecords.widgets : [];
        var nextSignature = widgetListSignature(nextItems);
        if (nextSignature === widgetItemsSignature)
            return;
        widgetItemsSignature = nextSignature;
        widgetItems = nextItems;
    }

    Component.onCompleted: refreshWidgetItems()
    onWidgetRecordsChanged: refreshWidgetItems()

    Rectangle {
        anchors.fill: parent
        color: widgetTab.c("surface", "#17181c")
    }

    Connections {
        target: widgetTab.widgetRecords
        function onWidgetsChanged() {
            widgetTab.refreshWidgetItems();
            if (widgetTab.selectedWidgetId !== "" && widgetTab.selectedWidgetRecord() === null) {
                widgetTab.selectedWidgetId = "";
                widgetTab.selectedOverlayId = "";
            }
        }
    }

    WidgetListPane {
        id: listPane
        z: 2
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        width: widgetTab.selectedWidgetId !== "" ? parent.width * 0.4 : parent.width
        widgets: widgetTab.widgetItems
        selectedWidgetId: widgetTab.selectedWidgetId
        selectedOverlayId: widgetTab.selectedOverlayId
        diagnosticsMessage: widgetTab.diagnosticsMessage
        canWriteWidgetConfig: widgetTab.widgetConfigWrite !== null
        theme: widgetTab.theme
        Behavior on width {
            NumberAnimation {
                duration: 180
                easing.type: Easing.OutCubic
            }
        }
        onSelectWidget: widget => widgetTab.selectWidget(widget)
        onSetWidgetEnabled: (overlayId, widgetId, enabled) => {
            if (widgetTab.widgetConfigWrite)
                widgetTab.widgetConfigWrite.setWidgetEnabled(overlayId, widgetId, enabled);
        }
    }

    Rectangle {
        z: 3
        visible: widgetTab.selectedWidgetId !== ""
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        x: listPane.width
        width: 1
        color: widgetTab.c("border", "#464b57")
    }

    Item {
        id: detailPane
        z: 1
        visible: widgetTab.selectedWidgetId !== ""
        anchors.top: parent.top
        anchors.left: listPane.right
        anchors.leftMargin: 1
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        clip: true
        opacity: visible ? 1 : 0
        Behavior on opacity {
            NumberAnimation {
                duration: 120
            }
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
                    text: widgetTab.widgetTitle(widgetTab.selectedWidgetRecord())
                    color: widgetTab.c("text", "#dce0e5")
                    font.pixelSize: widgetTab.f("fontSizeBase", 13)
                    font.family: widgetTab.f("fontFamily", "sans-serif")
                    font.weight: Font.DemiBold
                    elide: Text.ElideRight
                }

                Text {
                    width: parent.width
                    text: widgetTab.widgetDescription(widgetTab.selectedWidgetRecord())
                    color: widgetTab.c("textMuted", "#878a98")
                    font.pixelSize: widgetTab.f("fontSizeSmall", 11)
                    font.family: widgetTab.f("fontFamily", "sans-serif")
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
                color: closeHover.hovered ? widgetTab.c("surfaceRaised", "#3b414d") : "transparent"
                border.width: 1
                border.color: closeHover.hovered ? widgetTab.c("accent", "#4a9eff") : widgetTab.c("border", "#464b57")

                Image {
                    anchors.centerIn: parent
                    width: 16
                    height: 16
                    source: imageSources.imageUrl("ui.window-close")
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
                    onClicked: widgetTab.clearSelection()
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
                    iconSource: imageSources.imageUrl("ui.play")
                    enabled: widgetTab.widgetPreviewActions !== null && widgetTab.selectedOverlayId !== "" && widgetTab.selectedWidgetId !== "" && !widgetTab.focusedMockPreviewActive
                    onClicked: widgetTab.startFocusedMockPreview()
                }

                IconButton {
                    iconSource: imageSources.imageUrl("ui.stop")
                    enabled: widgetTab.focusedMockPreviewActive
                    onClicked: widgetTab.stopFocusedMockPreview()
                }
            }

            Rectangle {
                anchors.bottom: parent.bottom
                width: parent.width
                height: 1
                color: widgetTab.c("border", "#464b57")
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
                        textValue: widgetTab.widgetLabel(widgetTab.selectedWidgetRecord())
                        enabled: widgetTab.widgetConfigWrite !== null
                        onCommit: text => widgetTab.setWidgetValue("label", text)
                    }
                }

                EditRow {
                    label: "Name"
                    description: widgetTab.widgetTitle(widgetTab.selectedWidgetRecord())
                }

                EditRow {
                    label: "Description"
                    description: widgetTab.widgetDescription(widgetTab.selectedWidgetRecord())
                }

                SectionHeader {
                    text: "Position"
                }

                EditRow {
                    label: "Position X"
                    NumberStepper {
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        value: widgetTab.widgetPositionX(widgetTab.selectedWidgetRecord())
                        enabled: widgetTab.selectedOverlayId !== "" && widgetTab.widgetConfigWrite !== null
                        onCommit: v => {
                            if (widgetTab.widgetConfigWrite && widgetTab.selectedOverlayId !== "") {
                                widgetTab.widgetConfigWrite.setWidgetPosition(widgetTab.selectedOverlayId, widgetTab.selectedWidgetId, v, widgetTab.widgetPositionY(widgetTab.selectedWidgetRecord()));
                            }
                        }
                    }
                }

                EditRow {
                    label: "Position Y"
                    NumberStepper {
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        value: widgetTab.widgetPositionY(widgetTab.selectedWidgetRecord())
                        enabled: widgetTab.selectedOverlayId !== "" && widgetTab.widgetConfigWrite !== null
                        onCommit: v => {
                            if (widgetTab.widgetConfigWrite && widgetTab.selectedOverlayId !== "") {
                                widgetTab.widgetConfigWrite.setWidgetPosition(widgetTab.selectedOverlayId, widgetTab.selectedWidgetId, widgetTab.widgetPositionX(widgetTab.selectedWidgetRecord()), v);
                            }
                        }
                    }
                }

                SectionHeader {
                    text: "Provider"
                }

                EditRow {
                    label: "Binding"
                    description: widgetTab.widgetProvider(widgetTab.selectedWidgetRecord())
                }

                EditRow {
                    label: "Mode"
                    description: widgetTab.selectedWidgetRecord() ? widgetTab.selectedWidgetRecord().status : ""
                }

                SectionHeader {
                    text: "Style"
                }

                SectionHeader {
                    visible: widgetTab.supportsTypeDefaults(widgetTab.selectedWidgetRecord())
                    text: "Type defaults"
                }

                EditRow {
                    visible: widgetTab.supportsTypeDefaults(widgetTab.selectedWidgetRecord())
                    label: "Default size"
                    description: "Applies to text widgets in this overlay"
                    Row {
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        spacing: 6

                        NumberStepper {
                            width: 58
                            value: widgetTab.widgetTypeDefaultValue(widgetTab.selectedWidgetRecord(), "width", 220)
                            step: 10
                            min: 80
                            max: 800
                            enabled: widgetTab.widgetConfigWrite !== null
                            onCommit: v => widgetTab.setWidgetTypeDefault("width", Math.round(v))
                        }

                        NumberStepper {
                            width: 58
                            value: widgetTab.widgetTypeDefaultValue(widgetTab.selectedWidgetRecord(), "height", 72)
                            step: 4
                            min: 32
                            max: 400
                            enabled: widgetTab.widgetConfigWrite !== null
                            onCommit: v => widgetTab.setWidgetTypeDefault("height", Math.round(v))
                        }
                    }
                }

                EditRow {
                    visible: widgetTab.supportsTypeDefaults(widgetTab.selectedWidgetRecord())
                    label: "Default font"
                    description: "Text widget font size"
                    NumberStepper {
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        value: widgetTab.widgetTypeDefaultValue(widgetTab.selectedWidgetRecord(), "fontSize", 18)
                        step: 1
                        min: 8
                        max: 96
                        enabled: widgetTab.widgetConfigWrite !== null
                        onCommit: v => widgetTab.setWidgetTypeDefault("fontSize", Math.round(v))
                    }
                }

                EditRow {
                    visible: widgetTab.supportsTypeDefaults(widgetTab.selectedWidgetRecord())
                    label: "Text color"
                    description: "Default text color"
                    TextInputBox {
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        textValue: widgetTab.widgetTypeDefaultValue(widgetTab.selectedWidgetRecord(), "textColor", "#E8EDF2")
                        enabled: widgetTab.widgetConfigWrite !== null
                        onCommit: text => widgetTab.setWidgetTypeDefault("textColor", text)
                    }
                }

                EditRow {
                    visible: widgetTab.supportsTypeDefaults(widgetTab.selectedWidgetRecord())
                    label: "Background"
                    description: "Default background color"
                    TextInputBox {
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        textValue: widgetTab.widgetTypeDefaultValue(widgetTab.selectedWidgetRecord(), "backgroundColor", "#20242b")
                        enabled: widgetTab.widgetConfigWrite !== null
                        onCommit: text => widgetTab.setWidgetTypeDefault("backgroundColor", text)
                    }
                }

                EditRow {
                    visible: widgetTab.supportsTypeDefaults(widgetTab.selectedWidgetRecord())
                    label: "Reset type defaults"
                    description: "Return text widgets in this overlay to manifest values"
                    ActionButton {
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        label: "Reset"
                        enabled: widgetTab.widgetConfigWrite !== null
                        onClicked: widgetTab.resetWidgetTypeDefaults()
                    }
                }

                EditRow {
                    label: "Border"
                    description: "Draw an outline around the floating widget"
                    ToggleSwitch {
                        anchors.centerIn: parent
                        checked: widgetTab.widgetValue(widgetTab.selectedWidgetRecord(), "borderEnabled", true) !== false
                        enabled: widgetTab.widgetConfigWrite !== null
                        onToggled: v => widgetTab.setWidgetValue("borderEnabled", v)
                    }
                }

                EditRow {
                    label: "Border color"
                    description: "Base border color, before threshold overrides"
                    TextInputBox {
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        textValue: widgetTab.widgetValue(widgetTab.selectedWidgetRecord(), "borderColor", "#40FFFFFF")
                        enabled: widgetTab.widgetConfigWrite !== null
                        onCommit: text => widgetTab.setWidgetValue("borderColor", text)
                    }
                }

                EditRow {
                    label: "Border width"
                    description: "Base border thickness"
                    NumberStepper {
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        value: widgetTab.widgetValue(widgetTab.selectedWidgetRecord(), "borderWidth", 1)
                        step: 1
                        min: 1
                        max: 8
                        enabled: widgetTab.widgetConfigWrite !== null
                        onCommit: v => widgetTab.setWidgetValue("borderWidth", Math.round(v))
                    }
                }

                SectionHeader {
                    text: "Thresholds"
                }

                ThresholdEditor {
                    entries: widgetTab.thresholdEntries(widgetTab.selectedWidgetRecord())
                    editable: widgetTab.widgetConfigWrite !== null
                    theme: widgetTab.theme
                    onUpdateThreshold: (index, key, value) => widgetTab.updateThreshold(index, key, value)
                    onRemoveThreshold: index => widgetTab.removeThreshold(index)
                    onAddThreshold: widgetTab.addThreshold()
                }

                SectionHeader {
                    text: widgetTab.showAdvanced ? "Advanced" : "Advanced (hidden)"

                    MouseArea {
                        anchors.fill: parent
                        onClicked: widgetTab.showAdvanced = !widgetTab.showAdvanced
                    }
                }

                EditRow {
                    visible: widgetTab.showAdvanced
                    label: "Show source"
                    description: "Show the connector source key inside the floating widget"
                    ToggleSwitch {
                        anchors.centerIn: parent
                        checked: widgetTab.widgetValue(widgetTab.selectedWidgetRecord(), "showSource", false) === true
                        enabled: widgetTab.widgetConfigWrite !== null
                        onToggled: v => widgetTab.setWidgetValue("showSource", v)
                    }
                }

                EditRow {
                    visible: widgetTab.showAdvanced
                    label: "Widget ID"
                    value: widgetTab.selectedWidgetId
                }

                EditRow {
                    visible: widgetTab.showAdvanced
                    label: "Overlay"
                    value: widgetTab.selectedOverlayId
                }

                EditRow {
                    visible: widgetTab.showAdvanced
                    label: "Type"
                    value: widgetTab.selectedWidgetRecord() ? widgetTab.selectedWidgetRecord().widgetType : ""
                }

                EditRow {
                    visible: widgetTab.showAdvanced
                    label: "Source"
                    description: widgetTab.selectedWidgetRecord() ? widgetTab.selectedWidgetRecord().source : ""
                }

                EditRow {
                    visible: widgetTab.showAdvanced
                    label: "Resolved"
                    description: widgetTab.selectedWidgetRecord() ? widgetTab.selectedWidgetRecord().resolvedValue : ""
                }
            }
        }
    }

}
