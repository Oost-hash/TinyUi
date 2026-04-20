//  TinyUI
//  Copyright (C) 2026 Oost-hash
//
//  This file is part of TinyUI.
//
//  TinyUI is free software: you can redistribute it and/or modify
//  it under the terms of the GNU General Public License as published by
//  the Free Software Foundation, either version 3 of the License, or
//  (at your option) any later version.
//
//  TinyUI is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU General Public License for more details.
//
//  You should have received a copy of the GNU General Public License
//  along with this program.  If not, see <https://www.gnu.org/licenses/>.
//
//  TinyUI builds on TinyPedal by s-victor (https://github.com/s-victor/TinyPedal),
//  licensed under GPLv3.

pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Window

Item {
    id: listPaneRoot

    readonly property var hostWindow: Window.window
    property var theme: hostWindow && hostWindow.theme ? hostWindow.theme : null
    property var widgets: []
    property string selectedWidgetId: ""
    property string selectedOverlayId: ""
    property string diagnosticsMessage: ""
    property bool canWriteWidgetConfig: false

    readonly property int colName: 200
    readonly property int colToggle: 56
    readonly property int colPad: 16

    signal selectWidget(var widget)
    signal setWidgetEnabled(string overlayId, string widgetId, bool enabled)

    function c(token, fallback) {
        return theme ? theme[token] : fallback;
    }

    function f(token, fallback) {
        return theme ? theme[token] : fallback;
    }

    function widgetValues(widget) {
        return widget && widget.values ? widget.values : ({});
    }

    function widgetLabel(widget) {
        if (!widget)
            return "";
        var values = widgetValues(widget);
        return values.label || widget.label || widget.widgetId || "";
    }

    function widgetDescription(widget) {
        if (!widget)
            return "";
        var values = widgetValues(widget);
        if (values.description)
            return values.description;
        if (widget.resolvedValue)
            return widget.resolvedValue;
        if (widget.source)
            return widget.source;
        return widget.status || "";
    }

    function isWidgetSelected(widget) {
        return widget && selectedWidgetId === widget.widgetId && selectedOverlayId === widget.overlayId;
    }

    Rectangle {
        id: tableHeader
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 32
        color: "transparent"

        Row {
            anchors.fill: parent
            leftPadding: listPaneRoot.colPad

            Text {
                width: listPaneRoot.colName
                height: parent.height
                verticalAlignment: Text.AlignVCenter
                text: "Widget"
                color: listPaneRoot.c("text", "#dce0e5")
                font.pixelSize: listPaneRoot.f("fontSizeSmall", 11)
                font.family: listPaneRoot.f("fontFamily", "sans-serif")
            }

            Text {
                width: parent.width - listPaneRoot.colPad - listPaneRoot.colName - listPaneRoot.colToggle
                height: parent.height
                verticalAlignment: Text.AlignVCenter
                text: "Description"
                color: listPaneRoot.c("text", "#dce0e5")
                font.pixelSize: listPaneRoot.f("fontSizeSmall", 11)
                font.family: listPaneRoot.f("fontFamily", "sans-serif")
                elide: Text.ElideRight
            }

            Text {
                width: listPaneRoot.colToggle
                height: parent.height
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
                text: "On"
                color: listPaneRoot.c("text", "#dce0e5")
                font.pixelSize: listPaneRoot.f("fontSizeSmall", 11)
                font.family: listPaneRoot.f("fontFamily", "sans-serif")
            }
        }

        Rectangle {
            anchors.bottom: parent.bottom
            width: parent.width
            height: 1
            color: listPaneRoot.c("border", "#464b57")
        }
    }

    ListView {
        id: widgetList
        anchors.top: tableHeader.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        clip: true
        model: listPaneRoot.widgets
        spacing: 0

        delegate: Rectangle {
            id: row

            required property var modelData
            required property int index

            readonly property bool isSelected: listPaneRoot.isWidgetSelected(modelData)

            width: ListView.view.width
            height: 40
            color: isSelected ? listPaneRoot.c("surfaceRaised", "#3b414d") : (index % 2 === 0 ? listPaneRoot.c("surfaceAlt", "#2f343e") : "transparent")
            Behavior on color {
                ColorAnimation {
                    duration: 80
                }
            }

            Rectangle {
                width: 2
                height: parent.height
                color: listPaneRoot.c("accent", "#4a9eff")
                visible: row.isSelected
            }

            Rectangle {
                anchors.fill: parent
                opacity: rowHover.hovered && !row.isSelected ? 1 : 0
                Behavior on opacity {
                    NumberAnimation {
                        duration: 120
                    }
                }
                gradient: Gradient {
                    orientation: Gradient.Horizontal
                    GradientStop {
                        position: 0.0
                        color: "transparent"
                    }
                    GradientStop {
                        position: 0.5
                        color: "transparent"
                    }
                    GradientStop {
                        position: 1.0
                        color: "#20dec184"
                    }
                }
            }

            Rectangle {
                anchors.bottom: parent.bottom
                width: parent.width
                height: 1
                color: listPaneRoot.c("border", "#464b57")
                opacity: 0.4
            }

            Row {
                anchors.fill: parent
                leftPadding: listPaneRoot.colPad + (row.isSelected ? 8 : 0)
                Behavior on leftPadding {
                    NumberAnimation {
                        duration: 120
                    }
                }

                Text {
                    width: listPaneRoot.colName
                    height: parent.height
                    verticalAlignment: Text.AlignVCenter
                    text: listPaneRoot.widgetLabel(row.modelData)
                    color: row.isSelected ? listPaneRoot.c("accent", "#4a9eff") : listPaneRoot.c("text", "#dce0e5")
                    font.pixelSize: listPaneRoot.f("fontSizeBase", 13)
                    font.family: listPaneRoot.f("fontFamily", "sans-serif")
                    font.weight: row.isSelected ? Font.DemiBold : Font.Normal
                    elide: Text.ElideRight
                    Behavior on color {
                        ColorAnimation {
                            duration: 80
                        }
                    }
                }

                Text {
                    width: parent.width - listPaneRoot.colPad - listPaneRoot.colName - listPaneRoot.colToggle
                    height: parent.height
                    verticalAlignment: Text.AlignVCenter
                    text: listPaneRoot.widgetDescription(row.modelData)
                    color: rowHover.hovered ? "#dec184" : listPaneRoot.c("textMuted", "#878a98")
                    font.pixelSize: listPaneRoot.f("fontSizeSmall", 11)
                    font.family: listPaneRoot.f("fontFamily", "sans-serif")
                    elide: Text.ElideRight
                    Behavior on color {
                        ColorAnimation {
                            duration: 120
                        }
                    }
                }

                Item {
                    width: listPaneRoot.colToggle
                    height: parent.height

                    ToggleSwitch {
                        anchors.centerIn: parent
                        checked: row.modelData ? row.modelData.enabled : true
                        enabled: listPaneRoot.canWriteWidgetConfig && row.modelData && row.modelData.overlayId !== undefined
                        theme: listPaneRoot.theme
                        onToggled: value => {
                            if (row.modelData && row.modelData.overlayId !== undefined)
                                listPaneRoot.setWidgetEnabled(row.modelData.overlayId, row.modelData.widgetId, value);
                        }
                    }
                }
            }

            MouseArea {
                anchors.fill: parent
                anchors.rightMargin: listPaneRoot.colToggle
                acceptedButtons: Qt.LeftButton
                onClicked: listPaneRoot.selectWidget(row.modelData)
            }

            HoverHandler {
                id: rowHover
            }
        }
    }

    Rectangle {
        anchors.top: tableHeader.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        visible: listPaneRoot.diagnosticsMessage !== ""
        color: "transparent"

        Column {
            anchors.centerIn: parent
            width: Math.min(parent.width - 32, 420)
            spacing: 8

            Text {
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
                text: "No widgets found"
                color: listPaneRoot.c("text", "#dce0e5")
                font.pixelSize: listPaneRoot.f("fontSizeBase", 13)
                font.family: listPaneRoot.f("fontFamily", "sans-serif")
                font.weight: Font.DemiBold
            }

            Text {
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
                text: listPaneRoot.diagnosticsMessage
                color: listPaneRoot.c("textMuted", "#878a98")
                font.pixelSize: listPaneRoot.f("fontSizeSmall", 11)
                font.family: listPaneRoot.f("fontFamily", "sans-serif")
                wrapMode: Text.WordWrap
            }
        }
    }
}
