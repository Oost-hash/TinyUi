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

import QtQuick

Rectangle {
    id: root

    property var widgetData: ({})
    property var widgetEffects: null

    readonly property bool showSource: widgetData
            && widgetData.values
            && widgetData.values.showSource === true

    width: 120
    height: showSource ? 72 : 56
    radius: 6
    color: widgetData && widgetData.backgroundColor ? widgetData.backgroundColor : "#CC000000"
    visible: widgetData && widgetData.visible !== undefined ? widgetData.visible : true

    property bool flashVisible: true
    property string flashTarget: "value"
    property string thresholdColor: ""

    // Use regular properties instead of readonly so they update when widgetData changes
    property string labelText: widgetData && widgetData.label ? widgetData.label : ""
    property string sourceText: widgetData && widgetData.source && showSource ? widgetData.source : ""
    property string displayText: widgetData && widgetData.displayText ? widgetData.displayText : ""
    property string valueColor: widgetData && widgetData.textColor ? widgetData.textColor : "#E0E0E0"
    property string effectiveValueColor: thresholdColor !== "" ? thresholdColor : valueColor

    opacity: flashTarget === "widget" ? (flashVisible ? 1.0 : 0.0) : 1.0

    function refreshEffects() {
        if (!widgetEffects || !widgetData || !widgetData.overlayId || !widgetData.widgetId) {
            flashVisible = true
            flashTarget = "value"
            thresholdColor = ""
            return
        }
        flashVisible = widgetEffects.flashVisible(widgetData.overlayId, widgetData.widgetId)
        flashTarget = widgetEffects.flashTarget(widgetData.overlayId, widgetData.widgetId)
        thresholdColor = widgetEffects.textColor(widgetData.overlayId, widgetData.widgetId, "")
    }

    // Force property update when widgetData changes
    onWidgetDataChanged: {
        // Explicitly update text properties to force re-evaluation
        labelText = widgetData && widgetData.label ? widgetData.label : ""
        sourceText = widgetData && widgetData.source && showSource ? widgetData.source : ""
        displayText = widgetData && widgetData.displayText ? widgetData.displayText : ""
        valueColor = widgetData && widgetData.textColor ? widgetData.textColor : "#E0E0E0"
        refreshEffects()
    }
    onWidgetEffectsChanged: refreshEffects()
    Component.onCompleted: refreshEffects()

    Connections {
        target: root.widgetEffects
        function onEffectsChanged(overlayId, widgetId) {
            if (root.widgetData
                    && root.widgetData.overlayId === overlayId
                    && root.widgetData.widgetId === widgetId) {
                root.refreshEffects()
            }
        }
    }

    Column {
        anchors.centerIn: parent
        spacing: 2
        opacity: root.flashTarget === "text" ? (root.flashVisible ? 1.0 : 0.0) : 1.0

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: root.labelText
            color: "#888888"
            font.pixelSize: 10
            font.family: "Segoe UI"
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: root.displayText
            color: root.effectiveValueColor
            opacity: root.flashTarget === "value" ? (root.flashVisible ? 1.0 : 0.0) : 1.0
            font.pixelSize: 22
            font.bold: true
            font.family: "Segoe UI"
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: root.sourceText
            color: "#6E6E6E"
            font.pixelSize: 10
            font.family: "Segoe UI"
            visible: root.sourceText.length > 0
        }
    }
}
