import QtQuick
import TinyDevTools 1.0

Item {
    id: root

    property real currentTime: Date.now()
    readonly property var vm: StateMonitorViewModel ?? null

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
            anchors.leftMargin: 10
            anchors.rightMargin: 10
            spacing: 6

            Repeater {
                model: root.vm ? root.vm.sources : []

                delegate: Rectangle {
                    id: sourceChip
                    required property var modelData
                    required property int index
                    readonly property bool active: root.vm && root.vm.selectedIndex === index
                    width: Math.max(88, sourceLabel.implicitWidth + 14)
                    height: 24
                    radius: 3
                    anchors.verticalCenter: parent.verticalCenter
                    color: active ? "#24364f" : "transparent"
                    border.color: active ? "#4aa3ff" : "#3a404a"
                    border.width: 1

                    Text {
                        id: sourceLabel
                        anchors.centerIn: parent
                        text: sourceChip.modelData.label
                        color: sourceChip.active ? "#4aa3ff" : "#b0bec5"
                        font.pixelSize: 11
                        font.family: "Consolas, Courier New, monospace"
                        elide: Text.ElideRight
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            if (root.vm)
                                root.vm.selectSource(sourceChip.index)
                        }
                    }
                }
            }

            Rectangle {
                width: 72
                height: 24
                radius: 3
                anchors.verticalCenter: parent.verticalCenter
                color: copyAllMouse.containsMouse ? "#2b3038" : "transparent"
                border.color: "#3a404a"
                border.width: 1
                opacity: root.vm && root.vm.hasSelectedSource && root.vm.entries.length > 0 ? 1 : 0.45

                Text {
                    anchors.centerIn: parent
                    text: "Copy all"
                    color: "#b0bec5"
                    font.pixelSize: 11
                    font.family: "Consolas, Courier New, monospace"
                }

                MouseArea {
                    id: copyAllMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    enabled: root.vm && root.vm.hasSelectedSource && root.vm.entries.length > 0
                    onClicked: {
                        if (root.vm)
                            root.vm.copyAllEntries()
                    }
                }
            }

            Rectangle {
                width: 80
                height: 24
                radius: 3
                anchors.verticalCenter: parent.verticalCenter
                color: root.vm && root.vm.captureActive ? "#24364f" : (recordMouse.containsMouse ? "#2b3038" : "transparent")
                border.color: root.vm && root.vm.captureActive ? "#4aa3ff" : "#3a404a"
                border.width: 1
                opacity: root.vm && root.vm.hasSelectedSource ? 1 : 0.45

                Text {
                    anchors.centerIn: parent
                    text: root.vm && root.vm.captureActive ? "Recording" : "Record"
                    color: root.vm && root.vm.captureActive ? "#4aa3ff" : "#b0bec5"
                    font.pixelSize: 11
                    font.family: "Consolas, Courier New, monospace"
                }

                MouseArea {
                    id: recordMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    enabled: root.vm && root.vm.hasSelectedSource
                    onClicked: {
                        if (root.vm)
                            root.vm.toggleCapture()
                    }
                }
            }

            Rectangle {
                width: 86
                height: 24
                radius: 3
                anchors.verticalCenter: parent.verticalCenter
                color: pathMouse.containsMouse ? "#2b3038" : "transparent"
                border.color: "#3a404a"
                border.width: 1
                opacity: root.vm && root.vm.captureActive ? 1 : 0.45

                Text {
                    anchors.centerIn: parent
                    text: "Copy path"
                    color: "#b0bec5"
                    font.pixelSize: 11
                    font.family: "Consolas, Courier New, monospace"
                }

                MouseArea {
                    id: pathMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    enabled: root.vm && root.vm.captureActive
                    onClicked: {
                        if (root.vm)
                            root.vm.copyCapturePath()
                    }
                }
            }
        }
    }

    ListView {
        id: stateList
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: toolbar.bottom
        anchors.bottom: parent.bottom
        clip: true
        spacing: 0
        model: root.vm ? root.vm.sectionModel : null

        delegate: Item {
            id: rowRoot
            required property string rowType
            required property int index
            required property bool collapsed
            required property string sectionTitle
            required property int sectionCount
            required property string sectionName
            required property string keyText
            required property string valueText
            required property real changedAt

            readonly property bool isSection: rowType === "section"
            readonly property bool recentlyChanged: !isSection && (root.currentTime - changedAt) < 600
            property real copiedAt: 0
            readonly property bool showCopied: !isSection && (root.currentTime - copiedAt) < 900

            width: ListView.view.width
            height: isSection ? 28 : 22

            Rectangle {
                anchors.fill: parent
                color: rowRoot.isSection
                       ? "#20232a"
                       : (rowRoot.recentlyChanged ? "#24FFD700" : (rowRoot.index % 2 === 0 ? "transparent" : "#1b1e24"))
            }

            Row {
                visible: rowRoot.isSection
                anchors.fill: parent
                anchors.leftMargin: 12
                anchors.rightMargin: 12
                spacing: 8

                Text {
                    width: 14
                    height: parent.height
                    text: rowRoot.collapsed ? "▸" : "▾"
                    color: "#8f9ba8"
                    font.pixelSize: 10
                    font.family: "Consolas, Courier New, monospace"
                    verticalAlignment: Text.AlignVCenter
                }

                Text {
                    width: parent.width - 72
                    height: parent.height
                    text: rowRoot.sectionTitle
                    color: "#d0d6de"
                    font.pixelSize: 12
                    font.family: "Consolas, Courier New, monospace"
                    font.weight: Font.DemiBold
                    verticalAlignment: Text.AlignVCenter
                    elide: Text.ElideRight
                }

                Text {
                    width: 40
                    height: parent.height
                    text: rowRoot.sectionCount
                    color: "#8f9ba8"
                    font.pixelSize: 10
                    font.family: "Consolas, Courier New, monospace"
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignRight
                }
            }

            MouseArea {
                visible: rowRoot.isSection
                anchors.fill: parent
                onClicked: {
                    if (root.vm)
                        root.vm.toggleSection(rowRoot.sectionName)
                }
            }

            Row {
                visible: !rowRoot.isSection
                anchors.fill: parent
                anchors.leftMargin: 24
                anchors.rightMargin: 12
                spacing: 6

                Rectangle {
                    width: 6
                    height: 6
                    radius: 3
                    anchors.verticalCenter: parent.verticalCenter
                    color: (root.currentTime - rowRoot.changedAt) < 2000 ? "#44FF88" : "#3a404a"
                }

                Text {
                    width: parent.width * 0.56
                    height: parent.height
                    text: rowRoot.keyText
                    color: "#b0bec5"
                    font.pixelSize: 11
                    font.family: "Consolas, Courier New, monospace"
                    verticalAlignment: Text.AlignVCenter
                    elide: Text.ElideLeft
                }

                Item {
                    width: parent.width * 0.36
                    height: parent.height

                    Text {
                        anchors.fill: parent
                        text: rowRoot.showCopied ? "Copied" : rowRoot.valueText
                        color: rowRoot.showCopied ? "#4aa3ff" : "#e5e7eb"
                        font.pixelSize: 11
                        font.family: "Consolas, Courier New, monospace"
                        verticalAlignment: Text.AlignVCenter
                        elide: Text.ElideRight
                    }

                    MouseArea {
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: {
                            if (root.vm) {
                                root.vm.copyEntry(rowRoot.keyText, rowRoot.valueText)
                                rowRoot.copiedAt = Date.now()
                            }
                        }
                    }
                }
            }
        }

        Text {
            anchors.centerIn: parent
            visible: !root.vm || root.vm.sources.length === 0 || !root.vm.hasSelectedSource || stateList.count === 0
            text: !root.vm || root.vm.sources.length === 0
                  ? "No sources available."
                  : (!root.vm.hasSelectedSource ? "Select a source above." : "No state available for this source yet.")
            color: "#8f9ba8"
            font.pixelSize: 12
            font.family: "Consolas, Courier New, monospace"
        }
    }
}
