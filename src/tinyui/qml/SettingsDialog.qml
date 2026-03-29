import QtQuick
import QtQuick.Window

Window {
    id: root

    property string dialogTitle: "Settings"
    property bool open: false
    property int activeSection: 0
    property var sections: [
        { "title": "Application", "description": "" },
        { "title": "Widgets", "description": "" }
    ]

    signal closeRequested()

    width: 720
    height: 480
    minimumWidth: 540
    minimumHeight: 360
    visible: open
    color: "#15191e"
    title: dialogTitle
    flags: Qt.Window | Qt.FramelessWindowHint

    onVisibleChanged: {
        if (!visible)
            root.closeRequested()
    }

    Rectangle {
        anchors.fill: parent
        color: "#15191e"
        border.width: 1
        border.color: "#2b313a"

        Rectangle {
            id: titleBar
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            height: 40
            color: "#1b1f25"

            Text {
                anchors.left: parent.left
                anchors.leftMargin: 16
                anchors.verticalCenter: parent.verticalCenter
                text: root.dialogTitle
                color: "#f4f7fb"
                font.pixelSize: 15
                font.weight: Font.DemiBold
            }

            Rectangle {
                anchors.right: parent.right
                anchors.rightMargin: 10
                anchors.verticalCenter: parent.verticalCenter
                width: 26
                height: 26
                radius: 8
                color: "#252b34"

                Text {
                    anchors.centerIn: parent
                    text: "×"
                    color: "#f4f7fb"
                    font.pixelSize: 14
                }

                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        root.open = false
                        root.closeRequested()
                    }
                }
            }
        }

        Rectangle {
            anchors.top: titleBar.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: footer.top
            color: "#15191e"

            Rectangle {
                id: sidebar
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.bottom: parent.bottom
                width: 170
                color: "#1b1f25"
                border.width: 1
                border.color: "#2b313a"

                Column {
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 8

                    Repeater {
                        model: root.sections

                        delegate: Rectangle {
                            required property var modelData
                            required property int index

                            width: parent ? parent.width : 140
                            height: 40
                            radius: 10
                            color: root.activeSection === index ? "#e8edf5" : "#252b34"

                            Text {
                                anchors.left: parent.left
                                anchors.leftMargin: 12
                                anchors.verticalCenter: parent.verticalCenter
                                text: modelData && typeof modelData.title === "string" ? modelData.title : ""
                                color: root.activeSection === index ? "#14171b" : "#c5ccd8"
                                font.pixelSize: 13
                            }

                            MouseArea {
                                anchors.fill: parent
                                onClicked: root.activeSection = index
                            }
                        }
                    }
                }
            }

            Rectangle {
                anchors.top: parent.top
                anchors.left: sidebar.right
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                color: "#111418"

                Column {
                    anchors.fill: parent
                    anchors.margins: 22
                    spacing: 16

                    Text {
                        text: root.sections[root.activeSection].title
                        color: "#f4f7fb"
                        font.pixelSize: 20
                        font.weight: Font.DemiBold
                    }

                    Text {
                        width: parent.width
                        wrapMode: Text.WordWrap
                        text: root.sections[root.activeSection].description
                        visible: text.length > 0
                        color: "#9aa1ad"
                        font.pixelSize: 13
                    }

                    Rectangle {
                        width: parent.width
                        height: 1
                        color: "#252b34"
                    }

                    Rectangle {
                        width: parent.width
                        height: 52
                        radius: 12
                        color: "#1b1f25"

                        Text {
                            anchors.left: parent.left
                            anchors.leftMargin: 14
                            anchors.verticalCenter: parent.verticalCenter
                            text: root.sections[root.activeSection].title
                            color: "#f4f7fb"
                            font.pixelSize: 13
                        }
                    }
                }
            }
        }

        Rectangle {
            id: footer
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            height: 56
            color: "#1b1f25"

            Rectangle {
                id: closeButton
                anchors.right: parent.right
                anchors.rightMargin: 14
                anchors.verticalCenter: parent.verticalCenter
                width: 84
                height: 32
                radius: 10
                color: "#e8edf5"

                Text {
                    anchors.centerIn: parent
                    text: "Close"
                    color: "#14171b"
                    font.pixelSize: 12
                    font.weight: Font.DemiBold
                }

                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        root.open = false
                        root.closeRequested()
                    }
                }
            }
        }
    }
}
