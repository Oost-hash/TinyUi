import QtQuick
import TinyUI 1.0

Rectangle {
    id: root

    property var widgetItems: []
    property string sectionTitle: "Widgets"
    property int selectedIndex: 0
    property var thresholdPalette: [
        "#ff5252",
        "#f4b400",
        "#34a853",
        "#42a5f5",
        "#ab47bc",
        "#ff8a65"
    ]
    property var thresholdTargets: ["value", "text", "widget"]

    function updateWidgetItem(index, patch) {
        if (!Array.isArray(widgetItems) || index < 0 || index >= widgetItems.length)
            return
        var next = widgetItems.slice(0)
        next[index] = Object.assign({}, next[index], patch || {})
        widgetItems = next
    }

    function updateThresholdItem(widgetIndex, thresholdIndex, patch) {
        if (!Array.isArray(widgetItems) || widgetIndex < 0 || widgetIndex >= widgetItems.length)
            return
        var widget = widgetItems[widgetIndex]
        if (!widget || !Array.isArray(widget.thresholds) || thresholdIndex < 0 || thresholdIndex >= widget.thresholds.length)
            return
        var nextThresholds = widget.thresholds.slice(0)
        nextThresholds[thresholdIndex] = Object.assign({}, nextThresholds[thresholdIndex], patch || {})
        updateWidgetItem(widgetIndex, { "thresholds": nextThresholds })
    }

    function cycleThresholdColor(widgetIndex, thresholdIndex) {
        if (!Array.isArray(widgetItems) || widgetIndex < 0 || widgetIndex >= widgetItems.length)
            return
        var widget = widgetItems[widgetIndex]
        if (!widget || !Array.isArray(widget.thresholds) || thresholdIndex < 0 || thresholdIndex >= widget.thresholds.length)
            return
        var current = widget.thresholds[thresholdIndex].color
        var paletteIndex = thresholdPalette.indexOf(current)
        var nextColor = thresholdPalette[(paletteIndex + 1 + thresholdPalette.length) % thresholdPalette.length]
        updateThresholdItem(widgetIndex, thresholdIndex, { "color": nextColor })
    }

    function addThreshold(widgetIndex) {
        if (!Array.isArray(widgetItems) || widgetIndex < 0 || widgetIndex >= widgetItems.length)
            return
        var widget = widgetItems[widgetIndex]
        var thresholds = Array.isArray(widget.thresholds) ? widget.thresholds.slice(0) : []
        var lastValue = thresholds.length > 0 && typeof thresholds[thresholds.length - 1].value === "number"
            ? thresholds[thresholds.length - 1].value
            : 0
        thresholds.push({
            "value": lastValue + 10,
            "color": thresholdPalette[thresholds.length % thresholdPalette.length],
            "flash": false,
            "flashTarget": "value",
            "flashSpeed": 4
        })
        updateWidgetItem(widgetIndex, { "thresholds": thresholds })
    }

    function removeThreshold(widgetIndex, thresholdIndex) {
        if (!Array.isArray(widgetItems) || widgetIndex < 0 || widgetIndex >= widgetItems.length)
            return
        var widget = widgetItems[widgetIndex]
        if (!widget || !Array.isArray(widget.thresholds) || thresholdIndex < 0 || thresholdIndex >= widget.thresholds.length)
            return
        var thresholds = widget.thresholds.slice(0)
        thresholds.splice(thresholdIndex, 1)
        updateWidgetItem(widgetIndex, { "thresholds": thresholds })
    }

    function cycleThresholdTarget(widgetIndex, thresholdIndex) {
        if (!Array.isArray(widgetItems) || widgetIndex < 0 || widgetIndex >= widgetItems.length)
            return
        var widget = widgetItems[widgetIndex]
        if (!widget || !Array.isArray(widget.thresholds) || thresholdIndex < 0 || thresholdIndex >= widget.thresholds.length)
            return
        var current = widget.thresholds[thresholdIndex].flashTarget
        var targetIndex = thresholdTargets.indexOf(current)
        var nextTarget = thresholdTargets[(targetIndex + 1 + thresholdTargets.length) % thresholdTargets.length]
        updateThresholdItem(widgetIndex, thresholdIndex, { "flashTarget": nextTarget })
    }

    readonly property var selectedWidget: {
        if (!Array.isArray(widgetItems) || widgetItems.length === 0)
            return null
        var clamped = Math.max(0, Math.min(selectedIndex, widgetItems.length - 1))
        return widgetItems[clamped]
    }

    readonly property string selectedTitle: {
        if (!selectedWidget || typeof selectedWidget.title !== "string")
            return ""
        return selectedWidget.title
    }

    readonly property string selectedDescription: {
        if (!selectedWidget || typeof selectedWidget.description !== "string")
            return ""
        return selectedWidget.description
    }

    readonly property bool selectedEnabled: {
        if (!selectedWidget || typeof selectedWidget.enabled !== "boolean")
            return false
        return selectedWidget.enabled
    }

    readonly property real selectedValue: {
        if (!selectedWidget || typeof selectedWidget.value !== "number")
            return 0
        return selectedWidget.value
    }

    readonly property string selectedLabel: {
        if (!selectedWidget || typeof selectedWidget.label !== "string")
            return ""
        return selectedWidget.label
    }

    readonly property int selectedPositionX: {
        if (!selectedWidget || typeof selectedWidget.positionX !== "number")
            return 0
        return selectedWidget.positionX
    }

    readonly property int selectedPositionY: {
        if (!selectedWidget || typeof selectedWidget.positionY !== "number")
            return 0
        return selectedWidget.positionY
    }

    readonly property real selectedFlashBelow: {
        if (!selectedWidget || typeof selectedWidget.flashBelow !== "number")
            return -1
        return selectedWidget.flashBelow
    }

    readonly property var selectedThresholds: {
        if (!selectedWidget || !Array.isArray(selectedWidget.thresholds))
            return []
        return selectedWidget.thresholds
    }

    radius: 18
    color: "#111418"
    border.width: 1
    border.color: "#252b34"

    Row {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 18

        Rectangle {
            width: Math.max(280, parent.width * 0.42)
            height: parent.height
            radius: 16
            color: "#15191e"
            border.width: 1
            border.color: "#252b34"

            Text {
                id: sectionTitleText
                x: 18
                y: 16
                text: root.sectionTitle
                color: "#f4f7fb"
                font.pixelSize: 18
                font.weight: Font.DemiBold
            }

            Text {
                x: 18
                y: sectionTitleText.y + sectionTitleText.height + 4
                width: parent.width - 36
                text: "Widget overzicht."
                wrapMode: Text.WordWrap
                color: "#8e97a5"
                font.pixelSize: 13
            }

            Column {
                x: 12
                y: 92
                width: parent.width - 24
                spacing: 10

                Repeater {
                    model: root.widgetItems

                    delegate: Rectangle {
                        required property var modelData
                        required property int index

                        width: parent ? parent.width : 240
                        height: 48
                        radius: 12
                        color: root.selectedIndex === index ? "#e8edf5" : "#1b1f25"
                        border.width: root.selectedIndex === index ? 0 : 1
                        border.color: "#2b313a"

                        Text {
                            anchors.left: parent.left
                            anchors.leftMargin: 14
                            anchors.verticalCenter: parent.verticalCenter
                            text: modelData && typeof modelData.title === "string" ? modelData.title : ""
                            color: root.selectedIndex === index ? "#14171b" : "#c5ccd8"
                            font.pixelSize: 14
                        }

                        Rectangle {
                            anchors.right: parent.right
                            anchors.rightMargin: 12
                            anchors.verticalCenter: parent.verticalCenter
                            width: 48
                            height: 22
                            radius: 7
                            color: root.selectedIndex === index ? "#d7dee8" : "#252b34"

                            Text {
                                anchors.centerIn: parent
                                text: modelData && typeof modelData.enabled === "boolean" && modelData.enabled ? "on" : "off"
                                color: root.selectedIndex === index ? "#14171b" : "#9aa1ad"
                                font.pixelSize: 11
                            }
                        }

                        ToggleSwitch {
                            anchors.right: parent.right
                            anchors.rightMargin: 82
                            anchors.verticalCenter: parent.verticalCenter
                            checked: modelData && typeof modelData.enabled === "boolean" ? modelData.enabled : false
                            onToggled: (value) => root.updateWidgetItem(index, { "enabled": value })
                        }

                        MouseArea {
                            anchors.fill: parent
                            anchors.rightMargin: 152
                            onClicked: root.selectedIndex = index
                        }
                    }
                }
            }
        }

        Rectangle {
            width: parent.width - 18 - Math.max(280, parent.width * 0.42)
            height: parent.height
            radius: 16
            color: "#15191e"
            border.width: 1
            border.color: "#252b34"

            Column {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 14

                Text {
                    text: root.selectedTitle !== "" ? root.selectedTitle : "No widget selected"
                    color: "#f4f7fb"
                    font.pixelSize: 18
                    font.weight: Font.DemiBold
                }

                Text {
                    width: parent.width
                    wrapMode: Text.WordWrap
                    text: root.selectedTitle !== ""
                        ? root.selectedDescription
                        : ""
                    color: "#8e97a5"
                    font.pixelSize: 13
                }

                Rectangle {
                    width: parent.width
                    height: 1
                    color: "#252b34"
                }

                Rectangle {
                    width: parent.width
                    height: 44
                    radius: 12
                    color: "#1b1f25"

                    Text {
                        anchors.left: parent.left
                        anchors.leftMargin: 14
                        anchors.verticalCenter: parent.verticalCenter
                        text: "Selected widget"
                        color: "#9aa1ad"
                        font.pixelSize: 12
                    }

                    Text {
                        anchors.right: parent.right
                        anchors.rightMargin: 14
                        anchors.verticalCenter: parent.verticalCenter
                        text: root.selectedTitle
                        color: "#f4f7fb"
                        font.pixelSize: 13
                    }
                }

                Rectangle {
                    width: parent.width
                    height: 56
                    radius: 12
                    color: "#1b1f25"

                    Text {
                        anchors.left: parent.left
                        anchors.leftMargin: 14
                        anchors.verticalCenter: parent.verticalCenter
                        text: "Label"
                        color: "#9aa1ad"
                        font.pixelSize: 12
                    }

                    Rectangle {
                        anchors.right: parent.right
                        anchors.rightMargin: 14
                        anchors.verticalCenter: parent.verticalCenter
                        width: 220
                        height: 30
                        radius: 8
                        color: "#15191e"
                        border.width: 1
                        border.color: labelInput.activeFocus ? "#d7dee8" : "#2b313a"

                        TextInput {
                            id: labelInput
                            anchors.fill: parent
                            anchors.leftMargin: 10
                            anchors.rightMargin: 10
                            verticalAlignment: TextInput.AlignVCenter
                            color: "#f4f7fb"
                            font.pixelSize: 12
                            selectByMouse: true
                            text: root.selectedLabel

                            onEditingFinished: root.updateWidgetItem(root.selectedIndex, { "label": text })
                            onActiveFocusChanged: {
                                if (!activeFocus)
                                    text = root.selectedLabel
                            }
                        }
                    }
                }

                Rectangle {
                    width: parent.width
                    height: 56
                    radius: 12
                    color: "#1b1f25"

                    Text {
                        anchors.left: parent.left
                        anchors.leftMargin: 14
                        anchors.verticalCenter: parent.verticalCenter
                        text: "Enabled"
                        color: "#9aa1ad"
                        font.pixelSize: 12
                    }

                    ToggleSwitch {
                        anchors.right: parent.right
                        anchors.rightMargin: 14
                        anchors.verticalCenter: parent.verticalCenter
                        checked: root.selectedEnabled
                        onToggled: (value) => root.updateWidgetItem(root.selectedIndex, { "enabled": value })
                    }
                }

                Rectangle {
                    width: parent.width
                    height: 56
                    radius: 12
                    color: "#1b1f25"

                    Text {
                        anchors.left: parent.left
                        anchors.leftMargin: 14
                        anchors.verticalCenter: parent.verticalCenter
                        text: "Position X"
                        color: "#9aa1ad"
                        font.pixelSize: 12
                    }

                    NumberStepper {
                        anchors.right: parent.right
                        anchors.rightMargin: 14
                        anchors.verticalCenter: parent.verticalCenter
                        value: root.selectedPositionX
                        step: 1
                        min: 0
                        max: 9999
                        onCommit: (value) => root.updateWidgetItem(root.selectedIndex, { "positionX": value })
                    }
                }

                Rectangle {
                    width: parent.width
                    height: 56
                    radius: 12
                    color: "#1b1f25"

                    Text {
                        anchors.left: parent.left
                        anchors.leftMargin: 14
                        anchors.verticalCenter: parent.verticalCenter
                        text: "Position Y"
                        color: "#9aa1ad"
                        font.pixelSize: 12
                    }

                    NumberStepper {
                        anchors.right: parent.right
                        anchors.rightMargin: 14
                        anchors.verticalCenter: parent.verticalCenter
                        value: root.selectedPositionY
                        step: 1
                        min: 0
                        max: 9999
                        onCommit: (value) => root.updateWidgetItem(root.selectedIndex, { "positionY": value })
                    }
                }

                Rectangle {
                    width: parent.width
                    height: 56
                    radius: 12
                    color: "#1b1f25"

                    Text {
                        anchors.left: parent.left
                        anchors.leftMargin: 14
                        anchors.verticalCenter: parent.verticalCenter
                        text: "Flash below"
                        color: "#9aa1ad"
                        font.pixelSize: 12
                    }

                    NumberStepper {
                        anchors.right: parent.right
                        anchors.rightMargin: 14
                        anchors.verticalCenter: parent.verticalCenter
                        value: root.selectedFlashBelow
                        step: 1
                        min: -1
                        max: 9999
                        onCommit: (value) => root.updateWidgetItem(root.selectedIndex, { "flashBelow": value })
                    }
                }

                Rectangle {
                    width: parent.width
                    height: thresholdColumn.implicitHeight + 20
                    radius: 12
                    color: "#1b1f25"

                    Column {
                        id: thresholdColumn
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.margins: 14
                        spacing: 10

                        Text {
                            text: "Thresholds"
                            color: "#9aa1ad"
                            font.pixelSize: 12
                        }

                        Text {
                            width: parent.width
                            wrapMode: Text.WordWrap
                            text: "Each threshold is an upper bound. The widget uses the threshold color while the value is at or below that number."
                            color: "#8e97a5"
                            font.pixelSize: 12
                            visible: root.selectedThresholds.length > 0
                        }

                        Text {
                            text: "No thresholds configured."
                            color: "#8e97a5"
                            font.pixelSize: 12
                            visible: root.selectedThresholds.length === 0
                        }

                        Repeater {
                            model: root.selectedThresholds

                            delegate: Column {
                                required property var modelData
                                required property int index

                                width: thresholdColumn.width
                                spacing: 6

                                Rectangle {
                                    width: parent.width
                                    height: 42
                                    radius: 10
                                    color: "#15191e"
                                    border.width: 1
                                    border.color: "#2b313a"

                                    Rectangle {
                                        anchors.left: parent.left
                                        anchors.leftMargin: 10
                                        anchors.verticalCenter: parent.verticalCenter
                                        width: 14
                                        height: 14
                                        radius: 7
                                        color: modelData && typeof modelData.color === "string" ? modelData.color : "#c5ccd8"
                                        border.width: 1
                                        border.color: "#39414d"

                                        MouseArea {
                                            anchors.fill: parent
                                            onClicked: root.cycleThresholdColor(root.selectedIndex, index)
                                        }
                                    }

                                    Text {
                                        anchors.left: parent.left
                                        anchors.leftMargin: 34
                                        anchors.verticalCenter: parent.verticalCenter
                                        text: "≤"
                                        color: "#f4f7fb"
                                        font.pixelSize: 12
                                    }

                                    NumberStepper {
                                        anchors.left: parent.left
                                        anchors.leftMargin: 56
                                        anchors.verticalCenter: parent.verticalCenter
                                        value: modelData && typeof modelData.value === "number" ? modelData.value : 0
                                        step: 1
                                        min: -9999
                                        max: 9999
                                        onCommit: (value) => root.updateThresholdItem(root.selectedIndex, index, { "value": value })
                                    }

                                    ToggleSwitch {
                                        anchors.right: parent.right
                                        anchors.rightMargin: 46
                                        anchors.verticalCenter: parent.verticalCenter
                                        checked: modelData && typeof modelData.flash === "boolean" ? modelData.flash : false
                                        onToggled: (value) => root.updateThresholdItem(root.selectedIndex, index, { "flash": value })
                                    }

                                    Rectangle {
                                        anchors.right: parent.right
                                        anchors.rightMargin: 10
                                        anchors.verticalCenter: parent.verticalCenter
                                        width: 22
                                        height: 22
                                        radius: 11
                                        color: "#1b1f25"
                                        border.width: 1
                                        border.color: "#39414d"

                                        Text {
                                            anchors.centerIn: parent
                                            text: "x"
                                            color: "#c5ccd8"
                                            font.pixelSize: 11
                                        }

                                        MouseArea {
                                            anchors.fill: parent
                                            onClicked: root.removeThreshold(root.selectedIndex, index)
                                        }
                                    }
                                }

                                Rectangle {
                                    width: parent.width
                                    height: modelData && typeof modelData.flash === "boolean" && modelData.flash ? 42 : 0
                                    radius: 10
                                    color: "#111418"
                                    border.width: height > 0 ? 1 : 0
                                    border.color: "#2b313a"
                                    visible: height > 0
                                    clip: true

                                    Text {
                                        anchors.left: parent.left
                                        anchors.leftMargin: 12
                                        anchors.verticalCenter: parent.verticalCenter
                                        text: "Target"
                                        color: "#9aa1ad"
                                        font.pixelSize: 12
                                    }

                                    Rectangle {
                                        anchors.left: parent.left
                                        anchors.leftMargin: 56
                                        anchors.verticalCenter: parent.verticalCenter
                                        width: 92
                                        height: 26
                                        radius: 8
                                        color: "#15191e"
                                        border.width: 1
                                        border.color: "#39414d"

                                        Text {
                                            anchors.centerIn: parent
                                            text: modelData && typeof modelData.flashTarget === "string" ? modelData.flashTarget : "value"
                                            color: "#f4f7fb"
                                            font.pixelSize: 12
                                        }

                                        MouseArea {
                                            anchors.fill: parent
                                            onClicked: root.cycleThresholdTarget(root.selectedIndex, index)
                                        }
                                    }

                                    Text {
                                        anchors.left: parent.left
                                        anchors.leftMargin: 164
                                        anchors.verticalCenter: parent.verticalCenter
                                        text: "Speed"
                                        color: "#9aa1ad"
                                        font.pixelSize: 12
                                    }

                                    NumberStepper {
                                        anchors.right: parent.right
                                        anchors.rightMargin: 12
                                        anchors.verticalCenter: parent.verticalCenter
                                        value: modelData && typeof modelData.flashSpeed === "number" ? modelData.flashSpeed : 4
                                        step: 1
                                        min: 1
                                        max: 20
                                        onCommit: (value) => root.updateThresholdItem(root.selectedIndex, index, { "flashSpeed": value })
                                    }
                                }
                            }
                        }

                        Rectangle {
                            width: 132
                            height: 30
                            radius: 8
                            color: "#15191e"
                            border.width: 1
                            border.color: "#2b313a"

                            Text {
                                anchors.centerIn: parent
                                text: "Add threshold"
                                color: "#f4f7fb"
                                font.pixelSize: 12
                            }

                            MouseArea {
                                anchors.fill: parent
                                onClicked: root.addThreshold(root.selectedIndex)
                            }
                        }
                    }
                }

                Rectangle {
                    width: parent.width
                    height: 56
                    radius: 12
                    color: "#1b1f25"

                    Text {
                        anchors.left: parent.left
                        anchors.leftMargin: 14
                        anchors.verticalCenter: parent.verticalCenter
                        text: "Value"
                        color: "#9aa1ad"
                        font.pixelSize: 12
                    }

                    NumberStepper {
                        anchors.right: parent.right
                        anchors.rightMargin: 14
                        anchors.verticalCenter: parent.verticalCenter
                        value: root.selectedValue
                        step: 1
                        min: 0
                        max: 999
                        onCommit: (value) => root.updateWidgetItem(root.selectedIndex, { "value": value })
                    }
                }
            }
        }
    }
}
