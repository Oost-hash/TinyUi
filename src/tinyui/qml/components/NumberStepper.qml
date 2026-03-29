import QtQuick

Row {
    id: root

    property real value: 0
    property real step: 1
    property real min: -999999
    property real max: 999999

    signal commit(real value)

    spacing: 8

    function _clamp(nextValue) {
        return Math.max(root.min, Math.min(root.max, nextValue))
    }

    function _commit(nextValue) {
        var clamped = _clamp(nextValue)
        valueLabel.text = Number(clamped).toString()
        root.commit(clamped)
    }

    Rectangle {
        width: 24
        height: 24
        radius: 8
        color: "#252b34"

        Text {
            anchors.centerIn: parent
            text: "-"
            color: "#c5ccd8"
            font.pixelSize: 14
        }

        MouseArea {
            anchors.fill: parent
            onClicked: root._commit(root.value - root.step)
        }
    }

    Rectangle {
        width: 72
        height: 28
        radius: 8
        color: "#1b1f25"
        border.width: 1
        border.color: "#39414d"

        Text {
            id: valueLabel
            anchors.centerIn: parent
            text: Number(root.value).toString()
            color: "#f4f7fb"
            font.pixelSize: 13
        }
    }

    Rectangle {
        width: 24
        height: 24
        radius: 8
        color: "#252b34"

        Text {
            anchors.centerIn: parent
            text: "+"
            color: "#c5ccd8"
            font.pixelSize: 14
        }

        MouseArea {
            anchors.fill: parent
            onClicked: root._commit(root.value + root.step)
        }
    }
}
