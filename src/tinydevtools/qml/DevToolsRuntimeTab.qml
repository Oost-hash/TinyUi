import QtQuick
import TinyDevTools 1.0

Item {
    id: root

    readonly property var vm: RuntimeViewModel ?? null

    function stateColor(state) {
        if (state === "failed")
            return "#ef5350"
        if (state === "running")
            return "#66bb6a"
        if (state === "completed")
            return "#90a4ae"
        return "#b0bec5"
    }

    Rectangle {
        anchors.fill: parent
        color: "#17181c"
    }

    Rectangle {
        id: summaryBar
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        height: 36
        color: "#22252b"

        Text {
            anchors.left: parent.left
            anchors.right: copyButton.left
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.leftMargin: 10
            anchors.rightMargin: 12
            verticalAlignment: Text.AlignVCenter
            text: root.vm ? root.vm.summary : "No runtime data"
            color: "#b0bec5"
            font.pixelSize: 12
            font.family: "Consolas, Courier New, monospace"
            elide: Text.ElideRight
        }

        Rectangle {
            id: copyButton
            anchors.right: parent.right
            anchors.verticalCenter: parent.verticalCenter
            anchors.rightMargin: 10
            width: 84
            height: 24
            radius: 3
            color: copyMouse.containsMouse ? "#2b3038" : "transparent"
            border.color: "#3a404a"
            border.width: 1
            opacity: root.vm && root.vm.units.length > 0 ? 1 : 0.45

            Text {
                anchors.centerIn: parent
                text: "Copy all"
                color: "#b0bec5"
                font.pixelSize: 11
                font.family: "Consolas, Courier New, monospace"
            }

            MouseArea {
                id: copyMouse
                anchors.fill: parent
                hoverEnabled: true
                enabled: root.vm && root.vm.units.length > 0
                onClicked: {
                    if (root.vm)
                        root.vm.copyOverview()
                }
            }
        }
    }

    Flickable {
        id: filtersFlick
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: summaryBar.bottom
        height: 32
        contentWidth: filterRow.width + 16
        contentHeight: height
        clip: true
        flickableDirection: Flickable.HorizontalFlick

        Row {
            id: filterRow
            x: 8
            y: 6
            spacing: 4

            Repeater {
                model: root.vm ? root.vm.availableStateFilters : []

                delegate: Rectangle {
                    id: chip
                    required property string modelData
                    readonly property bool active: root.vm && root.vm.stateFilters.indexOf(modelData) >= 0
                    width: chipLabel.implicitWidth + 12
                    height: 20
                    radius: 3
                    color: active ? "#24364f" : "transparent"
                    border.color: active ? "#4aa3ff" : "#3a404a"
                    border.width: 1

                    Text {
                        id: chipLabel
                        anchors.centerIn: parent
                        text: chip.modelData
                        color: chip.active ? "#4aa3ff" : "#b0bec5"
                        font.pixelSize: 10
                        font.family: "Consolas, Courier New, monospace"
                    }

                    MouseArea {
                        anchors.fill: parent
                        enabled: root.vm
                        onClicked: {
                            if (root.vm)
                                root.vm.toggleStateFilter(chip.modelData)
                        }
                    }
                }
            }

            Rectangle {
                width: 44
                height: 20
                radius: 3
                color: "#22252b"
                border.color: "#3a404a"
                border.width: 1

                Text {
                    anchors.centerIn: parent
                    text: "Reset"
                    color: "#b0bec5"
                    font.pixelSize: 10
                    font.family: "Consolas, Courier New, monospace"
                }

                MouseArea {
                    anchors.fill: parent
                    enabled: root.vm
                    onClicked: {
                        if (root.vm)
                            root.vm.resetStateFilters()
                    }
                }
            }
        }
    }

    Rectangle {
        id: headerRow
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: filtersFlick.bottom
        height: 24
        color: "#20232a"

        Row {
            anchors.fill: parent
            anchors.leftMargin: 10
            anchors.rightMargin: 10
            spacing: 8

            Repeater {
                model: [
                    { "label": "Unit", "width": 260 },
                    { "label": "State", "width": 90 },
                    { "label": "Kind", "width": 80 },
                    { "label": "Execution", "width": 100 },
                    { "label": "Parent", "width": 180 }
                ]

                delegate: Text {
                    required property var modelData
                    width: modelData.width
                    height: parent.height
                    text: modelData.label
                    color: "#8f9ba8"
                    font.pixelSize: 10
                    font.family: "Consolas, Courier New, monospace"
                    font.weight: Font.DemiBold
                    verticalAlignment: Text.AlignVCenter
                }
            }
        }
    }

    ListView {
        id: runtimeList
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: headerRow.bottom
        anchors.bottom: footerBar.top
        clip: true
        spacing: 0
        model: root.vm ? root.vm.rowsModel : null

        delegate: Rectangle {
            id: rowRoot
            required property string unitId
            required property string displayId
            required property string state
            required property string kind
            required property string execution
            required property string parentUnit
            required property int depth
            required property bool hasChildren
            required property bool expanded

            width: ListView.view.width
            height: 26
            color: index % 2 === 0 ? "transparent" : "#1b1e24"

            Row {
                anchors.fill: parent
                anchors.leftMargin: 10
                anchors.rightMargin: 10
                spacing: 8

                Item {
                    width: 260
                    height: parent.height

                    Row {
                        anchors.fill: parent
                        spacing: 0

                        Item {
                            width: rowRoot.depth * 14
                            height: parent.height
                        }

                        Text {
                            width: 16
                            height: parent.height
                            text: rowRoot.hasChildren ? (rowRoot.expanded ? "▾" : "▸") : ""
                            color: "#8f9ba8"
                            font.pixelSize: 10
                            font.family: "Consolas, Courier New, monospace"
                            verticalAlignment: Text.AlignVCenter
                        }

                        Text {
                            width: 244 - (rowRoot.depth * 14)
                            height: parent.height
                            text: rowRoot.displayId
                            color: "#e5e7eb"
                            font.pixelSize: 11
                            font.family: "Consolas, Courier New, monospace"
                            verticalAlignment: Text.AlignVCenter
                            elide: Text.ElideRight
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        enabled: rowRoot.hasChildren && root.vm
                        onClicked: root.vm.toggleExpanded(rowRoot.unitId)
                    }
                }

                Text {
                    width: 90
                    height: parent.height
                    text: rowRoot.state
                    color: root.stateColor(rowRoot.state)
                    font.pixelSize: 11
                    font.family: "Consolas, Courier New, monospace"
                    verticalAlignment: Text.AlignVCenter
                }

                Text {
                    width: 80
                    height: parent.height
                    text: rowRoot.kind
                    color: "#b0bec5"
                    font.pixelSize: 11
                    font.family: "Consolas, Courier New, monospace"
                    verticalAlignment: Text.AlignVCenter
                    elide: Text.ElideRight
                }

                Text {
                    width: 100
                    height: parent.height
                    text: rowRoot.execution
                    color: "#b0bec5"
                    font.pixelSize: 11
                    font.family: "Consolas, Courier New, monospace"
                    verticalAlignment: Text.AlignVCenter
                    elide: Text.ElideRight
                }

                Text {
                    width: 180
                    height: parent.height
                    text: rowRoot.parentUnit
                    color: "#8f9ba8"
                    font.pixelSize: 11
                    font.family: "Consolas, Courier New, monospace"
                    verticalAlignment: Text.AlignVCenter
                    elide: Text.ElideRight
                }
            }
        }

        Text {
            anchors.centerIn: parent
            visible: !root.vm || root.vm.units.length === 0
            text: "No runtime units available."
            color: "#8f9ba8"
            font.pixelSize: 12
            font.family: "Consolas, Courier New, monospace"
        }
    }

    Rectangle {
        id: footerBar
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        height: root.vm && root.vm.taskIds.length > 0 ? 28 : 0
        visible: height > 0
        color: "#20232a"

        Text {
            anchors.fill: parent
            anchors.leftMargin: 10
            anchors.rightMargin: 10
            verticalAlignment: Text.AlignVCenter
            text: root.vm ? ("Tasks: " + root.vm.taskIds.join(", ")) : ""
            color: "#8f9ba8"
            font.pixelSize: 10
            font.family: "Consolas, Courier New, monospace"
            elide: Text.ElideRight
        }
    }
}
