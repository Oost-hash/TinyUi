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
import QtQuick.Layouts
import "components"

Window {
    id: settingsDialog

    title: "Settings"
    width: 720; height: 520
    minimumWidth: 540; minimumHeight: 380
    visible: settingsPanelViewModel.open
    color: theme.surface

    readonly property bool nativeChrome: Qt.platform.os === "linux" || Qt.platform.os === "osx"
    flags: nativeChrome ? Qt.Dialog : Qt.Dialog | Qt.FramelessWindowHint

    // ── Pending changes — lokaal beheerd in QML ───────────────────────────────
    // { pluginName: { key: newValue } }
    property var pendingChanges: ({})

    readonly property bool hasPendingChanges: {
        for (var p in pendingChanges)
            if (Object.keys(pendingChanges[p] || {}).length > 0) return true
        return false
    }

    function _effectiveValue(plugin, key, current) {
        var pc = pendingChanges[plugin]
        return (pc && pc[key] !== undefined) ? pc[key] : current
    }

    function _setPending(plugin, key, value) {
        var p = pendingChanges
        if (!p[plugin]) p[plugin] = {}
        p[plugin][key] = value
        pendingChanges = p
    }

    function _applyAndSave() {
        for (var plugin in pendingChanges) {
            var changes = pendingChanges[plugin]
            for (var key in changes)
                coreViewModel.setSettingValue(plugin, key, changes[key])
        }
        pendingChanges = ({})
    }

    // Actieve plugin-tab (index in coreViewModel.settingsByPlugin)
    property int activeTab: 0

    // Reset state wanneer dialog sluit
    onVisibleChanged: {
        if (!visible) {
            pendingChanges = ({})
            activeTab = 0
        }
    }

    // ── Layout ────────────────────────────────────────────────────────────────

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // Titlebar — alleen op Windows (CSD)
        Rectangle {
            id: dialogTitleBar
            visible: !settingsDialog.nativeChrome
            Layout.fillWidth: true
            height: visible ? 36 : 0
            color: theme.surfaceAlt

            DragHandler {
                onActiveChanged: if (active) settingsDialog.startSystemMove()
            }

            Text {
                anchors.left: parent.left; anchors.leftMargin: 16
                anchors.verticalCenter: parent.verticalCenter
                text: "Settings"
                color: theme.text
                font.pixelSize: theme.fontSizeBase; font.family: theme.fontFamily
                font.weight: Font.DemiBold
            }

            Item {
                anchors.right: parent.right
                width: 40; height: parent.height
                Text {
                    anchors.centerIn: parent
                    text: icons.close; font.family: theme.iconFont; font.pixelSize: 10
                    color: tbCloseHov.containsMouse ? theme.text : theme.textMuted
                    Behavior on color { ColorAnimation { duration: 80 } }
                }
                MouseArea { id: tbCloseHov; anchors.fill: parent; hoverEnabled: true
                    onClicked: settingsPanelViewModel.closePanel() }
            }

            Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: theme.border }
        }

        // Hoofdgebied: tabs links, content rechts
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 0

            // ── Verticale tab lijst ───────────────────────────────────────
            Rectangle {
                Layout.preferredWidth: 160
                Layout.fillHeight: true
                color: theme.surfaceAlt

                ListView {
                    id: tabList
                    anchors.fill: parent
                    model: coreViewModel.settingsByPlugin

                    delegate: Rectangle {
                        id: tabItem
                        required property var modelData
                        required property int index

                        width: tabList.width; height: 40
                        color: settingsDialog.activeTab === tabItem.index
                            ? theme.surface : (tabHov.containsMouse ? "#ffffff08" : "transparent")
                        Behavior on color { ColorAnimation { duration: 80 } }

                        // Accent links voor actieve tab
                        Rectangle {
                            width: 2; height: parent.height
                            color: theme.accent
                            visible: settingsDialog.activeTab === tabItem.index
                        }

                        Text {
                            anchors.left: parent.left; anchors.leftMargin: 16
                            anchors.verticalCenter: parent.verticalCenter
                            text: tabItem.modelData.plugin
                            color: settingsDialog.activeTab === tabItem.index ? theme.text : theme.textMuted
                            font.pixelSize: theme.fontSizeBase; font.family: theme.fontFamily
                            font.weight: settingsDialog.activeTab === tabItem.index ? Font.DemiBold : Font.Normal
                            Behavior on color { ColorAnimation { duration: 80 } }
                        }

                        // Pending indicator (● rechts)
                        Text {
                            anchors.right: parent.right; anchors.rightMargin: 12
                            anchors.verticalCenter: parent.verticalCenter
                            text: "●"; font.pixelSize: 6; font.family: theme.fontFamily
                            color: theme.accent
                            visible: {
                                var pc = settingsDialog.pendingChanges[tabItem.modelData.plugin]
                                return pc && Object.keys(pc).length > 0
                            }
                        }

                        MouseArea { id: tabHov; anchors.fill: parent; hoverEnabled: true
                            onClicked: settingsDialog.activeTab = tabItem.index }
                    }
                }

                // Rechter border
                Rectangle { anchors.right: parent.right; width: 1; height: parent.height; color: theme.border }
            }

            // ── Content: secties + setting rijen ─────────────────────────
            ListView {
                id: contentList
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                model: coreViewModel.settingsByPlugin.length > settingsDialog.activeTab
                    ? coreViewModel.settingsByPlugin[settingsDialog.activeTab].sections : []

                delegate: Column {
                    id: sectionBlock
                    required property var modelData   // { name, settings[] }
                    width: contentList.width

                    // Sectie header
                    Rectangle {
                        width: parent.width
                        height: sectionBlock.modelData.name !== "" ? 28 : 0
                        visible: height > 0
                        color: theme.surfaceAlt

                        Text {
                            anchors.left: parent.left; anchors.leftMargin: 16
                            anchors.verticalCenter: parent.verticalCenter
                            text: sectionBlock.modelData.name
                            color: theme.textSecondary
                            font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
                            font.weight: Font.Medium
                        }
                        Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: theme.border }
                    }

                    // Setting rijen
                    Repeater {
                        model: sectionBlock.modelData.settings

                        Rectangle {
                            id: settingRow
                            required property var modelData   // {key,label,type,value,description,options,min,max,step}

                            // Actieve plugin naam — eenmalig berekend per rij
                            readonly property string _plugin: coreViewModel.settingsByPlugin.length > settingsDialog.activeTab
                                ? coreViewModel.settingsByPlugin[settingsDialog.activeTab].plugin : ""

                            property var effectiveValue: settingsDialog._effectiveValue(
                                _plugin, modelData.key, modelData.value)

                            readonly property bool isPending: {
                                var pc = settingsDialog.pendingChanges[_plugin]
                                return pc !== undefined && pc[modelData.key] !== undefined
                            }

                            width: contentList.width; height: 44
                            color: rowHov.hovered ? "#dec1841a" : "transparent"
                            Behavior on color { ColorAnimation { duration: 80 } }

                            Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: theme.border; opacity: 0.4 }

                            Row {
                                anchors.fill: parent; leftPadding: 16

                                // Label + omschrijving
                                Column {
                                    width: parent.width - 16 - 120
                                    anchors.verticalCenter: parent.verticalCenter
                                    spacing: 3

                                    Row {
                                        spacing: 6
                                        Text {
                                            text: settingRow.modelData.label
                                            color: settingRow.isPending ? theme.accent : theme.text
                                            font.pixelSize: theme.fontSizeBase; font.family: theme.fontFamily
                                            Behavior on color { ColorAnimation { duration: 120 } }
                                        }
                                        Text {
                                            visible: settingRow.isPending
                                            text: "●"; font.pixelSize: 6; font.family: theme.fontFamily
                                            color: theme.accent
                                            anchors.bottom: parent.bottom; anchors.bottomMargin: 3
                                        }
                                    }
                                    Text {
                                        visible: settingRow.modelData.description !== ""
                                        text: settingRow.modelData.description
                                        color: rowHov.hovered ? "#dec184" : theme.textMuted
                                        font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
                                        Behavior on color { ColorAnimation { duration: 120 } }
                                    }
                                }

                                // Controls (120px breed)
                                Item {
                                    width: 120; height: parent.height

                                    // Bool → toggle
                                    ToggleSwitch {
                                        visible: settingRow.modelData.type === "bool"
                                        anchors.centerIn: parent
                                        checked: settingRow.effectiveValue === true
                                        onToggled: (v) => settingsDialog._setPending(settingRow._plugin, settingRow.modelData.key, v)
                                    }

                                    // Enum → pijl-selector
                                    Row {
                                        id: enumRow
                                        visible: settingRow.modelData.type === "enum"
                                        anchors.centerIn: parent; spacing: 8

                                        Text {
                                            anchors.verticalCenter: parent.verticalCenter; text: "\u2039"
                                            color: enumPrev.containsMouse ? theme.text : theme.textMuted
                                            font.pixelSize: theme.fontSizeBase; font.family: theme.fontFamily
                                            Behavior on color { ColorAnimation { duration: 80 } }
                                            MouseArea {
                                                id: enumPrev; anchors.fill: parent; hoverEnabled: true
                                                onClicked: {
                                                    var opts = settingRow.modelData.options
                                                    var idx = opts.indexOf(settingRow.effectiveValue)
                                                    settingsDialog._setPending(settingRow._plugin, settingRow.modelData.key,
                                                        opts[(idx - 1 + opts.length) % opts.length])
                                                }
                                            }
                                        }
                                        Text {
                                            anchors.verticalCenter: parent.verticalCenter
                                            text: settingRow.effectiveValue
                                            color: theme.text; font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
                                            width: 48; horizontalAlignment: Text.AlignHCenter
                                        }
                                        Text {
                                            anchors.verticalCenter: parent.verticalCenter; text: "\u203A"
                                            color: enumNext.containsMouse ? theme.text : theme.textMuted
                                            font.pixelSize: theme.fontSizeBase; font.family: theme.fontFamily
                                            Behavior on color { ColorAnimation { duration: 80 } }
                                            MouseArea {
                                                id: enumNext; anchors.fill: parent; hoverEnabled: true
                                                onClicked: {
                                                    var opts = settingRow.modelData.options
                                                    var idx = opts.indexOf(settingRow.effectiveValue)
                                                    settingsDialog._setPending(settingRow._plugin, settingRow.modelData.key,
                                                        opts[(idx + 1) % opts.length])
                                                }
                                            }
                                        }
                                    }

                                    // Int / Float → stepper
                                    Row {
                                        id: stepperRow
                                        visible: settingRow.modelData.type === "int" || settingRow.modelData.type === "float"
                                        anchors.centerIn: parent; spacing: 4

                                        property real _step: settingRow.modelData.step != null
                                            ? settingRow.modelData.step
                                            : (settingRow.modelData.type === "int" ? 1 : 0.1)
                                        property real _min:  settingRow.modelData.min  != null ? settingRow.modelData.min  : -1e9
                                        property real _max:  settingRow.modelData.max  != null ? settingRow.modelData.max  :  1e9

                                        function _clamp(v) { return Math.min(_max, Math.max(_min, v)) }
                                        function _round(v) {
                                            var dec = (_step.toString().split(".")[1] || "").length
                                            return parseFloat(v.toFixed(dec))
                                        }

                                        Text {
                                            anchors.verticalCenter: parent.verticalCenter; text: "\u2212"
                                            color: stepDec.containsMouse ? theme.text : theme.textMuted
                                            font.pixelSize: theme.fontSizeBase; font.family: theme.fontFamily
                                            Behavior on color { ColorAnimation { duration: 80 } }
                                            MouseArea {
                                                id: stepDec; anchors.fill: parent; hoverEnabled: true
                                                onClicked: settingsDialog._setPending(settingRow._plugin, settingRow.modelData.key,
                                                    stepperRow._round(stepperRow._clamp(settingRow.effectiveValue - stepperRow._step)))
                                            }
                                        }
                                        Text {
                                            anchors.verticalCenter: parent.verticalCenter
                                            text: settingRow.effectiveValue
                                            color: theme.text; font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
                                            width: 38; horizontalAlignment: Text.AlignHCenter
                                        }
                                        Text {
                                            anchors.verticalCenter: parent.verticalCenter; text: "+"
                                            color: stepInc.containsMouse ? theme.text : theme.textMuted
                                            font.pixelSize: theme.fontSizeBase; font.family: theme.fontFamily
                                            Behavior on color { ColorAnimation { duration: 80 } }
                                            MouseArea {
                                                id: stepInc; anchors.fill: parent; hoverEnabled: true
                                                onClicked: settingsDialog._setPending(settingRow._plugin, settingRow.modelData.key,
                                                    stepperRow._round(stepperRow._clamp(settingRow.effectiveValue + stepperRow._step)))
                                            }
                                        }
                                    }

                                    // Str → tekst input
                                    Rectangle {
                                        visible: settingRow.modelData.type === "str"
                                        anchors.centerIn: parent
                                        width: 100; height: 24; radius: 4
                                        color: theme.surfaceFloating
                                        border.width: 1
                                        border.color: strInput.activeFocus ? theme.accent : theme.border
                                        Behavior on border.color { ColorAnimation { duration: 80 } }
                                        TextInput {
                                            id: strInput
                                            anchors.fill: parent; anchors.leftMargin: 6; anchors.rightMargin: 6
                                            verticalAlignment: TextInput.AlignVCenter
                                            text: settingRow.effectiveValue
                                            color: theme.text; font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
                                            selectByMouse: true
                                            onEditingFinished: settingsDialog._setPending(settingRow._plugin, settingRow.modelData.key, text)
                                        }
                                    }

                                    // Color → swatch + hex input
                                    Row {
                                        visible: settingRow.modelData.type === "color"
                                        anchors.centerIn: parent; spacing: 6

                                        Rectangle {
                                            width: 20; height: 20; radius: 4
                                            anchors.verticalCenter: parent.verticalCenter
                                            color: settingRow.effectiveValue
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
                                                anchors.fill: parent; anchors.leftMargin: 6; anchors.rightMargin: 6
                                                verticalAlignment: TextInput.AlignVCenter
                                                text: settingRow.effectiveValue
                                                color: theme.text; font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
                                                maximumLength: 7; selectByMouse: true
                                                onEditingFinished: {
                                                    if (/^#[0-9A-Fa-f]{6}$/.test(text))
                                                        settingsDialog._setPending(settingRow._plugin, settingRow.modelData.key, text)
                                                    else
                                                        text = settingRow.effectiveValue
                                                }
                                            }
                                        }
                                    }
                                }
                            }

                            HoverHandler { id: rowHov }
                        }
                    }
                }
            }
        }

        // ── Bottom bar: Revert / Save / Close ────────────────────────────────
        Rectangle {
            Layout.fillWidth: true
            height: 48
            color: theme.surfaceAlt

            Rectangle { width: parent.width; height: 1; color: theme.border }

            Row {
                anchors.right: parent.right; anchors.rightMargin: 16
                anchors.verticalCenter: parent.verticalCenter
                spacing: 8
                topPadding: 1  // border compensatie

                // Revert
                Rectangle {
                    width: 80; height: 32; radius: 5
                    color: revertHov.containsMouse ? theme.surfaceFloating : theme.surfaceRaised
                    opacity: settingsDialog.hasPendingChanges ? 1 : 0.4
                    Behavior on color       { ColorAnimation { duration: 80 } }
                    Behavior on opacity     { NumberAnimation { duration: 120 } }
                    Text {
                        anchors.centerIn: parent; text: "Revert"
                        color: theme.text; font.pixelSize: theme.fontSizeBase; font.family: theme.fontFamily
                    }
                    MouseArea { id: revertHov; anchors.fill: parent; hoverEnabled: true
                        onClicked: if (settingsDialog.hasPendingChanges) settingsDialog.pendingChanges = ({}) }
                }

                // Save
                Rectangle {
                    width: 80; height: 32; radius: 5
                    color: saveHov.containsMouse ? theme.accentHover : theme.accent
                    opacity: settingsDialog.hasPendingChanges ? 1 : 0.4
                    Behavior on color       { ColorAnimation { duration: 80 } }
                    Behavior on opacity     { NumberAnimation { duration: 120 } }
                    Text {
                        anchors.centerIn: parent; text: "Save"
                        color: theme.accentText; font.pixelSize: theme.fontSizeBase; font.family: theme.fontFamily
                        font.weight: Font.Medium
                    }
                    MouseArea { id: saveHov; anchors.fill: parent; hoverEnabled: true
                        onClicked: if (settingsDialog.hasPendingChanges) settingsDialog._applyAndSave() }
                }

                // Close
                Rectangle {
                    width: 80; height: 32; radius: 5
                    color: closeHov.containsMouse ? theme.surfaceFloating : theme.surfaceRaised
                    Behavior on color { ColorAnimation { duration: 80 } }
                    Text {
                        anchors.centerIn: parent; text: "Close"
                        color: theme.text; font.pixelSize: theme.fontSizeBase; font.family: theme.fontFamily
                    }
                    MouseArea { id: closeHov; anchors.fill: parent; hoverEnabled: true
                        onClicked: settingsPanelViewModel.closePanel() }
                }
            }
        }
    }
}
