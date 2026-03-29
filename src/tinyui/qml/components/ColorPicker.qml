pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls
import QtQuick.Window

Item {
    id: root

    readonly property var hostWindow: Window.window
    readonly property var hostTheme: hostWindow && hostWindow.theme ? hostWindow.theme : null

    property color value: "#ffffff"
    signal colorPicked(string hex)

    readonly property color surfaceColor: hostTheme ? hostTheme.surface : "#282C33"
    readonly property color surfaceFloating: hostTheme ? hostTheme.surfaceFloating : "#20242b"
    readonly property color surfaceRaised: hostTheme ? hostTheme.surfaceRaised : "#3B414D"
    readonly property color borderColor: hostTheme ? hostTheme.border : "#464B57"
    readonly property color accentColor: hostTheme ? hostTheme.accent : "#74ADE8"
    readonly property color accentTextColor: hostTheme ? hostTheme.accentText : "#111418"
    readonly property color textColor: hostTheme ? hostTheme.text : "#DCE0E5"
    readonly property int fontSmall: hostTheme ? hostTheme.fontSizeSmall : 11
    readonly property string fontFamily: hostTheme ? hostTheme.fontFamily : "Segoe UI"

    implicitWidth: swatchRow.implicitWidth
    implicitHeight: swatchRow.implicitHeight

    property real _h: 0
    property real _s: 1
    property real _v: 1

    Component.onCompleted: _syncFromValue()
    onValueChanged: _syncFromValue()

    function _syncFromValue() {
        var c = Qt.colorEqual(value, "transparent") ? Qt.color("white") : value
        _h = c.hsvHue < 0 ? 0 : c.hsvHue
        _s = c.hsvSaturation
        _v = c.hsvValue
    }

    function _currentColor() { return Qt.hsva(_h, _s, _v, 1) }

    function _toHex(c) {
        var r = Math.round(c.r * 255).toString(16).padStart(2, "0")
        var g = Math.round(c.g * 255).toString(16).padStart(2, "0")
        var b = Math.round(c.b * 255).toString(16).padStart(2, "0")
        return "#" + r + g + b
    }

    Row {
        id: swatchRow
        spacing: 6
        anchors.verticalCenter: parent.verticalCenter

        Rectangle {
            id: swatch
            width: 20
            height: 20
            radius: 4
            anchors.verticalCenter: parent.verticalCenter
            color: root.value
            border.width: 1
            border.color: borderColor

            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                onClicked: root._openPicker()
            }
        }

        Rectangle {
            width: 92
            height: 28
            radius: 4
            anchors.verticalCenter: parent.verticalCenter
            color: surfaceFloating
            border.width: 1
            border.color: hexInput.activeFocus ? accentColor : borderColor
            Behavior on border.color { ColorAnimation { duration: 80 } }

            TextInput {
                id: hexInput
                anchors.fill: parent
                anchors.leftMargin: 8
                anchors.rightMargin: 8
                verticalAlignment: TextInput.AlignVCenter
                text: root._toHex(root.value)
                color: textColor
                font.pixelSize: fontSmall
                font.family: fontFamily
                maximumLength: 7
                selectByMouse: true
                Keys.onReturnPressed: root._commitHex(text)
                Keys.onEscapePressed: { text = root._toHex(root.value); focus = false }
                onActiveFocusChanged: if (!activeFocus) text = root._toHex(root.value)
            }
        }
    }

    function _commitHex(txt) {
        if (/^#[0-9A-Fa-f]{6}$/.test(txt)) {
            root.value = txt
            root.colorPicked(txt)
            hexInput.focus = false
        } else {
            hexInput.text = root._toHex(root.value)
        }
    }

    function _openPicker() {
        root._syncFromValue()
        var global = swatch.mapToGlobal(swatch.width / 2, 0)
        pickerWin.x = Math.round(global.x - pickerWin.width / 2)
        pickerWin.y = Math.round(global.y - pickerWin.height)
        pickerWin.show()
        pickerWin.requestActivate()
    }

    Window {
        id: pickerWin
        flags: Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        color: "transparent"
        width: 244
        height: pickerContent.height + arrow.height

        onActiveChanged: if (!active) pickerWin.hide()

        Connections {
            target: root.Window.window
            function onXChanged() { pickerWin.hide() }
            function onYChanged() { pickerWin.hide() }
            function onWidthChanged() { pickerWin.hide() }
            function onHeightChanged() { pickerWin.hide() }
        }

        readonly property int _arrowH: 10
        readonly property int _arrowW: 18
        readonly property int _radius: 8

        Canvas {
            id: arrow
            anchors.bottom: parent.bottom
            anchors.horizontalCenter: parent.horizontalCenter
            width: pickerWin._arrowW
            height: pickerWin._arrowH

            onPaint: {
                var ctx = getContext("2d")
                ctx.clearRect(0, 0, width, height)
                ctx.fillStyle = borderColor
                ctx.strokeStyle = borderColor
                ctx.beginPath()
                ctx.moveTo(0, 0)
                ctx.lineTo(width / 2, height)
                ctx.lineTo(width, 0)
                ctx.fill()
                ctx.fillStyle = surfaceFloating
                ctx.beginPath()
                ctx.moveTo(1, 0)
                ctx.lineTo(width / 2, height - 1)
                ctx.lineTo(width - 1, 0)
                ctx.fill()
            }
        }

        Rectangle {
            id: pickerContent
            anchors.top: parent.top
            anchors.horizontalCenter: parent.horizontalCenter
            width: pickerWin.width
            height: 268
            radius: pickerWin._radius
            color: surfaceFloating
            border.width: 1
            border.color: borderColor

            Column {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 8

                Item {
                    id: svSquare
                    width: parent.width
                    height: 150

                    Rectangle { anchors.fill: parent; radius: 4; color: Qt.hsva(root._h, 1, 1, 1) }
                    Rectangle {
                        anchors.fill: parent; radius: 4
                        gradient: Gradient {
                            orientation: Gradient.Horizontal
                            GradientStop { position: 0.0; color: "white" }
                            GradientStop { position: 1.0; color: "transparent" }
                        }
                    }
                    Rectangle {
                        anchors.fill: parent; radius: 4
                        gradient: Gradient {
                            GradientStop { position: 0.0; color: "transparent" }
                            GradientStop { position: 1.0; color: "black" }
                        }
                    }

                    Rectangle {
                        x: root._s * svSquare.width - width / 2
                        y: (1 - root._v) * svSquare.height - height / 2
                        width: 10
                        height: 10
                        radius: 5
                        color: "transparent"
                        border.width: 2
                        border.color: root._v > 0.4 ? "black" : "white"
                    }

                    MouseArea {
                        anchors.fill: parent
                        onPositionChanged: (m) => svSquare._updateSV(m.x, m.y)
                        onPressed: (m) => svSquare._updateSV(m.x, m.y)
                    }

                    function _updateSV(mx, my) {
                        root._s = Math.max(0, Math.min(1, mx / svSquare.width))
                        root._v = Math.max(0, Math.min(1, 1 - my / svSquare.height))
                    }
                }

                Item {
                    id: hueSlider
                    width: parent.width
                    height: 14

                    Rectangle {
                        anchors.fill: parent; radius: 7
                        gradient: Gradient {
                            orientation: Gradient.Horizontal
                            GradientStop { position: 0/6; color: "#ff0000" }
                            GradientStop { position: 1/6; color: "#ffff00" }
                            GradientStop { position: 2/6; color: "#00ff00" }
                            GradientStop { position: 3/6; color: "#00ffff" }
                            GradientStop { position: 4/6; color: "#0000ff" }
                            GradientStop { position: 5/6; color: "#ff00ff" }
                            GradientStop { position: 6/6; color: "#ff0000" }
                        }
                    }

                    Rectangle {
                        x: root._h * hueSlider.width - width / 2
                        y: hueSlider.height / 2 - height / 2
                        width: 10
                        height: 14
                        radius: 3
                        color: "transparent"
                        border.width: 2
                        border.color: "white"
                    }

                    MouseArea {
                        anchors.fill: parent
                        onPositionChanged: (m) => root._h = Math.max(0, Math.min(1, m.x / hueSlider.width))
                        onPressed: (m) => root._h = Math.max(0, Math.min(1, m.x / hueSlider.width))
                    }
                }

                Row {
                    width: parent.width
                    spacing: 8

                    Rectangle {
                        width: 32
                        height: 28
                        radius: 4
                        color: root._currentColor()
                        border.width: 1
                        border.color: borderColor
                    }

                    Rectangle {
                        width: parent.width - 32 - 8
                        height: 28
                        radius: 4
                        color: surfaceColor
                        border.width: 1
                        border.color: pickerHex.activeFocus ? accentColor : borderColor
                        Behavior on border.color { ColorAnimation { duration: 80 } }

                        TextInput {
                            id: pickerHex
                            anchors.fill: parent
                            anchors.leftMargin: 8
                            anchors.rightMargin: 8
                            verticalAlignment: TextInput.AlignVCenter
                            text: root._toHex(root._currentColor())
                            color: textColor
                            font.pixelSize: fontSmall
                            font.family: fontFamily
                            maximumLength: 7
                            selectByMouse: true

                            Connections {
                                target: root
                                function on_HChanged() { pickerHex.text = root._toHex(root._currentColor()) }
                                function on_SChanged() { pickerHex.text = root._toHex(root._currentColor()) }
                                function on_VChanged() { pickerHex.text = root._toHex(root._currentColor()) }
                            }

                            Keys.onReturnPressed: {
                                if (/^#[0-9A-Fa-f]{6}$/.test(text)) {
                                    root.value = text
                                    root._syncFromValue()
                                } else {
                                    text = root._toHex(root._currentColor())
                                }
                            }
                            Keys.onEscapePressed: { text = root._toHex(root._currentColor()); focus = false }
                        }
                    }
                }

                Rectangle {
                    width: parent.width
                    height: 28
                    radius: 4
                    color: okArea.containsMouse ? accentColor : surfaceRaised
                    Behavior on color { ColorAnimation { duration: 80 } }

                    Text {
                        anchors.centerIn: parent
                        text: "OK"
                        color: okArea.containsMouse ? accentTextColor : textColor
                        font.pixelSize: fontSmall
                        font.family: fontFamily
                        font.weight: Font.Medium
                        Behavior on color { ColorAnimation { duration: 80 } }
                    }

                    MouseArea {
                        id: okArea
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: {
                            var hex = root._toHex(root._currentColor())
                            root.value = hex
                            root.colorPicked(hex)
                            pickerWin.hide()
                        }
                    }
                }
            }
        }
    }
}
