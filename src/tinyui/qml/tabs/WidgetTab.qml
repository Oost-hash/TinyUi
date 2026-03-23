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

    // Currently selected widget context — null when nothing selected
    property var selectedContext: null

    // ── Left: widget list ──────────────────────────────────────────────────────
    Item {
        id: listPane
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        width: selectedContext ? parent.width * 0.4 : parent.width
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
                    color: theme.text
                    font.pixelSize: theme.fontSizeSmall
                    font.family: theme.fontFamily
                }

                Text {
                    width: parent.width - widgetTab.colPad - widgetTab.colName - widgetTab.colToggle
                    height: parent.height
                    verticalAlignment: Text.AlignVCenter
                    text: "Description"
                    color: theme.text
                    font.pixelSize: theme.fontSizeSmall
                    font.family: theme.fontFamily
                }
            }

            Rectangle {
                anchors.bottom: parent.bottom
                width: parent.width; height: 1
                color: theme.border
            }
        }

        ListView {
            anchors.top: tableHeader.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            clip: true
            model: widgetModel
            spacing: 0

            delegate: Rectangle {
                id: row

                required property var widgetContext
                required property int index

                property bool widgetEnabled: widgetContext ? widgetContext.visible : true

                readonly property bool isSelected:
                    widgetTab.selectedContext !== null
                    && widgetContext !== null
                    && widgetTab.selectedContext.widgetId === widgetContext.widgetId

                width: ListView.view.width
                height: 40
                color: isSelected
                    ? theme.surfaceRaised
                    : (index % 2 === 0 ? theme.surfaceAlt : "transparent")

                Behavior on color { ColorAnimation { duration: 80 } }

                Rectangle {
                    width: 2; height: parent.height
                    color: theme.accent
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
                    width: parent.width; height: 1
                    color: theme.border; opacity: 0.4
                }

                Row {
                    anchors.fill: parent
                    leftPadding: widgetTab.colPad + (row.isSelected ? 8 : 0)
                    Behavior on leftPadding { NumberAnimation { duration: 120 } }

                    Text {
                        width: widgetTab.colName
                        height: parent.height
                        verticalAlignment: Text.AlignVCenter
                        text: row.widgetContext ? row.widgetContext.title : ""
                        color: row.isSelected ? theme.accent : theme.text
                        font.pixelSize: theme.fontSizeBase
                        font.family: theme.fontFamily
                        font.weight: row.isSelected ? Font.DemiBold : Font.Normal
                        Behavior on color { ColorAnimation { duration: 80 } }
                    }

                    Text {
                        width: parent.width - widgetTab.colPad - widgetTab.colName - widgetTab.colToggle
                        height: parent.height
                        verticalAlignment: Text.AlignVCenter
                        text: row.widgetContext ? row.widgetContext.description : ""
                        color: rowHover.hovered ? "#dec184" : theme.textMuted
                        font.pixelSize: theme.fontSizeSmall
                        font.family: theme.fontFamily
                        elide: Text.ElideRight
                        Behavior on color { ColorAnimation { duration: 120 } }
                    }

                    Item {
                        width: widgetTab.colToggle
                        height: parent.height

                        ToggleSwitch {
                            anchors.centerIn: parent
                            checked: row.widgetEnabled
                            onToggled: (newValue) => { row.widgetEnabled = newValue }
                        }
                    }
                }

                MouseArea {
                    anchors.fill: parent
                    acceptedButtons: Qt.LeftButton
                    onClicked: widgetTab.selectedContext =
                        row.isSelected ? null : row.widgetContext
                }

                HoverHandler { id: rowHover }
            }
        }
    }

    // ── Divider ───────────────────────────────────────────────────────────────
    Rectangle {
        visible: widgetTab.selectedContext !== null
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        x: listPane.width
        width: 1
        color: theme.border
    }

    // ── Right: widget detail / edit panel ─────────────────────────────────────
    Item {
        id: detailPane
        visible: widgetTab.selectedContext !== null
        anchors.top: parent.top
        anchors.left: listPane.right
        anchors.leftMargin: 1
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        clip: true

        Rectangle {
            id: detailHeader
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            height: 56
            color: "transparent"

            Column {
                anchors.left: parent.left; anchors.leftMargin: 16
                anchors.verticalCenter: parent.verticalCenter
                spacing: 3

                Text {
                    text: widgetTab.selectedContext ? widgetTab.selectedContext.title : ""
                    color: theme.text
                    font.pixelSize: theme.fontSizeBase
                    font.family: theme.fontFamily
                    font.weight: Font.DemiBold
                }

                Text {
                    text: widgetTab.selectedContext ? widgetTab.selectedContext.description : ""
                    color: theme.textMuted
                    font.pixelSize: theme.fontSizeSmall
                    font.family: theme.fontFamily
                }
            }

            Rectangle {
                anchors.bottom: parent.bottom
                width: parent.width; height: 1
                color: theme.border
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
                anchors.top: parent.top
                anchors.topMargin: 8
                spacing: 0

                // ── Label ─────────────────────────────────────────────────────
                EditRow { label: "Label"
                    Rectangle {
                        width: 160; height: 28; radius: 4
                        color: theme.surfaceFloating
                        border.width: 1
                        border.color: labelInput.activeFocus ? theme.accent : theme.border
                        Behavior on border.color { ColorAnimation { duration: 80 } }

                        TextInput {
                            id: labelInput
                            anchors.fill: parent
                            anchors.leftMargin: 8; anchors.rightMargin: 8
                            verticalAlignment: TextInput.AlignVCenter
                            text: widgetTab.selectedContext ? widgetTab.selectedContext.label : ""
                            color: theme.text
                            font.pixelSize: theme.fontSizeSmall
                            font.family: theme.fontFamily
                            selectByMouse: true

                            onActiveFocusChanged: {
                                if (!activeFocus && widgetTab.selectedContext)
                                    widgetTab.selectedContext.setLabel(text)
                            }
                            Keys.onReturnPressed: {
                                if (widgetTab.selectedContext)
                                    widgetTab.selectedContext.setLabel(text)
                                focus = false
                            }
                            Keys.onEscapePressed: {
                                if (widgetTab.selectedContext)
                                    text = widgetTab.selectedContext.label
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

                // ── Position X ────────────────────────────────────────────────
                EditRow { label: "Position X"
                    NumberStepper {
                        value: widgetTab.selectedContext ? widgetTab.selectedContext.widgetX : 0
                        onCommit: (v) => {
                            if (widgetTab.selectedContext)
                                widgetTab.selectedContext.move(v, widgetTab.selectedContext.widgetY)
                        }
                        Connections {
                            target: widgetTab.selectedContext
                            function onPositionChanged() {
                                if (widgetTab.selectedContext)
                                    posXStepper.syncValue(widgetTab.selectedContext.widgetX)
                            }
                        }
                        id: posXStepper
                    }
                }

                // ── Position Y ────────────────────────────────────────────────
                EditRow { label: "Position Y"
                    NumberStepper {
                        id: posYStepper
                        value: widgetTab.selectedContext ? widgetTab.selectedContext.widgetY : 0
                        onCommit: (v) => {
                            if (widgetTab.selectedContext)
                                widgetTab.selectedContext.move(widgetTab.selectedContext.widgetX, v)
                        }
                        Connections {
                            target: widgetTab.selectedContext
                            function onPositionChanged() {
                                if (widgetTab.selectedContext)
                                    posYStepper.syncValue(widgetTab.selectedContext.widgetY)
                            }
                        }
                    }
                }

                // ── Flash below ───────────────────────────────────────────────
                EditRow {
                    label: "Flash below"
                    tooltip: "Value flashes when it drops to or below this number. Set to -1 to disable."
                    NumberStepper {
                        id: flashStepper
                        value: widgetTab.selectedContext ? widgetTab.selectedContext.flashBelow : -1
                        decimals: 1
                        onCommit: (v) => {
                            if (widgetTab.selectedContext)
                                widgetTab.selectedContext.setFlashBelow(v)
                        }
                        Connections {
                            target: widgetTab.selectedContext
                            function onConfigChanged() {
                                if (widgetTab.selectedContext)
                                    flashStepper.syncValue(widgetTab.selectedContext.flashBelow)
                            }
                        }
                    }
                }

                // ── Thresholds ────────────────────────────────────────────────
                Rectangle {
                    anchors.left: parent.left
                    anchors.right: parent.right
                    implicitHeight: thresholdCol.implicitHeight + 16
                    color: "transparent"

                    Column {
                        id: thresholdCol
                        anchors.left: parent.left; anchors.leftMargin: 16
                        anchors.right: parent.right; anchors.rightMargin: 16
                        anchors.top: parent.top; anchors.topMargin: 8
                        spacing: 6

                        Text {
                            text: "Thresholds"
                            color: theme.textSecondary
                            font.pixelSize: theme.fontSizeSmall
                            font.family: theme.fontFamily
                            font.weight: Font.Medium
                        }

                        Text {
                            anchors.left: parent.left
                            anchors.right: parent.right
                            wrapMode: Text.WordWrap
                            text: "Color changes based on the live value. Each threshold sets the color when the value is at or above that number."
                            color: theme.textMuted
                            font.pixelSize: theme.fontSizeSmall - 1
                            font.family: theme.fontFamily
                        }

                        Repeater {
                            model: widgetTab.selectedContext
                                ? widgetTab.selectedContext.thresholds : []

                            delegate: Row {
                                required property var modelData
                                required property int index
                                spacing: 8

                                Text {
                                    anchors.verticalCenter: parent.verticalCenter
                                    width: 24
                                    text: "≥"
                                    color: theme.textMuted
                                    font.pixelSize: theme.fontSizeSmall
                                    font.family: theme.fontFamily
                                    horizontalAlignment: Text.AlignRight
                                }

                                NumberStepper {
                                    value: modelData.value
                                    decimals: 1
                                    onCommit: (v) => {
                                        if (widgetTab.selectedContext)
                                            widgetTab.selectedContext.setThresholdValue(index, v)
                                    }
                                }

                                ColorPicker {
                                    anchors.verticalCenter: parent.verticalCenter
                                    value: modelData.color
                                    onColorPicked: (hex) => {
                                        if (widgetTab.selectedContext)
                                            widgetTab.selectedContext.setThresholdColor(index, hex)
                                    }
                                }
                            }
                        }
                    }

                    Rectangle {
                        anchors.bottom: parent.bottom
                        width: parent.width; height: 1
                        color: theme.border; opacity: 0.4
                    }
                }
            }
        }
    }

    // ── EditRow: label left, children right ───────────────────────────────────
    component EditRow: Rectangle {
        id: editRowRoot
        property string label: ""
        property string tooltip: ""
        default property alias rightContent: rightSlot.data

        anchors.left: parent ? parent.left : undefined
        anchors.right: parent ? parent.right : undefined
        implicitHeight: 44
        color: "transparent"

        Rectangle {
            anchors.bottom: parent.bottom
            width: parent.width; height: 1
            color: theme.border; opacity: 0.4
        }

        Text {
            anchors.left: parent.left; anchors.leftMargin: 16
            anchors.verticalCenter: parent.verticalCenter
            width: 100
            text: editRowRoot.label
            color: theme.textSecondary
            font.pixelSize: theme.fontSizeSmall
            font.family: theme.fontFamily
            font.weight: Font.Medium
        }

        Item {
            id: rightSlot
            anchors.left: parent.left; anchors.leftMargin: 116
            anchors.right: parent.right; anchors.rightMargin: 16
            anchors.verticalCenter: parent.verticalCenter
            height: 28
        }

        ToolTip.visible: tooltip !== "" && editRowHover.hovered
        ToolTip.text: tooltip
        ToolTip.delay: 600

        HoverHandler { id: editRowHover }
    }

    // ── NumberStepper: − [value] + ────────────────────────────────────────────
    component NumberStepper: Row {
        id: stepperRoot
        property real value: 0
        property int  decimals: 0
        signal commit(real v)

        function syncValue(v) { stepperField.text = _fmt(v) }
        function _fmt(v) {
            return decimals > 0 ? v.toFixed(decimals) : Math.round(v).toString()
        }
        function _step() { return decimals > 0 ? Math.pow(10, -decimals) : 1 }

        spacing: 0

        Rectangle {
            width: 24; height: 28; radius: 4
            color: minusArea.containsMouse ? theme.surfaceRaised : theme.surfaceFloating
            border.width: 1; border.color: theme.border
            Behavior on color { ColorAnimation { duration: 60 } }
            Text {
                anchors.centerIn: parent; text: "−"
                color: theme.text
                font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
            }
            MouseArea {
                id: minusArea; anchors.fill: parent; hoverEnabled: true
                onClicked: {
                    var v = parseFloat(stepperField.text) - stepperRoot._step()
                    stepperField.text = stepperRoot._fmt(v)
                    stepperRoot.commit(v)
                }
            }
        }

        Rectangle {
            width: 80; height: 28
            color: theme.surfaceFloating
            border.width: 1
            border.color: stepperField.activeFocus ? theme.accent : theme.border
            Behavior on border.color { ColorAnimation { duration: 80 } }

            TextInput {
                id: stepperField
                anchors.fill: parent; anchors.leftMargin: 6; anchors.rightMargin: 6
                verticalAlignment: TextInput.AlignVCenter
                horizontalAlignment: TextInput.AlignHCenter
                text: stepperRoot._fmt(stepperRoot.value)
                color: theme.text
                font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
                selectByMouse: true
                validator: DoubleValidator {}

                Keys.onReturnPressed: {
                    var v = parseFloat(text)
                    if (!isNaN(v)) stepperRoot.commit(v)
                    focus = false
                }
                Keys.onEscapePressed: {
                    text = stepperRoot._fmt(stepperRoot.value); focus = false
                }
                onActiveFocusChanged: {
                    if (!activeFocus) {
                        var v = parseFloat(text)
                        if (!isNaN(v)) stepperRoot.commit(v)
                        else text = stepperRoot._fmt(stepperRoot.value)
                    }
                }
            }
        }

        Rectangle {
            width: 24; height: 28; radius: 4
            color: plusArea.containsMouse ? theme.surfaceRaised : theme.surfaceFloating
            border.width: 1; border.color: theme.border
            Behavior on color { ColorAnimation { duration: 60 } }
            Text {
                anchors.centerIn: parent; text: "+"
                color: theme.text
                font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
            }
            MouseArea {
                id: plusArea; anchors.fill: parent; hoverEnabled: true
                onClicked: {
                    var v = parseFloat(stepperField.text) + stepperRoot._step()
                    stepperField.text = stepperRoot._fmt(v)
                    stepperRoot.commit(v)
                }
            }
        }
    }
}
