import QtQuick
import QtQuick.Window
import TinyUI 1.0

Column {
    id: root

    readonly property var hostWindow: Window.window
    readonly property var hostTheme: hostWindow && hostWindow.theme ? hostWindow.theme : null

    property var context: null
    property var bridge: null
    property int widgetIndex: -1
    property var thresholdPalette: []
    property var thresholdTargets: ["value", "text", "widget"]

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
    readonly property var thresholds: context && context.thresholds ? context.thresholds : []

    width: parent ? parent.width : 0
    spacing: 0

    function _thresholdAt(index) {
        return index >= 0 && index < thresholds.length ? thresholds[index] : null
    }

    function _update(index, patch) {
        if (!context)
            return
        var threshold = _thresholdAt(index)
        if (!threshold)
            return
        if (patch && patch.color !== undefined && typeof context.setThresholdColor === "function") {
            context.setThresholdColor(index, patch.color)
            return
        }
        if (patch && patch.value !== undefined && typeof context.setThresholdValue === "function") {
            context.setThresholdValue(index, patch.value)
            return
        }
        if (patch && patch.flash !== undefined && typeof context.setThresholdFlash === "function") {
            context.setThresholdFlash(index, patch.flash)
            return
        }
        if (patch && patch.flashSpeed !== undefined && typeof context.setThresholdFlashSpeed === "function") {
            context.setThresholdFlashSpeed(index, patch.flashSpeed)
            return
        }
        if (patch && patch.flashTarget !== undefined && typeof context.setThresholdFlashTarget === "function") {
            context.setThresholdFlashTarget(index, patch.flashTarget)
            return
        }
        if (bridge && typeof bridge.updateThresholdItem === "function" && widgetIndex >= 0)
            bridge.updateThresholdItem(widgetIndex, index, patch)
    }

    function _remove(index) {
        if (context && typeof context.removeThreshold === "function") {
            context.removeThreshold(index)
            return
        }
        if (bridge && typeof bridge.removeThreshold === "function" && widgetIndex >= 0)
            bridge.removeThreshold(widgetIndex, index)
    }

    function _add() {
        if (context && typeof context.addDefaultThreshold === "function") {
            context.addDefaultThreshold()
            return
        }
        if (bridge && typeof bridge.addThreshold === "function" && widgetIndex >= 0)
            bridge.addThreshold(widgetIndex)
    }

    function _cycleColor(index) {
        var threshold = _thresholdAt(index)
        if (!threshold)
            return
        if (bridge && typeof bridge.cycleThresholdColor === "function" && widgetIndex >= 0) {
            bridge.cycleThresholdColor(widgetIndex, index)
            return
        }
        if (!Array.isArray(thresholdPalette) || thresholdPalette.length === 0)
            return
        var paletteIndex = thresholdPalette.indexOf(threshold.color)
        var nextColor = thresholdPalette[(paletteIndex + 1 + thresholdPalette.length) % thresholdPalette.length]
        _update(index, { "color": nextColor })
    }

    function _cycleTarget(index) {
        var threshold = _thresholdAt(index)
        if (!threshold)
            return
        if (bridge && typeof bridge.cycleThresholdTarget === "function" && widgetIndex >= 0) {
            bridge.cycleThresholdTarget(widgetIndex, index)
            return
        }
        if (!Array.isArray(thresholdTargets) || thresholdTargets.length === 0)
            return
        var targetIndex = thresholdTargets.indexOf(threshold.flashTarget)
        var nextTarget = thresholdTargets[(targetIndex + 1 + thresholdTargets.length) % thresholdTargets.length]
        _update(index, { "flashTarget": nextTarget })
    }

    Rectangle {
        width: parent.width
        height: descLabel.implicitHeight + 10
        color: "transparent"

        Text {
            id: descLabel
            anchors.left: parent.left
            anchors.leftMargin: 16
            anchors.right: parent.right
            anchors.rightMargin: 10
            anchors.verticalCenter: parent.verticalCenter
            wrapMode: Text.WordWrap
            text: "Each entry is an upper bound. Above all thresholds the widget uses its default color."
            color: textMuted
            font.pixelSize: fontSmall
            font.family: fontFamily
        }

        Rectangle {
            anchors.bottom: parent.bottom
            width: parent.width
            height: 1
            color: borderColor
            opacity: 0.4
        }
    }

    Repeater {
        model: root.thresholds

        delegate: Column {
            id: entry
            required property var modelData
            required property int index

            width: root.width
            spacing: 0

            Rectangle {
                id: row1
                width: parent.width
                height: 34
                color: "transparent"

                Rectangle {
                    anchors.fill: parent
                    opacity: rowHover.hovered ? 1 : 0
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
                    spacing: 6

                    Rectangle {
                        width: 16
                        height: 16
                        radius: 9
                        color: entry.modelData && typeof entry.modelData.color === "string" ? entry.modelData.color : textMuted
                        border.width: 1
                        border.color: Qt.darker(color, 1.4)

                        Text {
                            anchors.centerIn: parent
                            text: entry.index + 1
                            font.pixelSize: 8
                            font.weight: Font.Bold
                            font.family: fontFamily
                            color: Qt.hsla(0, 0, Qt.colorEqual(parent.color, "black") ? 1 : 0, 1)
                        }

                        MouseArea {
                            anchors.fill: parent
                            onClicked: root._cycleColor(entry.index)
                        }
                    }

                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        text: "\u2264"
                        color: textSecondary
                        font.pixelSize: fontBase
                        font.family: fontFamily
                    }

                    NumberStepper {
                        anchors.verticalCenter: parent.verticalCenter
                        value: entry.modelData && typeof entry.modelData.value === "number" ? entry.modelData.value : 0
                        step: 1
                        min: -9999
                        max: 9999
                        onCommit: (v) => root._update(entry.index, { "value": v })
                    }
                }

                Row {
                    anchors.right: parent.right
                    anchors.rightMargin: 8
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 8

                    ColorPicker {
                        anchors.verticalCenter: parent.verticalCenter
                        value: entry.modelData && typeof entry.modelData.color === "string" ? entry.modelData.color : "#E0E0E0"
                        onColorPicked: (hex) => root._update(entry.index, { "color": hex })
                    }

                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        text: "Flash"
                        color: textMuted
                        font.pixelSize: fontSmall
                        font.family: fontFamily
                    }

                    ToggleSwitch {
                        anchors.verticalCenter: parent.verticalCenter
                        checked: entry.modelData && typeof entry.modelData.flash === "boolean" ? entry.modelData.flash : false
                        onToggled: (v) => root._update(entry.index, { "flash": v })
                    }

                    Rectangle {
                        anchors.verticalCenter: parent.verticalCenter
                        width: 18
                        height: 18
                        radius: 11
                        color: rmArea.containsMouse ? "#40FF4444" : "transparent"
                        border.width: 1
                        border.color: rmArea.containsMouse ? "#FF4444" : borderColor
                        Behavior on color { ColorAnimation { duration: 80 } }
                        Behavior on border.color { ColorAnimation { duration: 80 } }

                        Text {
                            anchors.centerIn: parent
                            text: "\u00d7"
                            font.pixelSize: 12
                            font.family: fontFamily
                            color: rmArea.containsMouse ? "#FF4444" : textMuted
                            Behavior on color { ColorAnimation { duration: 80 } }
                        }

                        MouseArea {
                            id: rmArea
                            anchors.fill: parent
                            hoverEnabled: true
                            onClicked: root._remove(entry.index)
                        }
                    }
                }

                HoverHandler { id: rowHover }
            }

            Rectangle {
                id: row2
                width: parent.width
                readonly property bool expanded: entry.modelData && entry.modelData.flash
                height: expanded ? 30 : 0
                clip: true
                color: surfaceAlt
                opacity: expanded ? 1 : 0

                Behavior on height { NumberAnimation { duration: 150; easing.type: Easing.OutCubic } }
                Behavior on opacity { NumberAnimation { duration: 120 } }

                Row {
                    anchors.left: parent.left
                    anchors.leftMargin: 38
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 10

                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        text: "Target"
                        color: textMuted
                        font.pixelSize: fontSmall
                        font.family: fontFamily
                    }

                    ThemedComboBox {
                        anchors.verticalCenter: parent.verticalCenter
                        model: root.thresholdTargets
                        implicitWidth: 72
                        currentIndex: {
                            var currentTarget = entry.modelData && typeof entry.modelData.flashTarget === "string"
                                ? entry.modelData.flashTarget
                                : "value"
                            var found = root.thresholdTargets.indexOf(currentTarget)
                            return found >= 0 ? found : 0
                        }
                        onActivated: (i) => root._update(entry.index, { "flashTarget": root.thresholdTargets[i] })
                    }

                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        text: "Speed"
                        color: textMuted
                        font.pixelSize: fontSmall
                        font.family: fontFamily
                    }

                    NumberStepper {
                        anchors.verticalCenter: parent.verticalCenter
                        value: entry.modelData && typeof entry.modelData.flashSpeed === "number" ? entry.modelData.flashSpeed : 4
                        step: 1
                        min: 1
                        max: 20
                        onCommit: (v) => root._update(entry.index, { "flashSpeed": v })
                    }
                }
            }

            Rectangle {
                width: parent.width
                height: 1
                color: borderColor
                opacity: 0.4
            }
        }
    }

    Rectangle {
        width: parent.width
        height: 34
        color: "transparent"

        Rectangle {
            anchors.left: parent.left
            anchors.leftMargin: 16
            anchors.verticalCenter: parent.verticalCenter
            width: 122
            height: 24
            radius: 4
            color: addArea.containsMouse ? surfaceRaised : "transparent"
            border.width: 1
            border.color: borderColor
            Behavior on color { ColorAnimation { duration: 80 } }

            Row {
                anchors.centerIn: parent
                spacing: 5

                Text {
                    anchors.verticalCenter: parent.verticalCenter
                    text: "+"
                    font.pixelSize: 14
                    font.family: fontFamily
                    color: addArea.containsMouse ? accentColor : textMuted
                    Behavior on color { ColorAnimation { duration: 80 } }
                }

                Text {
                    anchors.verticalCenter: parent.verticalCenter
                    text: "Add threshold"
                    font.pixelSize: fontSmall
                    font.family: fontFamily
                    color: addArea.containsMouse ? accentColor : textMuted
                    Behavior on color { ColorAnimation { duration: 80 } }
                }
            }

            MouseArea {
                id: addArea
                anchors.fill: parent
                hoverEnabled: true
                onClicked: root._add()
            }
        }
    }
}
