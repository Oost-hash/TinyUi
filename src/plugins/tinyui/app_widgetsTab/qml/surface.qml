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

    readonly property var hostWindow: Window.window
    readonly property var theme: hostWindow && hostWindow.theme ? hostWindow.theme : null
    readonly property var widgetRecords: hostWindow && hostWindow.widgetRecords ? hostWindow.widgetRecords : null
    readonly property var widgetConfigRead: hostWindow && hostWindow.widgetConfigRead ? hostWindow.widgetConfigRead : null
    readonly property var widgetConfigWrite: hostWindow && hostWindow.widgetConfigWrite ? hostWindow.widgetConfigWrite : null
    readonly property var widgetVisibility: hostWindow && hostWindow.widgetVisibility ? hostWindow.widgetVisibility : null

    readonly property int colName: 200
    readonly property int colToggle: 56
    readonly property int colPad: 16

    property string selectedWidgetId: ""
    property string selectedOverlayId: ""

    anchors.fill: parent

    function c(token, fallback) {
        return theme ? theme[token] : fallback
    }

    function f(token, fallback) {
        return theme ? theme[token] : fallback
    }

    function widgets() {
        return widgetRecords ? widgetRecords.widgets : []
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
            selectedWidgetId = ""
            selectedOverlayId = ""
            return
        }

        selectedWidgetId = widget.widgetId
        selectedOverlayId = widget.overlayId

        if (widgetVisibility && !widgetVisibility.globalVisible)
            widgetVisibility.setGlobalVisible(true)
    }

    function isWidgetSelected(widget) {
        return widget
            && selectedWidgetId === widget.widgetId
            && selectedOverlayId === widget.overlayId
    }

    function widgetTitle(widget) {
        if (!widget)
            return ""
        return widget.label || widget.widgetId || ""
    }

    function widgetDescription(widget) {
        if (!widget)
            return ""
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

    Rectangle {
        anchors.fill: parent
        color: widgetTab.c("surface", "#17181c")
    }

    Connections {
        target: widgetTab.widgetRecords
        function onWidgetsChanged() {
            if (widgetTab.selectedWidgetId !== "" && widgetTab.selectedWidgetRecord() === null) {
                widgetTab.selectedWidgetId = ""
                widgetTab.selectedOverlayId = ""
            }
        }
    }

    Item {
        id: listPane
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
            model: widgetTab.widgets()
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
                        text: widgetTab.widgetTitle(row.modelData)
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
    }

    Rectangle {
        visible: widgetTab.selectedWidgetId !== ""
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        x: listPane.width
        width: 1
        color: widgetTab.c("border", "#464b57")
    }

    Item {
        id: detailPane
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
                anchors.rightMargin: 16
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
                    value: widgetTab.widgetTitle(widgetTab.selectedWidgetRecord())
                }

                EditRow {
                    label: "Widget ID"
                    value: widgetTab.selectedWidgetId
                }

                EditRow {
                    label: "Overlay"
                    value: widgetTab.selectedOverlayId
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

                SectionHeader { text: "Runtime" }

                EditRow {
                    label: "Type"
                    value: widgetTab.selectedWidgetRecord()
                        ? widgetTab.selectedWidgetRecord().widgetType
                        : ""
                }

                EditRow {
                    label: "Source"
                    description: widgetTab.selectedWidgetRecord()
                        ? widgetTab.selectedWidgetRecord().source
                        : ""
                }

                EditRow {
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
        implicitHeight: description !== "" || value !== "" ? 52 : 44
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

    component NumberStepper: Rectangle {
        id: stepperRoot
        property int value: 0
        property int step: 1
        signal commit(int value)

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
                    stepperRoot.value = stepperRoot.value - stepperRoot.step
                    stepperRoot.commit(stepperRoot.value)
                }
            }

            TextInput {
                id: valueInput
                width: parent.width - 48
                height: parent.height
                verticalAlignment: TextInput.AlignVCenter
                horizontalAlignment: TextInput.AlignHCenter
                text: String(stepperRoot.value)
                color: widgetTab.c("text", "#dce0e5")
                font.pixelSize: widgetTab.f("fontSizeSmall", 11)
                font.family: widgetTab.f("fontFamily", "sans-serif")
                selectByMouse: true
                validator: IntValidator {}
                enabled: stepperRoot.enabled
                onEditingFinished: {
                    var parsed = parseInt(text)
                    if (!isNaN(parsed)) {
                        stepperRoot.value = parsed
                        stepperRoot.commit(parsed)
                    } else {
                        text = String(stepperRoot.value)
                    }
                }
            }

            StepperButton {
                label: "+"
                enabled: stepperRoot.enabled
                onPressed: {
                    stepperRoot.value = stepperRoot.value + stepperRoot.step
                    stepperRoot.commit(stepperRoot.value)
                }
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
