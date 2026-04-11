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
    readonly property string diagnosticsMessage: !hostWindow
        ? "WidgetTab cannot see the host window."
        : (!widgetRecords
            ? "Widget records are not attached to this window."
            : (widgetCount === 0
                ? "Widget records are attached, but no widgets are available."
                : ""))

    readonly property int colName: 200
    readonly property int colToggle: 56
    readonly property int colPad: 16

    property string selectedWidgetId: ""
    property string selectedOverlayId: ""
    property bool showAdvanced: false

    anchors.fill: parent

    function c(token, fallback) {
        return theme ? theme[token] : fallback
    }

    function f(token, fallback) {
        return theme ? theme[token] : fallback
    }

    function widgets() {
        return widgetItems
    }

    function selectedWidgetRecord() {
        var items = widgets()
        for (var i = 0; i < items.length; i++) {
            if (items[i].widgetId === selectedWidgetId && items[i].overlayId === selectedOverlayId)
                return items[i]
        }
        return null
    }

    function selectWidget(widget) {
        if (!widget)
            return

        if (selectedWidgetId === widget.widgetId && selectedOverlayId === widget.overlayId) {
            clearSelection()
            return
        }

        selectedWidgetId = widget.widgetId
        selectedOverlayId = widget.overlayId

        if (widgetPreviewActions && widgetVisibility && !widgetVisibility.globalVisible)
            widgetPreviewActions.setPreviewVisible(true)
    }

    function isWidgetSelected(widget) {
        return widget
            && selectedWidgetId === widget.widgetId
            && selectedOverlayId === widget.overlayId
    }

    function clearSelection() {
        selectedWidgetId = ""
        selectedOverlayId = ""
    }

    function widgetTitle(widget) {
        if (!widget)
            return ""
        var values = widgetValues(widget)
        return values.title || widget.label || widget.widgetId || ""
    }

    function widgetLabel(widget) {
        if (!widget)
            return ""
        var values = widgetValues(widget)
        return values.label || widget.label || widget.widgetId || ""
    }

    function widgetDescription(widget) {
        if (!widget)
            return ""
        var values = widgetValues(widget)
        if (values.description)
            return values.description
        if (widget.resolvedValue)
            return widget.resolvedValue
        if (widget.source)
            return widget.source
        return widget.status || ""
    }

    function widgetProvider(widget) {
        if (!widget)
            return ""
        if (widget.connectorIds && widget.connectorIds.length > 0)
            return widget.connectorIds.join(", ")
        return widget.overlayId || ""
    }

    function widgetPositionX(widget) {
        return widget && widget.position ? widget.position.x : 0
    }

    function widgetPositionY(widget) {
        return widget && widget.position ? widget.position.y : 0
    }

    function widgetValues(widget) {
        return widget && widget.values ? widget.values : ({})
    }

    function widgetValue(widget, key, fallback) {
        var values = widgetValues(widget)
        return values[key] !== undefined ? values[key] : fallback
    }

    function setWidgetValue(key, value) {
        if (!widgetConfigWrite || selectedOverlayId === "" || selectedWidgetId === "")
            return false
        var values = {}
        values[key] = value
        return widgetConfigWrite.setWidgetValues(selectedOverlayId, selectedWidgetId, values)
    }

    function thresholdEntries(widget) {
        var raw = widgetValue(widget, "thresholds", [])
        var entries = []
        if (!raw || raw.length === undefined)
            return entries
        for (var i = 0; i < raw.length; i++) {
            var item = raw[i]
            if (!item)
                continue
            entries.push({
                "value": Number(item.value !== undefined ? item.value : 0),
                "color": String(item.color !== undefined ? item.color : "#FFB000"),
                "colorTarget": String(item.colorTarget !== undefined ? item.colorTarget : (item.color_target !== undefined ? item.color_target : "value")),
                "flash": item.flash === true,
                "flashSpeed": Number(item.flashSpeed !== undefined ? item.flashSpeed : (item.flash_speed !== undefined ? item.flash_speed : 5)),
                "flashTarget": String(item.flashTarget !== undefined ? item.flashTarget : (item.flash_target !== undefined ? item.flash_target : "value"))
            })
        }
        return entries
    }

    function setThresholdEntries(entries) {
        return setWidgetValue("thresholds", entries)
    }

    function updateThreshold(index, key, value) {
        var entries = thresholdEntries(selectedWidgetRecord())
        if (index < 0 || index >= entries.length)
            return false
        entries[index][key] = value
        return setThresholdEntries(entries)
    }

    function removeThreshold(index) {
        var entries = thresholdEntries(selectedWidgetRecord())
        if (index < 0 || index >= entries.length)
            return false
        entries.splice(index, 1)
        return setThresholdEntries(entries)
    }

    function addThreshold() {
        var entries = thresholdEntries(selectedWidgetRecord())
        entries.push({
            "value": 0,
            "color": "#FFB000",
            "colorTarget": "value",
            "flash": false,
            "flashSpeed": 5,
            "flashTarget": "border"
        })
        return setThresholdEntries(entries)
    }

    function stableString(value) {
        if (value === undefined || value === null)
            return ""
        try {
            return JSON.stringify(value)
        } catch (error) {
            return String(value)
        }
    }

    function widgetListSignature(items) {
        if (!items || items.length === undefined)
            return ""

        var parts = []
        for (var i = 0; i < items.length; i++) {
            var item = items[i]
            if (!item)
                continue
            var position = item.position || ({})
            parts.push([
                item.overlayId || "",
                item.widgetId || "",
                item.widgetType || "",
                item.label || "",
                item.source || "",
                item.status || "",
                item.enabled === true ? "1" : "0",
                position.x !== undefined ? position.x : "",
                position.y !== undefined ? position.y : "",
                stableString(item.values || ({}))
            ].join("|"))
        }
        return parts.join("\n")
    }

    function refreshWidgetItems() {
        var nextItems = widgetRecords ? widgetRecords.widgets : []
        var nextSignature = widgetListSignature(nextItems)
        if (nextSignature === widgetItemsSignature)
            return
        widgetItemsSignature = nextSignature
        widgetItems = nextItems
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
            widgetTab.refreshWidgetItems()
            if (widgetTab.selectedWidgetId !== "" && widgetTab.selectedWidgetRecord() === null) {
                widgetTab.selectedWidgetId = ""
                widgetTab.selectedOverlayId = ""
            }
        }
    }

    Item {
        id: listPane
        z: 2
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        width: widgetTab.selectedWidgetId !== "" ? parent.width * 0.4 : parent.width
        Behavior on width { NumberAnimation { duration: 180; easing.type: Easing.OutCubic } }

        Rectangle {
            id: tableHeader
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            height: 32
            color: "transparent"

            Row {
                anchors.fill: parent
                leftPadding: widgetTab.colPad

                Text {
                    width: widgetTab.colName
                    height: parent.height
                    verticalAlignment: Text.AlignVCenter
                    text: "Widget"
                    color: widgetTab.c("text", "#dce0e5")
                    font.pixelSize: widgetTab.f("fontSizeSmall", 11)
                    font.family: widgetTab.f("fontFamily", "sans-serif")
                }

                Text {
                    width: parent.width - widgetTab.colPad - widgetTab.colName - widgetTab.colToggle
                    height: parent.height
                    verticalAlignment: Text.AlignVCenter
                    text: "Description"
                    color: widgetTab.c("text", "#dce0e5")
                    font.pixelSize: widgetTab.f("fontSizeSmall", 11)
                    font.family: widgetTab.f("fontFamily", "sans-serif")
                    elide: Text.ElideRight
                }

                Text {
                    width: widgetTab.colToggle
                    height: parent.height
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                    text: "On"
                    color: widgetTab.c("text", "#dce0e5")
                    font.pixelSize: widgetTab.f("fontSizeSmall", 11)
                    font.family: widgetTab.f("fontFamily", "sans-serif")
                }
            }

            Rectangle {
                anchors.bottom: parent.bottom
                width: parent.width
                height: 1
                color: widgetTab.c("border", "#464b57")
            }
        }

        ListView {
            id: widgetList
            anchors.top: tableHeader.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            clip: true
            model: widgetTab.widgetItems
            spacing: 0

            delegate: Rectangle {
                id: row
                required property var modelData
                required property int index

                readonly property bool isSelected: widgetTab.isWidgetSelected(modelData)

                width: ListView.view.width
                height: 40
                color: isSelected
                    ? widgetTab.c("surfaceRaised", "#3b414d")
                    : (index % 2 === 0 ? widgetTab.c("surfaceAlt", "#2f343e") : "transparent")
                Behavior on color { ColorAnimation { duration: 80 } }

                Rectangle {
                    width: 2
                    height: parent.height
                    color: widgetTab.c("accent", "#4a9eff")
                    visible: row.isSelected
                }

                Rectangle {
                    anchors.fill: parent
                    opacity: rowHover.hovered && !row.isSelected ? 1 : 0
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
                    color: widgetTab.c("border", "#464b57")
                    opacity: 0.4
                }

                Row {
                    anchors.fill: parent
                    leftPadding: widgetTab.colPad + (row.isSelected ? 8 : 0)
                    Behavior on leftPadding { NumberAnimation { duration: 120 } }

                    Text {
                        width: widgetTab.colName
                        height: parent.height
                        verticalAlignment: Text.AlignVCenter
                        text: widgetTab.widgetLabel(row.modelData)
                        color: row.isSelected ? widgetTab.c("accent", "#4a9eff") : widgetTab.c("text", "#dce0e5")
                        font.pixelSize: widgetTab.f("fontSizeBase", 13)
                        font.family: widgetTab.f("fontFamily", "sans-serif")
                        font.weight: row.isSelected ? Font.DemiBold : Font.Normal
                        elide: Text.ElideRight
                        Behavior on color { ColorAnimation { duration: 80 } }
                    }

                    Text {
                        width: parent.width - widgetTab.colPad - widgetTab.colName - widgetTab.colToggle
                        height: parent.height
                        verticalAlignment: Text.AlignVCenter
                        text: widgetTab.widgetDescription(row.modelData)
                        color: rowHover.hovered ? "#dec184" : widgetTab.c("textMuted", "#878a98")
                        font.pixelSize: widgetTab.f("fontSizeSmall", 11)
                        font.family: widgetTab.f("fontFamily", "sans-serif")
                        elide: Text.ElideRight
                        Behavior on color { ColorAnimation { duration: 120 } }
                    }

                    Item {
                        width: widgetTab.colToggle
                        height: parent.height

                        ToggleSwitch {
                            anchors.centerIn: parent
                            checked: row.modelData ? row.modelData.enabled : true
                            enabled: widgetTab.widgetConfigWrite !== null
                                && row.modelData
                                && row.modelData.overlayId !== undefined
                            onToggled: (v) => {
                                if (widgetTab.widgetConfigWrite && row.modelData && row.modelData.overlayId !== undefined) {
                                    widgetTab.widgetConfigWrite.setWidgetEnabled(
                                        row.modelData.overlayId,
                                        row.modelData.widgetId,
                                        v
                                    )
                                }
                            }
                        }
                    }
                }

                MouseArea {
                    anchors.fill: parent
                    anchors.rightMargin: widgetTab.colToggle
                    acceptedButtons: Qt.LeftButton
                    onClicked: widgetTab.selectWidget(row.modelData)
                }

                HoverHandler { id: rowHover }
            }
        }

        Rectangle {
            anchors.top: tableHeader.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            visible: widgetTab.diagnosticsMessage !== ""
            color: "transparent"

            Column {
                anchors.centerIn: parent
                width: Math.min(parent.width - 32, 420)
                spacing: 8

                Text {
                    width: parent.width
                    horizontalAlignment: Text.AlignHCenter
                    text: "No widgets found"
                    color: widgetTab.c("text", "#dce0e5")
                    font.pixelSize: widgetTab.f("fontSizeBase", 13)
                    font.family: widgetTab.f("fontFamily", "sans-serif")
                    font.weight: Font.DemiBold
                }

                Text {
                    width: parent.width
                    horizontalAlignment: Text.AlignHCenter
                    text: widgetTab.diagnosticsMessage
                    color: widgetTab.c("textMuted", "#878a98")
                    font.pixelSize: widgetTab.f("fontSizeSmall", 11)
                    font.family: widgetTab.f("fontFamily", "sans-serif")
                    wrapMode: Text.WordWrap
                }
            }
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
        Behavior on opacity { NumberAnimation { duration: 120 } }

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
                anchors.rightMargin: 48
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

                Text {
                    anchors.centerIn: parent
                    text: "x"
                    color: widgetTab.c("text", "#dce0e5")
                    font.pixelSize: widgetTab.f("fontSizeBase", 13)
                    font.family: widgetTab.f("fontFamily", "sans-serif")
                    font.weight: Font.DemiBold
                }

                MouseArea {
                    anchors.fill: parent
                    acceptedButtons: Qt.LeftButton
                    onClicked: widgetTab.clearSelection()
                }

                HoverHandler { id: closeHover }
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

                SectionHeader { text: "Identity" }

                EditRow {
                    label: "Label"
                    description: "Short text shown on the widget"
                    TextInputBox {
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        textValue: widgetTab.widgetLabel(widgetTab.selectedWidgetRecord())
                        enabled: widgetTab.widgetConfigWrite !== null
                        onCommit: (text) => widgetTab.setWidgetValue("label", text)
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

                SectionHeader { text: "Position" }

                EditRow {
                    label: "Position X"
                    NumberStepper {
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        value: widgetTab.widgetPositionX(widgetTab.selectedWidgetRecord())
                        enabled: widgetTab.selectedOverlayId !== "" && widgetTab.widgetConfigWrite !== null
                        onCommit: (v) => {
                            if (widgetTab.widgetConfigWrite && widgetTab.selectedOverlayId !== "") {
                                widgetTab.widgetConfigWrite.setWidgetPosition(
                                    widgetTab.selectedOverlayId,
                                    widgetTab.selectedWidgetId,
                                    v,
                                    widgetTab.widgetPositionY(widgetTab.selectedWidgetRecord())
                                )
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
                        onCommit: (v) => {
                            if (widgetTab.widgetConfigWrite && widgetTab.selectedOverlayId !== "") {
                                widgetTab.widgetConfigWrite.setWidgetPosition(
                                    widgetTab.selectedOverlayId,
                                    widgetTab.selectedWidgetId,
                                    widgetTab.widgetPositionX(widgetTab.selectedWidgetRecord()),
                                    v
                                )
                            }
                        }
                    }
                }

                SectionHeader { text: "Provider" }

                EditRow {
                    label: "Binding"
                    description: widgetTab.widgetProvider(widgetTab.selectedWidgetRecord())
                }

                EditRow {
                    label: "Mode"
                    description: widgetTab.selectedWidgetRecord()
                        ? widgetTab.selectedWidgetRecord().status
                        : ""
                }

                SectionHeader { text: "Style" }

                EditRow {
                    label: "Border"
                    description: "Draw an outline around the floating widget"
                    ToggleSwitch {
                        anchors.centerIn: parent
                        checked: widgetTab.widgetValue(widgetTab.selectedWidgetRecord(), "borderEnabled", true) !== false
                        enabled: widgetTab.widgetConfigWrite !== null
                        onToggled: (v) => widgetTab.setWidgetValue("borderEnabled", v)
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
                        onCommit: (text) => widgetTab.setWidgetValue("borderColor", text)
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
                        onCommit: (v) => widgetTab.setWidgetValue("borderWidth", Math.round(v))
                    }
                }

                SectionHeader { text: "Thresholds" }

                ThresholdEditor {
                    widget: widgetTab.selectedWidgetRecord()
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
                        onToggled: (v) => widgetTab.setWidgetValue("showSource", v)
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
                    value: widgetTab.selectedWidgetRecord()
                        ? widgetTab.selectedWidgetRecord().widgetType
                        : ""
                }

                EditRow {
                    visible: widgetTab.showAdvanced
                    label: "Source"
                    description: widgetTab.selectedWidgetRecord()
                        ? widgetTab.selectedWidgetRecord().source
                        : ""
                }

                EditRow {
                    visible: widgetTab.showAdvanced
                    label: "Resolved"
                    description: widgetTab.selectedWidgetRecord()
                        ? widgetTab.selectedWidgetRecord().resolvedValue
                        : ""
                }
            }
        }
    }

    component EditRow: Rectangle {
        id: editRowRoot
        property string label: ""
        property string description: ""
        property string value: ""
        default property alias rightContent: rightSlot.data

        anchors.left: parent ? parent.left : undefined
        anchors.right: parent ? parent.right : undefined
        implicitHeight: visible ? (description !== "" || value !== "" ? 52 : 44) : 0
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
            color: widgetTab.c("border", "#464b57")
            opacity: 0.4
        }

        Column {
            anchors.left: parent.left
            anchors.leftMargin: 16
            anchors.right: rightSlot.left
            anchors.rightMargin: 8
            anchors.verticalCenter: parent.verticalCenter
            spacing: 3

            Text {
                width: parent.width
                text: editRowRoot.label
                color: widgetTab.c("text", "#dce0e5")
                font.pixelSize: widgetTab.f("fontSizeBase", 13)
                font.family: widgetTab.f("fontFamily", "sans-serif")
                elide: Text.ElideRight
            }

            Text {
                width: parent.width
                visible: editRowRoot.description !== "" || editRowRoot.value !== ""
                text: editRowRoot.description !== "" ? editRowRoot.description : editRowRoot.value
                color: editRowHover.hovered ? "#dec184" : widgetTab.c("textMuted", "#878a98")
                font.pixelSize: widgetTab.f("fontSizeSmall", 11)
                font.family: widgetTab.f("fontFamily", "sans-serif")
                elide: Text.ElideRight
                Behavior on color { ColorAnimation { duration: 120 } }
            }
        }

        Item {
            id: rightSlot
            anchors.right: parent.right
            anchors.rightMargin: 12
            anchors.verticalCenter: parent.verticalCenter
            width: 128
            height: parent.height
        }

        HoverHandler { id: editRowHover }
    }

    component SectionHeader: Rectangle {
        id: sectionHeaderRoot
        property string text: ""

        anchors.left: parent ? parent.left : undefined
        anchors.right: parent ? parent.right : undefined
        height: 28
        color: widgetTab.c("surfaceAlt", "#2f343e")

        Text {
            anchors.left: parent.left
            anchors.leftMargin: 16
            anchors.verticalCenter: parent.verticalCenter
            text: sectionHeaderRoot.text
            color: widgetTab.c("textSecondary", "#a9afbc")
            font.pixelSize: widgetTab.f("fontSizeSmall", 11)
            font.family: widgetTab.f("fontFamily", "sans-serif")
            font.weight: Font.Medium
        }

        Rectangle {
            anchors.bottom: parent.bottom
            width: parent.width
            height: 1
            color: widgetTab.c("border", "#464b57")
        }
    }

    component ThresholdEditor: Column {
        id: thresholdEditorRoot
        property var widget: null
        readonly property var entries: widgetTab.thresholdEntries(widget)

        anchors.left: parent ? parent.left : undefined
        anchors.right: parent ? parent.right : undefined

        Rectangle {
            anchors.left: parent.left
            anchors.right: parent.right
            height: thresholdDescription.implicitHeight + 16
            color: "transparent"

            Text {
                id: thresholdDescription
                anchors.left: parent.left
                anchors.leftMargin: 16
                anchors.right: parent.right
                anchors.rightMargin: 16
                anchors.verticalCenter: parent.verticalCenter
                wrapMode: Text.WordWrap
                text: "Each entry is an upper bound. The color is used while the value is at or below that number; flash can hide the selected target on each tick."
                color: widgetTab.c("textMuted", "#878a98")
                font.pixelSize: widgetTab.f("fontSizeSmall", 11)
                font.family: widgetTab.f("fontFamily", "sans-serif")
            }

            Rectangle {
                anchors.bottom: parent.bottom
                width: parent.width
                height: 1
                color: widgetTab.c("border", "#464b57")
                opacity: 0.4
            }
        }

        Repeater {
            model: thresholdEditorRoot.entries

            delegate: Column {
                id: thresholdEntry
                required property var modelData
                required property int index
                readonly property var targets: ["value", "text", "widget", "border"]

                anchors.left: parent ? parent.left : undefined
                anchors.right: parent ? parent.right : undefined

                Rectangle {
                    id: thresholdRow
                    anchors.left: parent.left
                    anchors.right: parent.right
                    height: 44
                    color: "transparent"

                    Rectangle {
                        anchors.fill: parent
                        opacity: thresholdHover.hovered ? 1 : 0
                        Behavior on opacity { NumberAnimation { duration: 120 } }
                        gradient: Gradient {
                            orientation: Gradient.Horizontal
                            GradientStop { position: 0.0; color: "transparent" }
                            GradientStop { position: 0.6; color: "transparent" }
                            GradientStop { position: 1.0; color: "#20dec184" }
                        }
                    }

                    Row {
                        anchors.left: parent.left
                        anchors.leftMargin: 16
                        anchors.verticalCenter: parent.verticalCenter
                        spacing: 8

                        Rectangle {
                            width: 18
                            height: 18
                            radius: 9
                            anchors.verticalCenter: parent.verticalCenter
                            color: thresholdEntry.modelData.color
                            border.width: 1
                            border.color: widgetTab.c("border", "#464b57")

                            Text {
                                anchors.centerIn: parent
                                text: thresholdEntry.index + 1
                                color: "#ffffff"
                                font.pixelSize: 9
                                font.family: widgetTab.f("fontFamily", "sans-serif")
                                font.weight: Font.Bold
                            }
                        }

                        Text {
                            anchors.verticalCenter: parent.verticalCenter
                            text: "<="
                            color: widgetTab.c("textSecondary", "#a9afbc")
                            font.pixelSize: widgetTab.f("fontSizeBase", 13)
                            font.family: widgetTab.f("fontFamily", "sans-serif")
                        }

                        NumberStepper {
                            anchors.verticalCenter: parent.verticalCenter
                            width: 80
                            value: thresholdEntry.modelData.value
                            step: 0.5
                            decimals: 1
                            enabled: widgetTab.widgetConfigWrite !== null
                            onCommit: (v) => widgetTab.updateThreshold(thresholdEntry.index, "value", v)
                        }
                    }

                    Row {
                        anchors.right: parent.right
                        anchors.rightMargin: 12
                        anchors.verticalCenter: parent.verticalCenter
                        spacing: 8

                        TextInputBox {
                            width: 82
                            anchors.verticalCenter: parent.verticalCenter
                            textValue: thresholdEntry.modelData.color
                            enabled: widgetTab.widgetConfigWrite !== null
                            onCommit: (text) => widgetTab.updateThreshold(thresholdEntry.index, "color", text)
                        }

                        Text {
                            anchors.verticalCenter: parent.verticalCenter
                            text: "Flash"
                            color: widgetTab.c("textMuted", "#878a98")
                            font.pixelSize: widgetTab.f("fontSizeSmall", 11)
                            font.family: widgetTab.f("fontFamily", "sans-serif")
                        }

                        ToggleSwitch {
                            anchors.verticalCenter: parent.verticalCenter
                            checked: thresholdEntry.modelData.flash === true
                            enabled: widgetTab.widgetConfigWrite !== null
                            onToggled: (v) => widgetTab.updateThreshold(thresholdEntry.index, "flash", v)
                        }

                        Rectangle {
                            anchors.verticalCenter: parent.verticalCenter
                            width: 22
                            height: 22
                            radius: 4
                            color: removeHover.hovered ? "#40FF4444" : "transparent"
                            border.width: 1
                            border.color: removeHover.hovered ? "#FF4444" : widgetTab.c("border", "#464b57")
                            Behavior on color { ColorAnimation { duration: 80 } }
                            Behavior on border.color { ColorAnimation { duration: 80 } }

                            Text {
                                anchors.centerIn: parent
                                text: "x"
                                color: removeHover.hovered ? "#FF4444" : widgetTab.c("textMuted", "#878a98")
                                font.pixelSize: widgetTab.f("fontSizeBase", 13)
                                font.family: widgetTab.f("fontFamily", "sans-serif")
                            }

                            MouseArea {
                                anchors.fill: parent
                                enabled: widgetTab.widgetConfigWrite !== null
                                onClicked: widgetTab.removeThreshold(thresholdEntry.index)
                            }

                            HoverHandler { id: removeHover }
                        }
                    }

                    HoverHandler { id: thresholdHover }
                }

                Rectangle {
                    anchors.left: parent.left
                    anchors.right: parent.right
                    height: thresholdEntry.modelData.flash === true ? 72 : 36
                    clip: true
                    color: widgetTab.c("surfaceAlt", "#2f343e")
                    opacity: 1

                    Behavior on height { NumberAnimation { duration: 150; easing.type: Easing.OutCubic } }

                    Column {
                        anchors.left: parent.left
                        anchors.leftMargin: 44
                        anchors.right: parent.right
                        anchors.rightMargin: 12
                        anchors.verticalCenter: parent.verticalCenter
                        spacing: 6

                        Row {
                            spacing: 10

                            Text {
                                anchors.verticalCenter: parent.verticalCenter
                                width: 44
                                text: "Color"
                                color: widgetTab.c("textMuted", "#878a98")
                                font.pixelSize: widgetTab.f("fontSizeSmall", 11)
                                font.family: widgetTab.f("fontFamily", "sans-serif")
                            }

                            TargetPicker {
                                anchors.verticalCenter: parent.verticalCenter
                                targets: thresholdEntry.targets
                                value: thresholdEntry.modelData.colorTarget
                                enabled: widgetTab.widgetConfigWrite !== null
                                onPicked: (value) => widgetTab.updateThreshold(thresholdEntry.index, "colorTarget", value)
                            }
                        }

                        Row {
                            visible: thresholdEntry.modelData.flash === true
                            spacing: 10

                            Text {
                                anchors.verticalCenter: parent.verticalCenter
                                width: 44
                                text: "Flash"
                                color: widgetTab.c("textMuted", "#878a98")
                                font.pixelSize: widgetTab.f("fontSizeSmall", 11)
                                font.family: widgetTab.f("fontFamily", "sans-serif")
                            }

                            TargetPicker {
                                anchors.verticalCenter: parent.verticalCenter
                                targets: thresholdEntry.targets
                                value: thresholdEntry.modelData.flashTarget
                                enabled: widgetTab.widgetConfigWrite !== null
                                onPicked: (value) => widgetTab.updateThreshold(thresholdEntry.index, "flashTarget", value)
                            }

                            Text {
                                anchors.verticalCenter: parent.verticalCenter
                                text: "Speed"
                                color: widgetTab.c("textMuted", "#878a98")
                                font.pixelSize: widgetTab.f("fontSizeSmall", 11)
                                font.family: widgetTab.f("fontFamily", "sans-serif")
                            }

                            NumberStepper {
                                anchors.verticalCenter: parent.verticalCenter
                                width: 80
                                value: thresholdEntry.modelData.flashSpeed
                                step: 1
                                min: 1
                                max: 20
                                enabled: widgetTab.widgetConfigWrite !== null
                                onCommit: (v) => widgetTab.updateThreshold(thresholdEntry.index, "flashSpeed", Math.round(v))
                            }
                        }
                    }
                }

                Rectangle {
                    anchors.left: parent.left
                    anchors.right: parent.right
                    height: 1
                    color: widgetTab.c("border", "#464b57")
                    opacity: 0.4
                }
            }
        }

        Rectangle {
            anchors.left: parent.left
            anchors.right: parent.right
            height: 40
            color: "transparent"

            Rectangle {
                anchors.left: parent.left
                anchors.leftMargin: 16
                anchors.verticalCenter: parent.verticalCenter
                width: 130
                height: 26
                radius: 4
                color: addHover.hovered ? widgetTab.c("surfaceRaised", "#3b414d") : "transparent"
                border.width: 1
                border.color: widgetTab.c("border", "#464b57")
                Behavior on color { ColorAnimation { duration: 80 } }

                Row {
                    anchors.centerIn: parent
                    spacing: 6

                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        text: "+"
                        color: addHover.hovered ? widgetTab.c("accent", "#4a9eff") : widgetTab.c("textMuted", "#878a98")
                        font.pixelSize: widgetTab.f("fontSizeBase", 13)
                        font.family: widgetTab.f("fontFamily", "sans-serif")
                    }

                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        text: "Add threshold"
                        color: addHover.hovered ? widgetTab.c("accent", "#4a9eff") : widgetTab.c("textMuted", "#878a98")
                        font.pixelSize: widgetTab.f("fontSizeSmall", 11)
                        font.family: widgetTab.f("fontFamily", "sans-serif")
                    }
                }

                MouseArea {
                    anchors.fill: parent
                    enabled: widgetTab.widgetConfigWrite !== null
                    onClicked: widgetTab.addThreshold()
                }

                HoverHandler { id: addHover }
            }
        }
    }

    component NumberStepper: Rectangle {
        id: stepperRoot
        property real value: 0
        property real step: 1
        property real min: -999999
        property real max: 999999
        property int decimals: 0
        signal commit(real value)

        function clamped(nextValue) {
            return Math.max(min, Math.min(max, nextValue))
        }

        function rounded(nextValue) {
            var factor = Math.pow(10, decimals)
            return Math.round(nextValue * factor) / factor
        }

        function formatted(nextValue) {
            return decimals > 0 ? Number(nextValue).toFixed(decimals) : String(Math.round(nextValue))
        }

        width: 120
        height: 28
        radius: 4
        color: enabled ? widgetTab.c("surfaceFloating", "#20242b") : widgetTab.c("surfaceAlt", "#2f343e")
        border.width: 1
        border.color: valueInput.activeFocus ? widgetTab.c("accent", "#4a9eff") : widgetTab.c("border", "#464b57")
        opacity: enabled ? 1 : 0.6
        Behavior on border.color { ColorAnimation { duration: 80 } }

        Row {
            anchors.fill: parent

            StepperButton {
                label: "-"
                enabled: stepperRoot.enabled
                onPressed: {
                    stepperRoot.value = stepperRoot.rounded(stepperRoot.clamped(stepperRoot.value - stepperRoot.step))
                    stepperRoot.commit(stepperRoot.value)
                }
            }

            TextInput {
                id: valueInput
                width: parent.width - 48
                height: parent.height
                verticalAlignment: TextInput.AlignVCenter
                horizontalAlignment: TextInput.AlignHCenter
                color: widgetTab.c("text", "#dce0e5")
                font.pixelSize: widgetTab.f("fontSizeSmall", 11)
                font.family: widgetTab.f("fontFamily", "sans-serif")
                selectByMouse: true
                validator: DoubleValidator {
                    bottom: stepperRoot.min
                    top: stepperRoot.max
                    decimals: stepperRoot.decimals
                    notation: DoubleValidator.StandardNotation
                }
                enabled: stepperRoot.enabled
                text: stepperRoot.formatted(stepperRoot.value)
                onEditingFinished: {
                    var parsed = parseFloat(text)
                    if (!isNaN(parsed)) {
                        stepperRoot.value = stepperRoot.rounded(stepperRoot.clamped(parsed))
                        stepperRoot.commit(stepperRoot.value)
                    } else {
                        text = stepperRoot.formatted(stepperRoot.value)
                    }
                }
            }

            StepperButton {
                label: "+"
                enabled: stepperRoot.enabled
                onPressed: {
                    stepperRoot.value = stepperRoot.rounded(stepperRoot.clamped(stepperRoot.value + stepperRoot.step))
                    stepperRoot.commit(stepperRoot.value)
                }
            }
        }
    }

    component TargetPicker: Row {
        id: targetPickerRoot
        property var targets: []
        property string value: ""
        signal picked(string value)

        spacing: 4

        Repeater {
            model: targetPickerRoot.targets

            delegate: TargetChip {
                required property string modelData

                label: modelData
                checked: targetPickerRoot.value === modelData
                enabled: targetPickerRoot.enabled
                onPicked: {
                    targetPickerRoot.value = modelData
                    targetPickerRoot.picked(modelData)
                }
            }
        }
    }

    component TargetChip: Rectangle {
        id: targetChipRoot
        property string label: ""
        property bool checked: false
        signal picked()

        width: chipText.implicitWidth + 16
        height: 26
        radius: 4
        color: checked ? widgetTab.c("surfaceRaised", "#3b414d") : widgetTab.c("surfaceFloating", "#20242b")
        border.width: 1
        border.color: checked ? widgetTab.c("accent", "#4a9eff") : (chipHover.hovered ? widgetTab.c("accentHover", "#6bb6ff") : widgetTab.c("border", "#464b57"))
        opacity: enabled ? 1 : 0.6
        Behavior on color { ColorAnimation { duration: 80 } }
        Behavior on border.color { ColorAnimation { duration: 80 } }

        Text {
            id: chipText
            anchors.centerIn: parent
            text: (targetChipRoot.checked ? "v " : "") + targetChipRoot.label
            color: targetChipRoot.checked ? widgetTab.c("accent", "#4a9eff") : widgetTab.c("text", "#dce0e5")
            font.pixelSize: widgetTab.f("fontSizeSmall", 11)
            font.family: widgetTab.f("fontFamily", "sans-serif")
        }

        MouseArea {
            anchors.fill: parent
            enabled: targetChipRoot.enabled
            onClicked: targetChipRoot.picked()
        }

        HoverHandler { id: chipHover }
    }

    component TextInputBox: Rectangle {
        id: textInputBoxRoot
        property string textValue: ""
        signal commit(string text)

        width: 120
        height: 28
        radius: 4
        color: enabled ? widgetTab.c("surfaceFloating", "#20242b") : widgetTab.c("surfaceAlt", "#2f343e")
        border.width: 1
        border.color: textInput.activeFocus ? widgetTab.c("accent", "#4a9eff") : widgetTab.c("border", "#464b57")
        opacity: enabled ? 1 : 0.6
        Behavior on border.color { ColorAnimation { duration: 80 } }

        TextInput {
            id: textInput
            anchors.fill: parent
            anchors.leftMargin: 8
            anchors.rightMargin: 8
            verticalAlignment: TextInput.AlignVCenter
            text: textInputBoxRoot.textValue
            color: widgetTab.c("text", "#dce0e5")
            font.pixelSize: widgetTab.f("fontSizeSmall", 11)
            font.family: widgetTab.f("fontFamily", "sans-serif")
            selectByMouse: true
            enabled: textInputBoxRoot.enabled

            onEditingFinished: {
                textInputBoxRoot.textValue = text
                textInputBoxRoot.commit(text)
            }
        }
    }

    component StepperButton: Item {
        id: stepperButtonRoot
        property string label: ""
        signal pressed()

        width: 24
        height: parent ? parent.height : 28
        opacity: enabled ? 1 : 0.5

        Rectangle {
            anchors.fill: parent
            color: stepperHover.hovered ? widgetTab.c("surfaceRaised", "#3b414d") : "transparent"
            Behavior on color { ColorAnimation { duration: 80 } }
        }

        Text {
            anchors.centerIn: parent
            text: stepperButtonRoot.label
            color: widgetTab.c("textSecondary", "#a9afbc")
            font.pixelSize: widgetTab.f("fontSizeBase", 13)
            font.family: widgetTab.f("fontFamily", "sans-serif")
        }

        MouseArea {
            anchors.fill: parent
            enabled: stepperButtonRoot.enabled
            onClicked: stepperButtonRoot.pressed()
        }

        HoverHandler { id: stepperHover }
    }

    component ToggleSwitch: Item {
        id: toggleRoot
        property bool checked: false
        signal toggled(bool checked)

        width: 34
        height: 18
        opacity: enabled ? 1 : 0.45

        Rectangle {
            anchors.fill: parent
            radius: height / 2
            color: toggleRoot.checked ? widgetTab.c("accent", "#4a9eff") : widgetTab.c("surfaceFloating", "#20242b")
            border.width: 1
            border.color: toggleRoot.checked ? widgetTab.c("accentHover", "#6bb6ff") : widgetTab.c("border", "#464b57")
            Behavior on color { ColorAnimation { duration: 100 } }
            Behavior on border.color { ColorAnimation { duration: 100 } }
        }

        Rectangle {
            width: 14
            height: 14
            radius: 7
            y: 2
            x: toggleRoot.checked ? toggleRoot.width - width - 2 : 2
            color: toggleRoot.checked ? widgetTab.c("accentText", "#ffffff") : widgetTab.c("textMuted", "#878a98")
            Behavior on x { NumberAnimation { duration: 120; easing.type: Easing.OutCubic } }
            Behavior on color { ColorAnimation { duration: 100 } }
        }

        MouseArea {
            anchors.fill: parent
            enabled: toggleRoot.enabled
            onClicked: {
                toggleRoot.checked = !toggleRoot.checked
                toggleRoot.toggled(toggleRoot.checked)
            }
        }
    }
}
