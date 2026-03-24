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
import "../components"

Item {
    id: widgetTab

    readonly property int colName:   200
    readonly property int colToggle:  56
    readonly property int colPad:     16

    property var selectedContext: null

    // ── Left: widget list ──────────────────────────────────────────────────────
    Item {
        id: listPane
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        width: selectedContext ? parent.width * 0.4 : parent.width
        Behavior on width { NumberAnimation { duration: 180; easing.type: Easing.OutCubic } }

        // Header
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
                    width: widgetTab.colName; height: parent.height
                    verticalAlignment: Text.AlignVCenter
                    text: "Widget"; color: theme.text
                    font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
                }
                Text {
                    width: parent.width - widgetTab.colPad - widgetTab.colName - widgetTab.colToggle
                    height: parent.height
                    verticalAlignment: Text.AlignVCenter
                    text: "Description"; color: theme.text
                    font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
                }
            }
            Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: theme.border }
        }

        ListView {
            anchors.top: tableHeader.bottom
            anchors.left: parent.left; anchors.right: parent.right; anchors.bottom: parent.bottom
            clip: true; model: widgetModel; spacing: 0

            delegate: Rectangle {
                id: row
                required property var widgetContext
                required property int index

                readonly property bool isSelected:
                    widgetTab.selectedContext !== null
                    && widgetContext !== null
                    && widgetTab.selectedContext.widgetId === widgetContext.widgetId

                width: ListView.view.width; height: 40
                color: isSelected ? theme.surfaceRaised
                     : (index % 2 === 0 ? theme.surfaceAlt : "transparent")
                Behavior on color { ColorAnimation { duration: 80 } }

                Rectangle { width: 2; height: parent.height; color: theme.accent; visible: row.isSelected }

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

                Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: theme.border; opacity: 0.4 }

                Row {
                    anchors.fill: parent
                    leftPadding: widgetTab.colPad + (row.isSelected ? 8 : 0)
                    Behavior on leftPadding { NumberAnimation { duration: 120 } }

                    Text {
                        width: widgetTab.colName; height: parent.height
                        verticalAlignment: Text.AlignVCenter
                        text: row.widgetContext ? row.widgetContext.title : ""
                        color: row.isSelected ? theme.accent : theme.text
                        font.pixelSize: theme.fontSizeBase; font.family: theme.fontFamily
                        font.weight: row.isSelected ? Font.DemiBold : Font.Normal
                        Behavior on color { ColorAnimation { duration: 80 } }
                    }
                    Text {
                        width: parent.width - widgetTab.colPad - widgetTab.colName - widgetTab.colToggle
                        height: parent.height
                        verticalAlignment: Text.AlignVCenter
                        text: row.widgetContext ? row.widgetContext.description : ""
                        color: rowHover.hovered ? "#dec184" : theme.textMuted
                        font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
                        elide: Text.ElideRight
                        Behavior on color { ColorAnimation { duration: 120 } }
                    }
                    Item {
                        width: widgetTab.colToggle; height: parent.height
                        ToggleSwitch {
                            anchors.centerIn: parent
                            checked: row.widgetContext ? row.widgetContext.visible : true
                            onToggled: (v) => { }  // TODO: wire enable/disable to context
                        }
                    }
                }

                MouseArea {
                    anchors.fill: parent; acceptedButtons: Qt.LeftButton
                    onClicked: widgetTab.selectedContext = row.isSelected ? null : row.widgetContext
                }
                HoverHandler { id: rowHover }
            }
        }
    }

    // ── Divider ───────────────────────────────────────────────────────────────
    Rectangle {
        visible: widgetTab.selectedContext !== null
        anchors.top: parent.top; anchors.bottom: parent.bottom
        x: listPane.width; width: 1
        color: theme.border
    }

    // ── Right: edit panel ─────────────────────────────────────────────────────
    Item {
        id: detailPane
        visible: widgetTab.selectedContext !== null
        anchors.top: parent.top
        anchors.left: listPane.right; anchors.leftMargin: 1
        anchors.right: parent.right; anchors.bottom: parent.bottom
        clip: true

        // Widget title + description header
        Rectangle {
            id: detailHeader
            anchors.top: parent.top; anchors.left: parent.left; anchors.right: parent.right
            height: 56; color: "transparent"

            // Title + description
            Column {
                anchors.left: parent.left; anchors.leftMargin: 16
                anchors.right: demoBtn.left; anchors.rightMargin: 8
                anchors.verticalCenter: parent.verticalCenter
                spacing: 3

                Text {
                    text: widgetTab.selectedContext ? widgetTab.selectedContext.title : ""
                    color: theme.text
                    font.pixelSize: theme.fontSizeBase; font.family: theme.fontFamily
                    font.weight: Font.DemiBold
                }
                Text {
                    text: widgetTab.selectedContext ? widgetTab.selectedContext.description : ""
                    color: theme.textMuted
                    font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
                    elide: Text.ElideRight
                }
            }

            // Demo toggle button — only shown when mockViewModel is available
            Rectangle {
                id: demoBtn
                visible: typeof mockViewModel !== "undefined"
                anchors.right: parent.right; anchors.rightMargin: 12
                anchors.verticalCenter: parent.verticalCenter
                width: 64; height: 26; radius: 4
                color: (typeof mockViewModel !== "undefined" && mockViewModel.active)
                       ? theme.accent
                       : (demoBtnArea.containsMouse ? theme.surfaceRaised : "transparent")
                border.width: 1
                border.color: (typeof mockViewModel !== "undefined" && mockViewModel.active)
                              ? theme.accent : theme.border
                Behavior on color { ColorAnimation { duration: 80 } }

                Text {
                    anchors.centerIn: parent
                    text: (typeof mockViewModel !== "undefined" && mockViewModel.active)
                          ? "■ Demo" : "▶ Demo"
                    color: (typeof mockViewModel !== "undefined" && mockViewModel.active)
                           ? theme.accentText : (demoBtnArea.containsMouse ? theme.text : theme.textMuted)
                    font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
                    font.weight: Font.Medium
                    Behavior on color { ColorAnimation { duration: 80 } }
                }

                MouseArea {
                    id: demoBtnArea
                    anchors.fill: parent; hoverEnabled: true
                    onClicked: if (typeof mockViewModel !== "undefined") mockViewModel.toggle()
                }
            }

            Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: theme.border }
        }

        Flickable {
            anchors.top: detailHeader.bottom
            anchors.left: parent.left; anchors.right: parent.right; anchors.bottom: parent.bottom
            contentHeight: editColumn.implicitHeight + 16
            clip: true

            Column {
                id: editColumn
                anchors.left: parent.left; anchors.right: parent.right
                spacing: 0

                // ── Section: Identity ──────────────────────────────────────────
                SectionHeader { text: "Identity" }

                EditRow {
                    label: "Label"
                    description: "Short text shown on the widget"
                    Rectangle {
                        anchors.right: parent.right; anchors.rightMargin: 0
                        anchors.verticalCenter: parent.verticalCenter
                        width: 120; height: 28; radius: 4
                        color: theme.surfaceFloating
                        border.width: 1
                        border.color: labelInput.activeFocus ? theme.accent : theme.border
                        Behavior on border.color { ColorAnimation { duration: 80 } }

                        TextInput {
                            id: labelInput
                            anchors.fill: parent; anchors.leftMargin: 8; anchors.rightMargin: 8
                            verticalAlignment: TextInput.AlignVCenter
                            text: widgetTab.selectedContext ? widgetTab.selectedContext.label : ""
                            color: theme.text
                            font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
                            selectByMouse: true
                            onActiveFocusChanged: {
                                if (!activeFocus && widgetTab.selectedContext)
                                    widgetTab.selectedContext.setLabel(text)
                            }
                            Keys.onReturnPressed: {
                                if (widgetTab.selectedContext) widgetTab.selectedContext.setLabel(text)
                                focus = false
                            }
                            Keys.onEscapePressed: {
                                if (widgetTab.selectedContext) text = widgetTab.selectedContext.label
                                focus = false
                            }
                            Connections {
                                target: widgetTab
                                function onSelectedContextChanged() {
                                    labelInput.text = widgetTab.selectedContext
                                        ? widgetTab.selectedContext.label : ""
                                }
                            }
                        }
                    }
                }

                EditRow {
                    label: "Position X"
                    NumberStepper {
                        anchors.right: parent.right; anchors.rightMargin: 0
                        anchors.verticalCenter: parent.verticalCenter
                        value: widgetTab.selectedContext ? widgetTab.selectedContext.widgetX : 0
                        step: 1
                        onCommit: (v) => {
                            if (widgetTab.selectedContext)
                                widgetTab.selectedContext.move(v, widgetTab.selectedContext.widgetY)
                        }
                    }
                }

                EditRow {
                    label: "Position Y"
                    NumberStepper {
                        anchors.right: parent.right; anchors.rightMargin: 0
                        anchors.verticalCenter: parent.verticalCenter
                        value: widgetTab.selectedContext ? widgetTab.selectedContext.widgetY : 0
                        step: 1
                        onCommit: (v) => {
                            if (widgetTab.selectedContext)
                                widgetTab.selectedContext.move(widgetTab.selectedContext.widgetX, v)
                        }
                    }
                }

                // ── Section: Flash ─────────────────────────────────────────────
                SectionHeader { text: "Flash" }

                EditRow {
                    label: "Target"
                    description: "Which part blinks: value, label + value, or whole widget"
                    ThemedComboBox {
                        id: flashTargetCombo
                        readonly property var _opts: ["value", "text", "widget"]
                        anchors.right: parent.right; anchors.rightMargin: 0
                        anchors.verticalCenter: parent.verticalCenter
                        model: _opts
                        currentIndex: {
                            var t = widgetTab.selectedContext
                                ? widgetTab.selectedContext.flashTarget : "value"
                            var i = _opts.indexOf(t)
                            return i >= 0 ? i : 0
                        }
                        onActivated: (i) => {
                            if (widgetTab.selectedContext)
                                widgetTab.selectedContext.setFlashTarget(_opts[i])
                        }
                    }
                }

                // ── Section: Demo ──────────────────────────────────────────────
                SectionHeader {
                    text: "Demo"
                    visible: typeof mockViewModel !== "undefined"
                }

                EditRow {
                    visible: typeof mockViewModel !== "undefined"
                    label: "Min"
                    description: "Lowest value in the sweep"
                    NumberStepper {
                        anchors.right: parent.right; anchors.rightMargin: 0
                        anchors.verticalCenter: parent.verticalCenter
                        value: typeof mockViewModel !== "undefined" ? mockViewModel.demoMin : 0
                        step: 1
                        onCommit: (v) => { if (typeof mockViewModel !== "undefined") mockViewModel.setMin(v) }
                    }
                }

                EditRow {
                    visible: typeof mockViewModel !== "undefined"
                    label: "Max"
                    description: "Starting value; sweep resets here"
                    NumberStepper {
                        anchors.right: parent.right; anchors.rightMargin: 0
                        anchors.verticalCenter: parent.verticalCenter
                        value: typeof mockViewModel !== "undefined" ? mockViewModel.demoMax : 100
                        step: 1
                        onCommit: (v) => { if (typeof mockViewModel !== "undefined") mockViewModel.setMax(v) }
                    }
                }

                EditRow {
                    visible: typeof mockViewModel !== "undefined"
                    label: "Speed"
                    description: "Decrease per tick (100 ms)"
                    NumberStepper {
                        anchors.right: parent.right; anchors.rightMargin: 0
                        anchors.verticalCenter: parent.verticalCenter
                        value: typeof mockViewModel !== "undefined" ? mockViewModel.demoSpeed : 0.5
                        step: 0.1
                        onCommit: (v) => { if (typeof mockViewModel !== "undefined") mockViewModel.setSpeed(v) }
                    }
                }

                // ── Section: Thresholds ────────────────────────────────────────
                SectionHeader { text: "Thresholds" }

                // Description row
                Rectangle {
                    anchors.left: parent.left; anchors.right: parent.right
                    height: descText.implicitHeight + 16
                    color: "transparent"

                    Text {
                        id: descText
                        anchors.left: parent.left; anchors.leftMargin: 16
                        anchors.right: parent.right; anchors.rightMargin: 16
                        anchors.verticalCenter: parent.verticalCenter
                        wrapMode: Text.WordWrap
                        text: "Each entry is an upper bound — the widget uses that color while the value is at or below that number. Above all thresholds the default color is used. Enable flash per threshold to blink when in that range."
                        color: theme.textMuted
                        font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
                    }
                    Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: theme.border; opacity: 0.4 }
                }

                // Threshold rows
                Repeater {
                    model: widgetTab.selectedContext ? widgetTab.selectedContext.thresholds : []

                    delegate: Rectangle {
                        id: tRow
                        required property var modelData
                        required property int index

                        anchors.left: parent ? parent.left : undefined
                        anchors.right: parent ? parent.right : undefined
                        height: 44
                        color: "transparent"

                        Rectangle {
                            anchors.fill: parent
                            opacity: tRowHover.hovered ? 1 : 0
                            Behavior on opacity { NumberAnimation { duration: 120 } }
                            gradient: Gradient {
                                orientation: Gradient.Horizontal
                                GradientStop { position: 0.0; color: "transparent" }
                                GradientStop { position: 0.5; color: "transparent" }
                                GradientStop { position: 1.0; color: "#20dec184" }
                            }
                        }
                        Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: theme.border; opacity: 0.4 }

                        // Left: ≥ symbol + value stepper
                        Row {
                            id: tLeft
                            anchors.left: parent.left; anchors.leftMargin: 16
                            anchors.verticalCenter: parent.verticalCenter
                            spacing: 6

                            Text {
                                anchors.verticalCenter: parent.verticalCenter
                                text: "≥"
                                color: theme.textSecondary
                                font.pixelSize: theme.fontSizeBase; font.family: theme.fontFamily
                            }
                            NumberStepper {
                                anchors.verticalCenter: parent.verticalCenter
                                value: tRow.modelData.value
                                step: 0.1
                                onCommit: (v) => {
                                    if (widgetTab.selectedContext)
                                        widgetTab.selectedContext.setThresholdValue(tRow.index, v)
                                }
                            }
                        }

                        // Right: color + flash toggle + flash speed + remove button
                        Row {
                            anchors.right: parent.right; anchors.rightMargin: 12
                            anchors.verticalCenter: parent.verticalCenter
                            spacing: 10

                            ColorPicker {
                                anchors.verticalCenter: parent.verticalCenter
                                value: tRow.modelData.color
                                onColorPicked: (hex) => {
                                    if (widgetTab.selectedContext)
                                        widgetTab.selectedContext.setThresholdColor(tRow.index, hex)
                                }
                            }

                            // Flash speed — only visible when flash is on
                            NumberStepper {
                                visible: tRow.modelData.flash
                                anchors.verticalCenter: parent.verticalCenter
                                value: tRow.modelData.flashSpeed
                                step: 1; min: 1; max: 20
                                onCommit: (v) => {
                                    if (widgetTab.selectedContext)
                                        widgetTab.selectedContext.setThresholdFlashSpeed(tRow.index, v)
                                }
                            }

                            ToggleSwitch {
                                anchors.verticalCenter: parent.verticalCenter
                                checked: tRow.modelData.flash
                                onToggled: (v) => {
                                    if (widgetTab.selectedContext)
                                        widgetTab.selectedContext.setThresholdFlash(tRow.index, v)
                                }
                            }

                            // Remove button
                            Rectangle {
                                anchors.verticalCenter: parent.verticalCenter
                                width: 22; height: 22; radius: 11
                                color: removeArea.containsMouse ? "#40FF4444" : "transparent"
                                border.width: 1
                                border.color: removeArea.containsMouse ? "#FF4444" : theme.border
                                Behavior on color { ColorAnimation { duration: 80 } }

                                Text {
                                    anchors.centerIn: parent
                                    text: "×"
                                    font.pixelSize: 14; font.family: theme.fontFamily
                                    color: removeArea.containsMouse ? "#FF4444" : theme.textMuted
                                    Behavior on color { ColorAnimation { duration: 80 } }
                                }

                                MouseArea {
                                    id: removeArea
                                    anchors.fill: parent; hoverEnabled: true
                                    onClicked: {
                                        if (widgetTab.selectedContext)
                                            widgetTab.selectedContext.removeThreshold(tRow.index)
                                    }
                                }
                            }
                        }

                        HoverHandler { id: tRowHover }
                    }
                }

                // Add threshold button
                Rectangle {
                    anchors.left: parent.left; anchors.right: parent.right
                    height: 40
                    color: "transparent"

                    Rectangle {
                        anchors.left: parent.left; anchors.leftMargin: 16
                        anchors.verticalCenter: parent.verticalCenter
                        width: 120; height: 26; radius: 4
                        color: addArea.containsMouse ? theme.surfaceRaised : "transparent"
                        border.width: 1; border.color: theme.border
                        Behavior on color { ColorAnimation { duration: 80 } }

                        Row {
                            anchors.centerIn: parent
                            spacing: 6
                            Text {
                                anchors.verticalCenter: parent.verticalCenter
                                text: "+"; font.pixelSize: 14; font.family: theme.fontFamily
                                color: addArea.containsMouse ? theme.accent : theme.textMuted
                                Behavior on color { ColorAnimation { duration: 80 } }
                            }
                            Text {
                                anchors.verticalCenter: parent.verticalCenter
                                text: "Add threshold"
                                font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
                                color: addArea.containsMouse ? theme.accent : theme.textMuted
                                Behavior on color { ColorAnimation { duration: 80 } }
                            }
                        }

                        MouseArea {
                            id: addArea
                            anchors.fill: parent; hoverEnabled: true
                            onClicked: {
                                if (!widgetTab.selectedContext) return
                                var ts = widgetTab.selectedContext.thresholds
                                var nextVal = ts.length > 0 ? ts[ts.length - 1].value + 10 : 10
                                widgetTab.selectedContext.addThreshold(nextVal, "#E0E0E0")
                            }
                        }
                    }
                }
            }
        }
    }

    // ── EditRow: matches SettingsDialog row style ──────────────────────────────
    component EditRow: Rectangle {
        id: editRowRoot
        property string label: ""
        property string description: ""
        default property alias rightContent: rightSlot.data

        anchors.left: parent ? parent.left : undefined
        anchors.right: parent ? parent.right : undefined
        implicitHeight: description !== "" ? 52 : 44
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

        Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: theme.border; opacity: 0.4 }

        // Label (+ optional description) — same layout as SettingsDialog
        Column {
            anchors.left: parent.left; anchors.leftMargin: 16
            anchors.right: rightSlot.left; anchors.rightMargin: 8
            anchors.verticalCenter: parent.verticalCenter
            spacing: 3

            Text {
                text: editRowRoot.label
                color: theme.text
                font.pixelSize: theme.fontSizeBase; font.family: theme.fontFamily
            }
            Text {
                visible: editRowRoot.description !== ""
                text: editRowRoot.description
                color: editRowHover.hovered ? "#dec184" : theme.textMuted
                font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
                Behavior on color { ColorAnimation { duration: 120 } }
            }
        }

        // Control slot — 128px, right-aligned with 12px margin
        Item {
            id: rightSlot
            anchors.right: parent.right; anchors.rightMargin: 12
            anchors.verticalCenter: parent.verticalCenter
            width: 128; height: parent.height
        }

        HoverHandler { id: editRowHover }
    }

    // ── SectionHeader: same as SettingsDialog section headers ─────────────────
    component SectionHeader: Rectangle {
        property string text: ""
        anchors.left: parent ? parent.left : undefined
        anchors.right: parent ? parent.right : undefined
        height: 28
        color: theme.surfaceAlt

        Text {
            anchors.left: parent.left; anchors.leftMargin: 16
            anchors.verticalCenter: parent.verticalCenter
            text: parent.text
            color: theme.textSecondary
            font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
            font.weight: Font.Medium
        }
        Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: theme.border }
    }
}
