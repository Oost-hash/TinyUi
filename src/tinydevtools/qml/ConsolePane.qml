import QtQuick
import TinyDevTools 1.0

Item {
    id: root

    property bool showDebug: true
    property bool showInfo: true
    property bool showWarning: true
    property bool showError: true

    function levelVisible(level) {
        if (level === "DEBUG")
            return root.showDebug
        if (level === "INFO")
            return root.showInfo
        if (level === "WARNING")
            return root.showWarning
        return root.showError
    }

    function levelColor(level) {
        if (level === "DEBUG")
            return "#8f9ba8"
        if (level === "INFO")
            return "#e5e7eb"
        if (level === "WARNING")
            return "#f4b400"
        return "#ef5350"
    }

    ListModel {
        id: logModel
    }

    Rectangle {
        anchors.fill: parent
        color: "#17181c"
    }

    Rectangle {
        id: toolbar
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        height: 36
        color: "#22252b"

        Row {
            anchors.fill: parent
            anchors.leftMargin: 8
            anchors.rightMargin: 8
            spacing: 4

            Repeater {
                model: ["DEBUG", "INFO", "WARN", "ERROR"]

                delegate: Rectangle {
                    id: chip
                    required property string modelData
                    readonly property bool active: {
                        if (modelData === "DEBUG")
                            return root.showDebug
                        if (modelData === "INFO")
                            return root.showInfo
                        if (modelData === "WARN")
                            return root.showWarning
                        return root.showError
                    }
                    readonly property color chipColor: {
                        if (modelData === "DEBUG")
                            return "#8f9ba8"
                        if (modelData === "INFO")
                            return "#e5e7eb"
                        if (modelData === "WARN")
                            return "#f4b400"
                        return "#ef5350"
                    }

                    width: 52
                    height: 22
                    radius: 3
                    anchors.verticalCenter: parent.verticalCenter
                    color: chip.active ? Qt.rgba(chip.chipColor.r, chip.chipColor.g, chip.chipColor.b, 0.15) : "transparent"
                    border.color: chip.active ? chip.chipColor : "#3a404a"
                    border.width: 1

                    Text {
                        anchors.centerIn: parent
                        text: chip.modelData
                        color: chip.active ? chip.chipColor : "#8f9ba8"
                        font.pixelSize: 10
                        font.family: "Consolas, Courier New, monospace"
                        font.weight: Font.DemiBold
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            if (chip.modelData === "DEBUG")
                                root.showDebug = !root.showDebug
                            if (chip.modelData === "INFO")
                                root.showInfo = !root.showInfo
                            if (chip.modelData === "WARN")
                                root.showWarning = !root.showWarning
                            if (chip.modelData === "ERROR")
                                root.showError = !root.showError
                        }
                    }
                }
            }

            Item {
                width: Math.max(0, parent.width - 310)
                height: 1
            }

            Rectangle {
                width: 104
                height: 22
                radius: 3
                anchors.verticalCenter: parent.verticalCenter
                color: autoScrollMouse.containsMouse ? "#2b3038" : "transparent"
                border.color: autoScroll ? "#4aa3ff" : "#3a404a"
                border.width: 1

                Text {
                    anchors.centerIn: parent
                    text: autoScroll ? "Auto-scroll ON" : "Auto-scroll OFF"
                    color: autoScroll ? "#4aa3ff" : "#8f9ba8"
                    font.pixelSize: 10
                    font.family: "Consolas, Courier New, monospace"
                }

                MouseArea {
                    id: autoScrollMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: autoScroll = !autoScroll
                }
            }

            Rectangle {
                width: 48
                height: 22
                radius: 3
                anchors.verticalCenter: parent.verticalCenter
                color: clearMouse.containsMouse ? "#2b3038" : "transparent"
                border.color: "#3a404a"
                border.width: 1

                Text {
                    anchors.centerIn: parent
                    text: "Clear"
                    color: "#8f9ba8"
                    font.pixelSize: 10
                    font.family: "Consolas, Courier New, monospace"
                }

                MouseArea {
                    id: clearMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: {
                        logModel.clear()
                        LogViewModel.clear()
                    }
                }
            }
        }
    }

    Rectangle {
        id: categoryBar
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: toolbar.bottom
        height: 30
        color: "#1d2026"

        Flickable {
            anchors.fill: parent
            contentWidth: categoryRow.width + 16
            contentHeight: height
            clip: true
            flickableDirection: Flickable.HorizontalFlick

            Row {
                id: categoryRow
                x: 8
                y: 5
                spacing: 4

                Rectangle {
                    width: 44
                    height: 20
                    radius: 3
                    readonly property bool allOn: LogSettingsViewModel ? LogSettingsViewModel.allCategoriesEnabled : false
                    color: allOn ? "#24364f" : "transparent"
                    border.color: allOn ? "#4aa3ff" : "#3a404a"
                    border.width: 1

                    Text {
                        anchors.centerIn: parent
                        text: "ALL"
                        color: parent.allOn ? "#4aa3ff" : "#8f9ba8"
                        font.pixelSize: 10
                        font.family: "Consolas, Courier New, monospace"
                        font.weight: Font.Bold
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            if (LogSettingsViewModel)
                                LogSettingsViewModel.setDevMode(!LogSettingsViewModel.allCategoriesEnabled)
                        }
                    }
                }

                Repeater {
                    model: LogSettingsViewModel ? LogSettingsViewModel.categories : []

                    delegate: Rectangle {
                        id: categoryChip
                        required property var modelData
                        readonly property bool enabledState: categoryChip.modelData.enabled
                        width: categoryLabel.implicitWidth + 12
                        height: 20
                        radius: 3
                        color: enabledState ? "#24364f" : "transparent"
                        border.color: enabledState ? "#4aa3ff" : "#3a404a"
                        border.width: 1

                        Text {
                            id: categoryLabel
                            anchors.centerIn: parent
                            text: categoryChip.modelData.name
                            color: categoryChip.enabledState ? "#4aa3ff" : "#8f9ba8"
                            font.pixelSize: 10
                            font.family: "Consolas, Courier New, monospace"
                        }

                        MouseArea {
                            anchors.fill: parent
                            onClicked: {
                                if (LogSettingsViewModel) {
                                    LogSettingsViewModel.setCategoryEnabled(
                                        categoryChip.modelData.name,
                                        !categoryChip.modelData.enabled
                                    )
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    property bool autoScroll: true

    ListView {
        id: logList
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: categoryBar.bottom
        anchors.bottom: parent.bottom
        clip: true
        spacing: 0
        model: logModel

        delegate: Item {
            id: logRow
            required property string level
            required property string time
            required property string name
            required property string message

            width: logList.width
            visible: root.levelVisible(logRow.level)
            height: visible ? 24 : 0

            Row {
                anchors.fill: parent
                anchors.leftMargin: 8
                anchors.rightMargin: 8
                spacing: 8

                Text {
                    width: 70
                    height: parent.height
                    text: logRow.time
                    color: "#8f9ba8"
                    font.pixelSize: 11
                    font.family: "Consolas, Courier New, monospace"
                    verticalAlignment: Text.AlignVCenter
                }

                Rectangle {
                    width: 52
                    height: 16
                    radius: 2
                    anchors.verticalCenter: parent.verticalCenter
                    color: Qt.rgba(root.levelColor(logRow.level).r, root.levelColor(logRow.level).g, root.levelColor(logRow.level).b, 0.15)

                    Text {
                        anchors.centerIn: parent
                        text: logRow.level === "CRITICAL" ? "CRIT" : logRow.level
                        color: root.levelColor(logRow.level)
                        font.pixelSize: 10
                        font.family: "Consolas, Courier New, monospace"
                        font.weight: Font.Bold
                    }
                }

                Text {
                    width: 200
                    height: parent.height
                    text: logRow.name
                    color: "#c7d0db"
                    font.pixelSize: 11
                    font.family: "Consolas, Courier New, monospace"
                    verticalAlignment: Text.AlignVCenter
                    elide: Text.ElideRight
                }

                Text {
                    width: parent.width - 346
                    height: parent.height
                    text: logRow.message
                    color: root.levelColor(logRow.level)
                    font.pixelSize: 11
                    font.family: "Consolas, Courier New, monospace"
                    verticalAlignment: Text.AlignVCenter
                    elide: Text.ElideRight
                }
            }
        }

        onCountChanged: {
            if (root.autoScroll)
                logList.positionViewAtEnd()
        }
    }

    Connections {
        target: LogViewModel

        function onRecordAdded(time, level, name, message) {
            logModel.append({ time, level, name, message })
        }

        function onCleared() {
            logModel.clear()
        }
    }
}
