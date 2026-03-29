
import QtQuick
import QtQuick.Window
import TinyUI 1.0

Rectangle {
    id: root

    readonly property var hostWindow: Window.window
    readonly property var hostTheme: hostWindow && hostWindow.theme ? hostWindow.theme : null

    property var widgetItems: []
    property string sectionTitle: "Widgets"
    property int selectedIndex: -1
    property var demoLeaseWidget: null
    property var thresholdPalette: [
        "#ff5252",
        "#f4b400",
        "#34a853",
        "#42a5f5",
        "#ab47bc",
        "#ff8a65"
    ]
    property var thresholdTargets: ["value", "text", "widget"]

    readonly property color surface: hostTheme ? hostTheme.surface : "#282C33"
    readonly property color surfaceAlt: hostTheme ? hostTheme.surfaceAlt : "#2F343E"
    readonly property color surfaceRaised: hostTheme ? hostTheme.surfaceRaised : "#3B414D"
    readonly property color surfaceFloating: hostTheme ? hostTheme.surfaceFloating : "#20242b"
    readonly property color borderColor: hostTheme ? hostTheme.border : "#464B57"
    readonly property color textColor: hostTheme ? hostTheme.text : "#DCE0E5"
    readonly property color textSecondary: hostTheme ? hostTheme.textSecondary : "#A9AFBC"
    readonly property color textMuted: hostTheme ? hostTheme.textMuted : "#878A98"
    readonly property color accentColor: hostTheme ? hostTheme.accent : "#74ADE8"
    readonly property color warningColor: hostTheme ? hostTheme.warning : "#dec184"
    readonly property int fontBase: hostTheme ? hostTheme.fontSizeBase : 13
    readonly property int fontSmall: hostTheme ? hostTheme.fontSizeSmall : 11
    readonly property string fontFamily: hostTheme ? hostTheme.fontFamily : "Segoe UI"

    onSelectedWidgetChanged: {
        if (demoLeaseWidget
                && demoLeaseWidget !== selectedWidget
                && typeof demoLeaseWidget.releaseDemo === "function"
                && root.itemValue(demoLeaseWidget, "demoRequested", false)) {
            demoLeaseWidget.releaseDemo()
        }
        if (selectedWidget
                && root.itemValue(selectedWidget, "supportsDemoMode", false)
                && typeof selectedWidget.requestDemo === "function") {
            if (!root.itemValue(selectedWidget, "demoRequested", false))
                selectedWidget.requestDemo()
            demoLeaseWidget = selectedWidget
            return
        }
        demoLeaseWidget = null
    }

    function itemCount(items) {
        if (!items || items.length === undefined || items.length === null)
            return 0
        return Number(items.length)
    }

    function widgetAt(index) {
        if (index < 0 || index >= itemCount(widgetItems))
            return null
        return widgetItems[index]
    }

    function itemValue(item, fieldName, fallback) {
        if (!item || typeof item !== "object")
            return fallback
        if (item[fieldName] === undefined || item[fieldName] === null)
            return fallback
        return item[fieldName]
    }

    function updateWidgetItem(index, patch) {
        var current = widgetAt(index)
        if (!current)
            return
        if (typeof current.setLabel === "function" && patch && patch.label !== undefined)
            current.setLabel(patch.label)
        if (typeof current.setEnabled === "function" && patch && patch.enabled !== undefined)
            current.setEnabled(patch.enabled)
        if (typeof current.move === "function" && patch && (patch.positionX !== undefined || patch.positionY !== undefined)) {
            var nextX = patch.positionX !== undefined ? patch.positionX : itemValue(current, "widgetX", itemValue(current, "positionX", 0))
            var nextY = patch.positionY !== undefined ? patch.positionY : itemValue(current, "widgetY", itemValue(current, "positionY", 0))
            current.move(nextX, nextY)
        }
        if (typeof current.setValue === "function" && patch && patch.value !== undefined)
            current.setValue(patch.value)
        if (typeof current.setThresholds === "function" && patch && patch.thresholds !== undefined)
            current.setThresholds(patch.thresholds)
        if (typeof current.setLabel === "function" || typeof current.setEnabled === "function" || typeof current.move === "function")
            return
        var next = Array.prototype.slice.call(widgetItems, 0)
        next[index] = Object.assign({}, next[index], patch || {})
        widgetItems = next
    }

    function updateThresholdItem(widgetIndex, thresholdIndex, patch) {
        if (widgetIndex < 0 || widgetIndex >= itemCount(widgetItems))
            return
        var widget = widgetAt(widgetIndex)
        if (!widget || !widget.thresholds || thresholdIndex < 0 || thresholdIndex >= itemCount(widget.thresholds))
            return
        if (patch && patch.color !== undefined && typeof widget.setThresholdColor === "function")
            widget.setThresholdColor(thresholdIndex, patch.color)
        if (patch && patch.value !== undefined && typeof widget.setThresholdValue === "function")
            widget.setThresholdValue(thresholdIndex, patch.value)
        if (patch && patch.flash !== undefined && typeof widget.setThresholdFlash === "function")
            widget.setThresholdFlash(thresholdIndex, patch.flash)
        if (patch && patch.flashSpeed !== undefined && typeof widget.setThresholdFlashSpeed === "function")
            widget.setThresholdFlashSpeed(thresholdIndex, patch.flashSpeed)
        if (patch && patch.flashTarget !== undefined && typeof widget.setThresholdFlashTarget === "function")
            widget.setThresholdFlashTarget(thresholdIndex, patch.flashTarget)
        if (typeof widget.setThresholdColor === "function"
                || typeof widget.setThresholdValue === "function"
                || typeof widget.setThresholdFlash === "function"
                || typeof widget.setThresholdFlashSpeed === "function"
                || typeof widget.setThresholdFlashTarget === "function")
            return
        var nextThresholds = widget.thresholds.slice(0)
        nextThresholds[thresholdIndex] = Object.assign({}, nextThresholds[thresholdIndex], patch || {})
        updateWidgetItem(widgetIndex, { "thresholds": nextThresholds })
    }

    function cycleThresholdColor(widgetIndex, thresholdIndex) {
        if (widgetIndex < 0 || widgetIndex >= itemCount(widgetItems))
            return
        var widget = widgetItems[widgetIndex]
        if (!widget || !widget.thresholds || thresholdIndex < 0 || thresholdIndex >= itemCount(widget.thresholds))
            return
        var current = widget.thresholds[thresholdIndex].color
        var paletteIndex = thresholdPalette.indexOf(current)
        var nextColor = thresholdPalette[(paletteIndex + 1 + thresholdPalette.length) % thresholdPalette.length]
        updateThresholdItem(widgetIndex, thresholdIndex, { "color": nextColor })
    }

    function addThreshold(widgetIndex) {
        var widget = widgetAt(widgetIndex)
        if (!widget)
            return
        var thresholds = widget.thresholds ? Array.prototype.slice.call(widget.thresholds, 0) : []
        var lastValue = thresholds.length > 0 && typeof thresholds[thresholds.length - 1].value === "number"
            ? thresholds[thresholds.length - 1].value
            : 0
        if (typeof widget.addDefaultThreshold === "function") {
            widget.addDefaultThreshold()
            return
        }
        if (typeof widget.addThreshold === "function") {
            widget.addThreshold(lastValue + 10, thresholdPalette[thresholds.length % thresholdPalette.length])
            return
        }
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
        if (widgetIndex < 0 || widgetIndex >= itemCount(widgetItems))
            return
        var widget = widgetAt(widgetIndex)
        if (!widget || !widget.thresholds || thresholdIndex < 0 || thresholdIndex >= itemCount(widget.thresholds))
            return
        if (typeof widget.removeThreshold === "function") {
            widget.removeThreshold(thresholdIndex)
            return
        }
        var thresholds = widget.thresholds.slice(0)
        thresholds.splice(thresholdIndex, 1)
        updateWidgetItem(widgetIndex, { "thresholds": thresholds })
    }

    function cycleThresholdTarget(widgetIndex, thresholdIndex) {
        if (widgetIndex < 0 || widgetIndex >= itemCount(widgetItems))
            return
        var widget = widgetItems[widgetIndex]
        if (!widget || !widget.thresholds || thresholdIndex < 0 || thresholdIndex >= itemCount(widget.thresholds))
            return
        var current = widget.thresholds[thresholdIndex].flashTarget
        var targetIndex = thresholdTargets.indexOf(current)
        var nextTarget = thresholdTargets[(targetIndex + 1 + thresholdTargets.length) % thresholdTargets.length]
        updateThresholdItem(widgetIndex, thresholdIndex, { "flashTarget": nextTarget })
    }
    readonly property var selectedWidget: {
        var count = itemCount(widgetItems)
        if (count === 0)
            return null
        if (selectedIndex < 0 || selectedIndex >= count)
            return null
        return widgetItems[selectedIndex]
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
    readonly property bool selectedSupportsDemoMode: {
        return !!(selectedWidget && root.itemValue(selectedWidget, "supportsDemoMode", false))
    }
    readonly property bool selectedDemoRequested: {
        return !!(selectedWidget && root.itemValue(selectedWidget, "demoRequested", false))
    }
    readonly property real selectedDemoMin: {
        return selectedWidget ? root.itemValue(selectedWidget, "demoMin", 0) : 0
    }
    readonly property real selectedDemoMax: {
        return selectedWidget ? root.itemValue(selectedWidget, "demoMax", 100) : 100
    }
    readonly property real selectedDemoSpeed: {
        return selectedWidget ? root.itemValue(selectedWidget, "demoSpeed", 0.5) : 0.5
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

    readonly property bool selectedHasEditableValue: {
        if (!selectedWidget)
            return false
        return typeof selectedWidget.value === "number" || typeof selectedWidget.setValue === "function"
    }

    readonly property string selectedLabel: {
        if (!selectedWidget || typeof selectedWidget.label !== "string")
            return ""
        return selectedWidget.label
    }

    readonly property int selectedPositionX: {
        if (!selectedWidget || typeof itemValue(selectedWidget, "widgetX", itemValue(selectedWidget, "positionX", null)) !== "number")
            return 0
        return itemValue(selectedWidget, "widgetX", itemValue(selectedWidget, "positionX", 0))
    }

    readonly property int selectedPositionY: {
        if (!selectedWidget || typeof itemValue(selectedWidget, "widgetY", itemValue(selectedWidget, "positionY", null)) !== "number")
            return 0
        return itemValue(selectedWidget, "widgetY", itemValue(selectedWidget, "positionY", 0))
    }

    readonly property var selectedThresholds: {
        if (!selectedWidget || !selectedWidget.thresholds)
            return []
        return selectedWidget.thresholds
    }

    color: surface

    Row {
        anchors.fill: parent
        spacing: 0

        Item {
            id: listPane
            width: selectedWidget ? Math.round(parent.width * 0.39) : parent.width
            height: parent.height
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
                    anchors.leftMargin: 16

                    Text {
                        width: 200
                        height: parent.height
                        verticalAlignment: Text.AlignVCenter
                        text: "Widget"
                        color: textColor
                        font.pixelSize: fontSmall
                        font.family: fontFamily
                    }

                    Text {
                        width: parent.width - 16 - 200 - 56
                        height: parent.height
                        verticalAlignment: Text.AlignVCenter
                        text: "Description"
                        color: textColor
                        font.pixelSize: fontSmall
                        font.family: fontFamily
                    }
                }

                Rectangle {
                    anchors.bottom: parent.bottom
                    width: parent.width
                    height: 1
                    color: borderColor
                }
            }

            ListView {
                id: widgetList
                anchors.top: tableHeader.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                clip: true
                model: root.widgetItems
                spacing: 0

                delegate: Rectangle {
                    id: row
                    required property var modelData
                    required property int index

                    readonly property bool isSelected: root.selectedIndex === index

                    width: ListView.view.width
                    height: 40
                    color: isSelected ? surfaceRaised : (index % 2 === 0 ? surfaceAlt : "transparent")
                    Behavior on color { ColorAnimation { duration: 80 } }

                    Rectangle {
                        width: 2
                        height: parent.height
                        color: accentColor
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
                        color: borderColor
                        opacity: 0.4
                    }
                    Row {
                        anchors.fill: parent
                        anchors.leftMargin: 16 + (row.isSelected ? 8 : 0)
                        spacing: 0

                        Text {
                            width: 200
                            height: parent.height
                            verticalAlignment: Text.AlignVCenter
                            text: modelData && typeof modelData.title === "string" ? modelData.title : ""
                            color: row.isSelected ? accentColor : textColor
                            font.pixelSize: fontBase
                            font.family: fontFamily
                            font.weight: row.isSelected ? Font.DemiBold : Font.Normal
                            Behavior on color { ColorAnimation { duration: 80 } }
                        }

                        Text {
                            width: parent.width - 16 - 200 - 56
                            height: parent.height
                            verticalAlignment: Text.AlignVCenter
                            text: modelData && typeof modelData.description === "string" ? modelData.description : ""
                            color: rowHover.hovered ? warningColor : textMuted
                            font.pixelSize: fontSmall
                            font.family: fontFamily
                            elide: Text.ElideRight
                            Behavior on color { ColorAnimation { duration: 120 } }
                        }

                        Item {
                            width: 56
                            height: parent.height

                            ToggleSwitch {
                                anchors.centerIn: parent
                                checked: modelData && typeof modelData.enabled === "boolean" ? modelData.enabled : false
                                onToggled: (value) => root.updateWidgetItem(index, { "enabled": value })
                            }
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        anchors.rightMargin: 56
                        onClicked: root.selectedIndex = root.selectedIndex === index ? -1 : index
                    }

                    HoverHandler { id: rowHover }
                }
            }
        }

        Rectangle {
            visible: selectedWidget !== null
            width: 1
            height: parent.height
            color: borderColor
        }

        Item {
            id: detailPane
            visible: root.selectedWidget !== null
            width: parent.width - listPane.width - 1
            height: parent.height
            clip: true

            Rectangle {
                id: detailHeader
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: parent.right
                height: 48
                color: "transparent"

                Column {
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.leftMargin: 16
                    anchors.rightMargin: 12
                    spacing: 2

                    Text {
                        text: root.selectedTitle
                        color: textColor
                        font.pixelSize: fontBase - 1
                        font.family: fontFamily
                        font.weight: Font.DemiBold
                    }

                    Text {
                        text: root.selectedDescription
                        color: textMuted
                        font.pixelSize: fontSmall
                        font.family: fontFamily
                        elide: Text.ElideRight
                    }
                }

                Rectangle {
                    anchors.bottom: parent.bottom
                    width: parent.width
                    height: 1
                    color: borderColor
                }
            }

            Rectangle {
                id: demoSection
                readonly property bool active: root.selectedSupportsDemoMode && root.selectedDemoRequested
                anchors.top: detailHeader.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                height: active ? demoSectionInner.implicitHeight : 0
                Behavior on height { NumberAnimation { duration: 160; easing.type: Easing.OutCubic } }
                clip: true
                color: surfaceAlt
                visible: height > 0

                Rectangle {
                    anchors.bottom: parent.bottom
                    width: parent.width
                    height: 1
                    color: borderColor
                }

                Column {
                    id: demoSectionInner
                    anchors.left: parent.left
                    anchors.right: parent.right
                    spacing: 0

                    EditRow {
                        label: "Min"
                        description: "Lowest value in the mock sweep"
                        NumberStepper {
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            value: root.selectedDemoMin
                            step: 1
                            onCommit: (value) => {
                                if (root.selectedWidget && typeof root.selectedWidget.setDemoMin === "function")
                                    root.selectedWidget.setDemoMin(value)
                            }
                        }
                    }

                    EditRow {
                        label: "Max"
                        description: "Highest value before the sweep resets"
                        NumberStepper {
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            value: root.selectedDemoMax
                            step: 1
                            onCommit: (value) => {
                                if (root.selectedWidget && typeof root.selectedWidget.setDemoMax === "function")
                                    root.selectedWidget.setDemoMax(value)
                            }
                        }
                    }

                    EditRow {
                        label: "Speed"
                        description: "Sweep speed per update cycle"
                        NumberStepper {
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            value: root.selectedDemoSpeed
                            step: 0.1
                            min: 0.1
                            onCommit: (value) => {
                                if (root.selectedWidget && typeof root.selectedWidget.setDemoSpeed === "function")
                                    root.selectedWidget.setDemoSpeed(value)
                            }
                        }
                    }
                }
            }

            Flickable {
                anchors.top: demoSection.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                clip: true
                contentHeight: editColumn.implicitHeight

                Column {
                    id: editColumn
                    width: detailPane.width
                    spacing: 0

                    SectionHeader { text: "Identity" }

                    EditRow {
                        label: "Label"
                        description: "Short text shown on the widget"

                        Rectangle {
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            width: 124
                            height: 26
                            radius: 4
                            color: surfaceFloating
                            border.width: 1
                            border.color: labelInput.activeFocus ? accentColor : borderColor

                            TextInput {
                                id: labelInput
                                anchors.fill: parent
                                anchors.leftMargin: 8
                                anchors.rightMargin: 8
                                verticalAlignment: TextInput.AlignVCenter
                                text: root.selectedLabel
                                color: textColor
                                font.pixelSize: fontSmall
                                font.family: fontFamily
                                selectByMouse: true
                                onActiveFocusChanged: {
                                    if (!activeFocus)
                                        root.updateWidgetItem(root.selectedIndex, { "label": text })
                                }
                                Keys.onReturnPressed: {
                                    root.updateWidgetItem(root.selectedIndex, { "label": text })
                                    focus = false
                                }
                                Keys.onEscapePressed: {
                                    text = root.selectedLabel
                                    focus = false
                                }
                            }
                        }
                    }

                    EditRow {
                        label: "Position X"

                        NumberStepper {
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            value: root.selectedPositionX
                            step: 1
                            min: 0
                            max: 9999
                            onCommit: (value) => root.updateWidgetItem(root.selectedIndex, { "positionX": value })
                        }
                    }

                    EditRow {
                        label: "Position Y"

                        NumberStepper {
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            value: root.selectedPositionY
                            step: 1
                            min: 0
                            max: 9999
                            onCommit: (value) => root.updateWidgetItem(root.selectedIndex, { "positionY": value })
                        }
                    }

                    SectionHeader { text: "Provider" }

                    EditRow {
                        label: "Binding"
                        description: root.selectedWidget
                            ? (
                                root.itemValue(root.selectedWidget, "activeGame", "none") !== "none"
                                ? root.itemValue(root.selectedWidget, "providerName", "") + " / " + root.itemValue(root.selectedWidget, "activeGame", "")
                                : root.itemValue(root.selectedWidget, "providerName", "")
                              )
                            : ""
                    }

                    EditRow {
                        label: "Mode"
                        description: root.selectedWidget ? root.itemValue(root.selectedWidget, "providerMode", "") : ""
                    }

                    EditRow {
                        visible: root.selectedHasEditableValue
                        label: "Value"

                        NumberStepper {
                            anchors.right: parent.right
                            anchors.rightMargin: 0
                            anchors.verticalCenter: parent.verticalCenter
                            value: root.selectedValue
                            step: 1
                            min: 0
                            max: 999
                            onCommit: (value) => root.updateWidgetItem(root.selectedIndex, { "value": value })
                        }
                    }

                    SectionHeader { text: "Thresholds" }

                    ThresholdEditor {
                        width: parent.width
                        context: root.selectedWidget
                        bridge: root
                        widgetIndex: root.selectedIndex
                        thresholdPalette: root.thresholdPalette
                        thresholdTargets: root.thresholdTargets
                    }
                }
            }
        }
    }

}
