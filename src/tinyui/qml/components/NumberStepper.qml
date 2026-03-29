import QtQuick
import QtQuick.Window

Row {
    id: root

    readonly property var hostWindow: Window.window
    readonly property var hostTheme: hostWindow && hostWindow.theme ? hostWindow.theme : null

    property real value: 0
    property real step: 1
    property real min: -999999
    property real max: 999999

    readonly property color surfaceFloating: hostTheme ? hostTheme.surfaceFloating : "#20242b"
    readonly property color borderColor: hostTheme ? hostTheme.border : "#464B57"
    readonly property color textColor: hostTheme ? hostTheme.text : "#DCE0E5"
    readonly property color textMuted: hostTheme ? hostTheme.textMuted : "#878A98"
    readonly property color accentColor: hostTheme ? hostTheme.accent : "#74ADE8"
    readonly property int fontBase: hostTheme ? hostTheme.fontSizeBase : 13
    readonly property int fontSmall: hostTheme ? hostTheme.fontSizeSmall : 11
    readonly property string fontFamily: hostTheme ? hostTheme.fontFamily : "Segoe UI"

    signal commit(real value)

    spacing: 6

    function _clamp(nextValue) {
        return Math.max(root.min, Math.min(root.max, nextValue))
    }

    function _decimals() {
        var s = step.toString()
        var dot = s.indexOf(".")
        return dot < 0 ? 0 : s.length - dot - 1
    }

    function _format(nextValue) {
        return Number(nextValue).toFixed(_decimals())
    }

    function _round(nextValue) {
        return parseFloat(Number(nextValue).toFixed(_decimals()))
    }

    function _commit(nextValue) {
        var clamped = _round(_clamp(nextValue))
        stepEdit.text = _format(clamped)
        root.commit(clamped)
        editState.editing = false
    }

    onValueChanged: {
        if (!editState.editing)
            stepEdit.text = _format(value)
    }

    Item {
        width: 24
        height: 26
        anchors.verticalCenter: parent.verticalCenter

        Text {
            anchors.centerIn: parent
            text: "\u2212"
            color: decArea.containsMouse ? textColor : textMuted
            font.pixelSize: fontBase
            font.family: fontFamily
            Behavior on color { ColorAnimation { duration: 80 } }
        }

        MouseArea {
            id: decArea
            anchors.fill: parent
            hoverEnabled: true
            onClicked: root._commit(root.value - root.step)
        }
    }

    Rectangle {
        width: 72
        height: 28
        anchors.verticalCenter: parent.verticalCenter
        radius: 4
        color: editState.editing ? surfaceFloating : "transparent"
        border.width: 1
        border.color: editState.editing ? accentColor : (valueHover.hovered ? borderColor : "transparent")
        Behavior on border.color { ColorAnimation { duration: 80 } }
        Behavior on color { ColorAnimation { duration: 80 } }

        TextInput {
            id: stepEdit
            anchors.fill: parent
            anchors.leftMargin: 5
            anchors.rightMargin: 5
            horizontalAlignment: TextInput.AlignHCenter
            verticalAlignment: TextInput.AlignVCenter
            text: root._format(root.value)
            color: editState.editing ? accentColor : textColor
            font.pixelSize: fontSmall
            font.family: fontFamily
            selectByMouse: true
            readOnly: !editState.editing
            inputMethodHints: Qt.ImhFormattedNumbersOnly
            Behavior on color { ColorAnimation { duration: 80 } }

            Keys.onReturnPressed: root._commit(parseFloat(text))
            Keys.onEscapePressed: {
                text = root._format(root.value)
                editState.editing = false
            }
            onActiveFocusChanged: {
                if (!activeFocus && editState.editing)
                    root._commit(parseFloat(text))
            }
        }

        HoverHandler {
            id: valueHover
            enabled: !editState.editing
            cursorShape: Qt.IBeamCursor
        }

        MouseArea {
            anchors.fill: parent
            enabled: !editState.editing
            acceptedButtons: Qt.LeftButton
            onClicked: {
                editState.editing = true
                stepEdit.forceActiveFocus()
                stepEdit.selectAll()
            }
        }
    }

    Item {
        width: 24
        height: 26
        anchors.verticalCenter: parent.verticalCenter

        Text {
            anchors.centerIn: parent
            text: "+"
            color: incArea.containsMouse ? textColor : textMuted
            font.pixelSize: fontBase
            font.family: fontFamily
            Behavior on color { ColorAnimation { duration: 80 } }
        }

        MouseArea {
            id: incArea
            anchors.fill: parent
            hoverEnabled: true
            onClicked: root._commit(root.value + root.step)
        }
    }

    Item {
        id: editState
        property bool editing: false
        width: 0
        height: 0
        visible: false
    }
}
