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
import "../components"

Item {
    id: panel
    anchors.fill: parent
    opacity: settingsPanelViewModel.open ? 1 : 0
    visible: opacity > 0
    z: 5

    Behavior on opacity {
        NumberAnimation { duration: 180; easing.type: Easing.OutCubic }
    }

    Component.onCompleted: {
        console.log("[SettingsPanel] model count:", coreViewModel.settingsByPlugin.length)
        console.log("[SettingsPanel] model:", JSON.stringify(coreViewModel.settingsByPlugin))
    }

    onVisibleChanged: {
        if (visible)
            console.log("[SettingsPanel] opened, model count:", coreViewModel.settingsByPlugin.length)
    }

    Rectangle { anchors.fill: parent; color: theme.surface }

    // ── Header ────────────────────────────────────────────────────────────

    Rectangle {
        id: panelHeader
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 40
        color: theme.surfaceAlt

        Text {
            anchors.left: parent.left; anchors.leftMargin: 16
            anchors.verticalCenter: parent.verticalCenter
            text: "Settings"
            color: theme.text
            font.pixelSize: theme.fontSizeBase
            font.family: theme.fontFamily
            font.weight: Font.DemiBold
        }

        Item {
            anchors.right: parent.right
            width: 40; height: parent.height
            Text {
                anchors.centerIn: parent
                text: icons.close
                font.family: theme.iconFont; font.pixelSize: 10
                color: closeHover.containsMouse ? theme.text : theme.textMuted
                Behavior on color { ColorAnimation { duration: 80 } }
            }
            MouseArea {
                id: closeHover
                anchors.fill: parent; hoverEnabled: true
                onClicked: settingsPanelViewModel.closePanel()
            }
        }

        Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: theme.border }
    }

    // ── Settings lijst ────────────────────────────────────────────────────
    // Model: [{ plugin, sections: [{ name, settings: [{key,label,type,value,description,options}] }] }]

    ListView {
        anchors.top: panelHeader.bottom
        anchors.left: parent.left; anchors.right: parent.right; anchors.bottom: parent.bottom
        clip: true
        model: coreViewModel.settingsByPlugin

        delegate: Column {
            id: pluginBlock
            required property var modelData   // { plugin, sections[] }
            width: ListView.view.width

            // Plugin header
            Rectangle {
                width: parent.width; height: 28; color: theme.surfaceAlt
                Text {
                    anchors.left: parent.left; anchors.leftMargin: 16
                    anchors.verticalCenter: parent.verticalCenter
                    text: pluginBlock.modelData.plugin
                    color: theme.textMuted
                    font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
                    font.weight: Font.Medium
                }
                Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: theme.border }
            }

            // Secties — Python heeft al gegroepeerd
            Repeater {
                model: pluginBlock.modelData.sections

                Column {
                    id: sectionBlock
                    required property var modelData   // { name, settings[] }
                    width: pluginBlock.width

                    // Sectie-header (leeg = geen header)
                    Rectangle {
                        width: parent.width
                        height: sectionBlock.modelData.name !== "" ? 28 : 0
                        visible: height > 0
                        color: theme.surface

                        Text {
                            anchors.left: parent.left; anchors.leftMargin: 24
                            anchors.verticalCenter: parent.verticalCenter
                            text: sectionBlock.modelData.name
                            color: theme.textSecondary
                            font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
                        }
                        Rectangle {
                            anchors.bottom: parent.bottom; width: parent.width; height: 1
                            color: theme.border; opacity: 0.4
                        }
                    }

                    // Setting rijen
                    Repeater {
                        model: sectionBlock.modelData.settings

                        Rectangle {
                            id: settingRow
                            required property var modelData   // {key,label,type,value,description,options}

                            width: sectionBlock.width; height: 44
                            color: rowHover.hovered ? "#dec1841a" : "transparent"
                            Behavior on color { ColorAnimation { duration: 80 } }

                            Rectangle {
                                anchors.bottom: parent.bottom; width: parent.width; height: 1
                                color: theme.border; opacity: 0.4
                            }

                            Row {
                                anchors.fill: parent; leftPadding: 16

                                Column {
                                    width: parent.width - 16 - 100
                                    anchors.verticalCenter: parent.verticalCenter
                                    spacing: 3

                                    Text {
                                        text: settingRow.modelData.label
                                        color: theme.text
                                        font.pixelSize: theme.fontSizeBase; font.family: theme.fontFamily
                                    }
                                    Text {
                                        visible: settingRow.modelData.description !== ""
                                        text: settingRow.modelData.description
                                        color: rowHover.hovered ? "#dec184" : theme.textMuted
                                        font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
                                        Behavior on color { ColorAnimation { duration: 120 } }
                                    }
                                }

                                Item {
                                    width: 100; height: parent.height

                                    // Bool → ToggleSwitch component
                                    ToggleSwitch {
                                        visible: settingRow.modelData.type === "bool"
                                        anchors.centerIn: parent
                                        checked: settingRow.modelData.value === true
                                        onToggled: (newValue) => settingsPanelViewModel.setSetting(
                                            pluginBlock.modelData.plugin,
                                            settingRow.modelData.key,
                                            newValue
                                        )
                                    }

                                    // Int / Float → stepper
                                    Row {
                                        visible: settingRow.modelData.type === "int"
                                               || settingRow.modelData.type === "float"
                                        anchors.centerIn: parent; spacing: 4

                                        property real _step: settingRow.modelData.step != null
                                            ? settingRow.modelData.step
                                            : (settingRow.modelData.type === "int" ? 1 : 0.1)
                                        property real _min: settingRow.modelData.min != null
                                            ? settingRow.modelData.min : -1e9
                                        property real _max: settingRow.modelData.max != null
                                            ? settingRow.modelData.max :  1e9

                                        function _clamp(v) {
                                            return Math.min(_max, Math.max(_min, v))
                                        }
                                        function _rounded(v) {
                                            // float precision: round to step's decimal places
                                            var decimals = (_step.toString().split(".")[1] || "").length
                                            return parseFloat(v.toFixed(decimals))
                                        }

                                        Text {
                                            anchors.verticalCenter: parent.verticalCenter
                                            text: "\u2212"   // −
                                            color: decHover.containsMouse ? theme.text : theme.textMuted
                                            font.pixelSize: theme.fontSizeBase; font.family: theme.fontFamily
                                            Behavior on color { ColorAnimation { duration: 80 } }
                                            MouseArea {
                                                id: decHover; anchors.fill: parent; hoverEnabled: true
                                                onClicked: {
                                                    var row = stepperRow
                                                    settingsPanelViewModel.setSetting(
                                                        pluginBlock.modelData.plugin,
                                                        settingRow.modelData.key,
                                                        row._rounded(row._clamp(settingRow.modelData.value - row._step))
                                                    )
                                                }
                                            }
                                        }

                                        Text {
                                            id: stepperRow
                                            anchors.verticalCenter: parent.verticalCenter
                                            text: settingRow.modelData.value
                                            color: theme.text
                                            font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
                                            width: 38; horizontalAlignment: Text.AlignHCenter
                                            // expose stepper helpers to siblings
                                            property real _step: parent._step
                                            property real _min:  parent._min
                                            property real _max:  parent._max
                                            function _clamp(v) { return parent._clamp(v) }
                                            function _rounded(v) { return parent._rounded(v) }
                                        }

                                        Text {
                                            anchors.verticalCenter: parent.verticalCenter
                                            text: "+"
                                            color: incHover.containsMouse ? theme.text : theme.textMuted
                                            font.pixelSize: theme.fontSizeBase; font.family: theme.fontFamily
                                            Behavior on color { ColorAnimation { duration: 80 } }
                                            MouseArea {
                                                id: incHover; anchors.fill: parent; hoverEnabled: true
                                                onClicked: {
                                                    var row = stepperRow
                                                    settingsPanelViewModel.setSetting(
                                                        pluginBlock.modelData.plugin,
                                                        settingRow.modelData.key,
                                                        row._rounded(row._clamp(settingRow.modelData.value + row._step))
                                                    )
                                                }
                                            }
                                        }
                                    }

                                    // Str → tekst input
                                    Rectangle {
                                        visible: settingRow.modelData.type === "str"
                                        anchors.centerIn: parent
                                        width: 90; height: 24; radius: 4
                                        color: theme.surfaceFloating
                                        border.width: 1
                                        border.color: strInput.activeFocus ? theme.accent : theme.border
                                        Behavior on border.color { ColorAnimation { duration: 80 } }

                                        TextInput {
                                            id: strInput
                                            anchors.fill: parent
                                            anchors.leftMargin: 6; anchors.rightMargin: 6
                                            anchors.verticalCenter: parent.verticalCenter
                                            verticalAlignment: TextInput.AlignVCenter
                                            text: settingRow.modelData.value
                                            color: theme.text
                                            font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
                                            selectByMouse: true
                                            onEditingFinished: settingsPanelViewModel.setSetting(
                                                pluginBlock.modelData.plugin,
                                                settingRow.modelData.key,
                                                text
                                            )
                                        }
                                    }

                                    // Color → kleur-swatch + hex input
                                    Row {
                                        visible: settingRow.modelData.type === "color"
                                        anchors.centerIn: parent; spacing: 6

                                        Rectangle {
                                            width: 20; height: 20; radius: 4
                                            anchors.verticalCenter: parent.verticalCenter
                                            color: settingRow.modelData.value
                                            border.width: 1; border.color: theme.border
                                        }

                                        Rectangle {
                                            width: 68; height: 24; radius: 4
                                            anchors.verticalCenter: parent.verticalCenter
                                            color: theme.surfaceFloating
                                            border.width: 1
                                            border.color: colorInput.activeFocus ? theme.accent : theme.border
                                            Behavior on border.color { ColorAnimation { duration: 80 } }

                                            TextInput {
                                                id: colorInput
                                                anchors.fill: parent
                                                anchors.leftMargin: 6; anchors.rightMargin: 6
                                                anchors.verticalCenter: parent.verticalCenter
                                                verticalAlignment: TextInput.AlignVCenter
                                                text: settingRow.modelData.value
                                                color: theme.text
                                                font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
                                                maximumLength: 7
                                                selectByMouse: true
                                                onEditingFinished: {
                                                    if (/^#[0-9A-Fa-f]{6}$/.test(text))
                                                        settingsPanelViewModel.setSetting(
                                                            pluginBlock.modelData.plugin,
                                                            settingRow.modelData.key,
                                                            text
                                                        )
                                                    else
                                                        text = settingRow.modelData.value
                                                }
                                            }
                                        }
                                    }

                                    // Enum → pijl-selector
                                    Row {
                                        visible: settingRow.modelData.type === "enum"
                                        anchors.centerIn: parent; spacing: 8

                                        Text {
                                            anchors.verticalCenter: parent.verticalCenter
                                            text: "\u2039"
                                            color: prevHover.containsMouse ? theme.text : theme.textMuted
                                            font.pixelSize: theme.fontSizeBase; font.family: theme.fontFamily
                                            Behavior on color { ColorAnimation { duration: 80 } }
                                            MouseArea {
                                                id: prevHover; anchors.fill: parent; hoverEnabled: true
                                                onClicked: {
                                                    var opts = settingRow.modelData.options
                                                    var idx  = opts.indexOf(settingRow.modelData.value)
                                                    settingsPanelViewModel.setSetting(
                                                        pluginBlock.modelData.plugin,
                                                        settingRow.modelData.key,
                                                        opts[(idx - 1 + opts.length) % opts.length]
                                                    )
                                                }
                                            }
                                        }

                                        Text {
                                            anchors.verticalCenter: parent.verticalCenter
                                            text: settingRow.modelData.value
                                            color: theme.text
                                            font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
                                            width: 42; horizontalAlignment: Text.AlignHCenter
                                        }

                                        Text {
                                            anchors.verticalCenter: parent.verticalCenter
                                            text: "\u203A"
                                            color: nextHover.containsMouse ? theme.text : theme.textMuted
                                            font.pixelSize: theme.fontSizeBase; font.family: theme.fontFamily
                                            Behavior on color { ColorAnimation { duration: 80 } }
                                            MouseArea {
                                                id: nextHover; anchors.fill: parent; hoverEnabled: true
                                                onClicked: {
                                                    var opts = settingRow.modelData.options
                                                    var idx  = opts.indexOf(settingRow.modelData.value)
                                                    settingsPanelViewModel.setSetting(
                                                        pluginBlock.modelData.plugin,
                                                        settingRow.modelData.key,
                                                        opts[(idx + 1) % opts.length]
                                                    )
                                                }
                                            }
                                        }
                                    }
                                }
                            }

                            HoverHandler { id: rowHover }
                        }
                    }
                }
            }
        }
    }
}
