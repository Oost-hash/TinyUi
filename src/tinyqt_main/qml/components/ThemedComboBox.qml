pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls
import QtQuick.Window

ComboBox {
    id: root

    readonly property var hostWindow: Window.window
    readonly property var hostTheme: hostWindow && hostWindow.theme ? hostWindow.theme : null

    readonly property color surfaceFloating: hostTheme ? hostTheme.surfaceFloating : "#20242b"
    readonly property color surfaceRaised: hostTheme ? hostTheme.surfaceRaised : "#3B414D"
    readonly property color borderColor: hostTheme ? hostTheme.border : "#464B57"
    readonly property color accentColor: hostTheme ? hostTheme.accent : "#74ADE8"
    readonly property color textColor: hostTheme ? hostTheme.text : "#DCE0E5"
    readonly property color textMuted: hostTheme ? hostTheme.textMuted : "#878A98"
    readonly property color warningColor: hostTheme ? hostTheme.warning : "#dec184"
    readonly property int fontSmall: hostTheme ? hostTheme.fontSizeSmall : 11
    readonly property string fontFamily: hostTheme ? hostTheme.fontFamily : "Segoe UI"

    implicitWidth: 120
    implicitHeight: 28

    contentItem: Text {
        leftPadding: 8
        rightPadding: root.indicator.width + 4
        text: root.displayText
        color: textColor
        font.pixelSize: fontSmall
        font.family: fontFamily
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }

    indicator: Text {
        x: root.width - width - 8
        anchors.verticalCenter: root.verticalCenter
        text: "▾"
        color: textMuted
        font.pixelSize: 10
        font.family: fontFamily
    }

    background: Rectangle {
        color: surfaceFloating
        border.width: 1
        border.color: root.popup.opened ? accentColor : borderColor
        radius: 4
        Behavior on border.color { ColorAnimation { duration: 80 } }
    }

    popup: Popup {
        y: root.height + 2
        width: root.width
        padding: 0

        contentItem: ListView {
            clip: true
            implicitHeight: Math.min(contentHeight, 200)
            model: root.delegateModel
            currentIndex: root.highlightedIndex
        }

        background: Rectangle {
            color: surfaceFloating
            border.width: 1
            border.color: borderColor
            radius: 4
        }
    }

    delegate: ItemDelegate {
        id: delegateItem
        required property int index
        required property string modelData

        width: root.popup.width
        height: 32
        highlighted: root.highlightedIndex === index

        contentItem: Text {
            text: delegateItem.modelData
            color: delegateItem.highlighted ? warningColor : textColor
            font.pixelSize: fontSmall
            font.family: fontFamily
            verticalAlignment: Text.AlignVCenter
            leftPadding: 8
            Behavior on color { ColorAnimation { duration: 80 } }
        }

        background: Rectangle {
            color: delegateItem.highlighted ? surfaceRaised : "transparent"
        }
    }
}
