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
import QtQuick.Layouts
import TinyUI
import "components"

BaseDialog {
    id: settingsDialog

    dialogTitle: "Settings"
    width: 720; height: 520
    minimumWidth: 540; minimumHeight: 380
    visible: SettingsPanelViewModel.open
    onCloseRequested: SettingsPanelViewModel.closePanel()

    // ── Pending changes — managed locally in QML ──────────────────────────────
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
        // Object.assign creates new references — without this QML won't detect the change
        // and bindings on pendingChanges won't update.
        var p = Object.assign({}, pendingChanges)
        p[plugin] = Object.assign({}, p[plugin] || {})
        p[plugin][key] = value
        pendingChanges = p
    }

    function _settingType(plugin, key) {
        for (var i = 0; i < CoreViewModel.settingsByPlugin.length; ++i) {
            var pluginGroup = CoreViewModel.settingsByPlugin[i]
            if (pluginGroup.plugin !== plugin)
                continue
            for (var j = 0; j < pluginGroup.sections.length; ++j) {
                var section = pluginGroup.sections[j]
                for (var k = 0; k < section.settings.length; ++k) {
                    var setting = section.settings[k]
                    if (setting.key === key)
                        return setting.type
                }
            }
        }
        return ""
    }

    function _savePendingSetting(plugin, key, value) {
        var type = _settingType(plugin, key)
        if (type === "bool")
            CoreViewModel.setBoolSettingValue(plugin, key, value === true)
        else if (type === "int")
            CoreViewModel.setIntSettingValue(plugin, key, Math.round(value))
        else if (type === "float")
            CoreViewModel.setFloatSettingValue(plugin, key, Number(value))
        else
            CoreViewModel.setStringSettingValue(plugin, key, String(value))
    }

    function _applyAndSave() {
        for (var plugin in pendingChanges) {
            var changes = pendingChanges[plugin]
            for (var key in changes)
                _savePendingSetting(plugin, key, changes[key])
        }
        pendingChanges = ({})
    }

    property int activeTab: 0

    onVisibleChanged: {
        if (!visible) {
            pendingChanges = ({})
            activeTab = 0
        }
    }

    // ── Content (via BaseDialog default alias → contentArea) ──────────────────

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // ── Main area: tabs left, settings right ─────────────────────────────
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 0

            // Vertical tab list
            Rectangle {
                Layout.preferredWidth: 160
                Layout.fillHeight: true
                color: Theme.surfaceAlt

                ListView {
                    id: tabList
                    anchors.fill: parent
                    model: CoreViewModel.settingsByPlugin
                    property var dialog: settingsDialog

                    delegate: Rectangle {
                        id: tabItem
                        required property var modelData
                        required property int index

                        width: ListView.view.width; height: 40
                        color: ListView.view.dialog.activeTab === tabItem.index
                            ? Theme.surface : (tabHov.containsMouse ? Theme.surfaceRaised : "transparent")
                        Behavior on color { ColorAnimation { duration: 80 } }

                        Rectangle {
                            width: 2; height: parent.height
                            color: Theme.accent
                            visible: ListView.view.dialog.activeTab === tabItem.index
                        }

                        Text {
                            anchors.left: parent.left; anchors.leftMargin: 16
                            anchors.verticalCenter: parent.verticalCenter
                            text: tabItem.modelData.plugin
                            color: ListView.view.dialog.activeTab === tabItem.index ? Theme.text : Theme.textMuted
                            font.pixelSize: Theme.fontSizeBase; font.family: Theme.fontFamily
                            font.weight: ListView.view.dialog.activeTab === tabItem.index ? Font.DemiBold : Font.Normal
                            Behavior on color { ColorAnimation { duration: 80 } }
                        }

                        Text {
                            anchors.right: parent.right; anchors.rightMargin: 12
                            anchors.verticalCenter: parent.verticalCenter
                            text: "●"; font.pixelSize: 6; font.family: Theme.fontFamily
                            color: Theme.accent
                            visible: {
                                var pc = ListView.view.dialog.pendingChanges[tabItem.modelData.plugin]
                                return pc ? Object.keys(pc).length > 0 : false
                            }
                        }

                        MouseArea { id: tabHov; anchors.fill: parent; hoverEnabled: true
                            onClicked: ListView.view.dialog.activeTab = tabItem.index }
                    }
                }

                Rectangle { anchors.right: parent.right; width: 1; height: parent.height; color: Theme.border }
            }

            // ── Content: sections + setting rows ─────────────────────────────
            ListView {
                id: contentList
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                property var dialog: settingsDialog
                model: CoreViewModel.settingsByPlugin.length > settingsDialog.activeTab
                    ? CoreViewModel.settingsByPlugin[settingsDialog.activeTab].sections : []

                delegate: Column {
                    id: sectionBlock
                    required property var modelData   // { name, settings[] }
                    readonly property var _dialog: ListView.view.dialog
                    width: ListView.view.width

                    Rectangle {
                        width: parent.width
                        height: sectionBlock.modelData.name !== "" ? 28 : 0
                        visible: height > 0
                        color: Theme.surfaceAlt

                        Text {
                            anchors.left: parent.left; anchors.leftMargin: 16
                            anchors.verticalCenter: parent.verticalCenter
                            text: sectionBlock.modelData.name
                            color: Theme.textSecondary
                            font.pixelSize: Theme.fontSizeSmall; font.family: Theme.fontFamily
                            font.weight: Font.Medium
                        }
                        Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: Theme.border }
                    }

                    Repeater {
                        model: sectionBlock.modelData.settings

                        Rectangle {
                            id: settingRow
                            required property var modelData

                            // parent is sectionBlock (Column), expose dialog as own property
                            // so nested child items can reach it via settingRow._dlg
                            readonly property var _dlg: parent._dialog

                            readonly property string _plugin: CoreViewModel.settingsByPlugin.length > settingRow._dlg.activeTab
                                ? CoreViewModel.settingsByPlugin[settingRow._dlg.activeTab].plugin : ""

                            property var effectiveValue: settingRow._dlg._effectiveValue(
                                settingRow._plugin, settingRow.modelData.key, settingRow.modelData.value)

                            readonly property bool isPending: {
                                var pc = settingRow._dlg.pendingChanges[settingRow._plugin]
                                return pc !== undefined && pc[settingRow.modelData.key] !== undefined
                            }

                            width: parent.width; height: 44
                            color: "transparent"

                            // Hover gradient — same pattern as WidgetTab
                            Rectangle {
                                anchors.fill: parent
                                opacity: rowHov.hovered ? 1 : 0
                                Behavior on opacity { NumberAnimation { duration: 120 } }
                                gradient: Gradient {
                                    orientation: Gradient.Horizontal
                                    GradientStop { position: 0.0; color: "transparent" }
                                    GradientStop { position: 0.5; color: "transparent" }
                                    GradientStop { position: 1.0; color: "#20dec184" }
                                }
                            }

                            Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: Theme.border; opacity: 0.4 }

                            Row {
                                anchors.fill: parent; leftPadding: 16

                                // Label + description
                                Column {
                                    width: parent.width - 16 - 128
                                    anchors.verticalCenter: parent.verticalCenter
                                    spacing: 3

                                    Row {
                                        spacing: 6
                                        Text {
                                            text: settingRow.modelData.label
                                            color: settingRow.isPending ? Theme.accent : Theme.text
                                            font.pixelSize: Theme.fontSizeBase; font.family: Theme.fontFamily
                                            Behavior on color { ColorAnimation { duration: 120 } }
                                        }
                                        Text {
                                            visible: settingRow.isPending
                                            text: "●"; font.pixelSize: 6; font.family: Theme.fontFamily
                                            color: Theme.accent
                                            anchors.bottom: parent.bottom; anchors.bottomMargin: 3
                                        }
                                    }
                                    Text {
                                        visible: settingRow.modelData.description !== ""
                                        text: settingRow.modelData.description
                                        color: rowHov.hovered ? "#dec184" : Theme.textMuted
                                        font.pixelSize: Theme.fontSizeSmall; font.family: Theme.fontFamily
                                        Behavior on color { ColorAnimation { duration: 120 } }
                                    }
                                }

                                // ── Controls (128px) ──────────────────────────────────────────
                                Item {
                                    width: 128; height: parent.height

                                    // Bool → ToggleSwitch
                                    ToggleSwitch {
                                        visible: settingRow.modelData.type === "bool"
                                        anchors.right: parent.right; anchors.rightMargin: 12
                                        anchors.verticalCenter: parent.verticalCenter
                                        checked: settingRow.effectiveValue === true
                                        onToggled: (v) => settingRow._dlg._setPending(
                                            settingRow._plugin, settingRow.modelData.key, v)
                                    }

                                    // Enum → ThemedComboBox
                                    ThemedComboBox {
                                        visible: settingRow.modelData.type === "enum"
                                        anchors.right: parent.right; anchors.rightMargin: 12
                                        anchors.verticalCenter: parent.verticalCenter
                                        model: settingRow.modelData.options
                                        currentIndex: {
                                            var idx = settingRow.modelData.options.indexOf(settingRow.effectiveValue)
                                            return idx >= 0 ? idx : 0
                                        }
                                        onActivated: (idx) => settingRow._dlg._setPending(
                                            settingRow._plugin, settingRow.modelData.key,
                                            settingRow.modelData.options[idx])
                                    }

                                    // Int / Float → NumberStepper
                                    NumberStepper {
                                        visible: settingRow.modelData.type === "int"
                                               || settingRow.modelData.type === "float"
                                        anchors.right: parent.right; anchors.rightMargin: 12
                                        anchors.verticalCenter: parent.verticalCenter
                                        value: settingRow.effectiveValue
                                        step: settingRow.modelData.step != null
                                            ? settingRow.modelData.step
                                            : (settingRow.modelData.type === "int" ? 1 : 0.1)
                                        min: settingRow.modelData.min != null ? settingRow.modelData.min : -1e9
                                        max: settingRow.modelData.max != null ? settingRow.modelData.max :  1e9
                                        onCommit: (v) => settingRow._dlg._setPending(
                                            settingRow._plugin, settingRow.modelData.key, v)
                                    }

                                    // Str → text input
                                    Rectangle {
                                        visible: settingRow.modelData.type === "str"
                                        anchors.right: parent.right; anchors.rightMargin: 12
                                        anchors.verticalCenter: parent.verticalCenter
                                        width: 120; height: 28; radius: 4
                                        color: Theme.surfaceFloating
                                        border.width: 1
                                        border.color: strInput.activeFocus ? Theme.accent : Theme.border
                                        Behavior on border.color { ColorAnimation { duration: 80 } }

                                        TextInput {
                                            id: strInput
                                            anchors.fill: parent; anchors.leftMargin: 8; anchors.rightMargin: 8
                                            verticalAlignment: TextInput.AlignVCenter
                                            text: settingRow.effectiveValue
                                            color: Theme.text
                                            font.pixelSize: Theme.fontSizeSmall; font.family: Theme.fontFamily
                                            selectByMouse: true
                                            Keys.onReturnPressed: settingRow._dlg._setPending(
                                                settingRow._plugin, settingRow.modelData.key, text)
                                            Keys.onEscapePressed: { text = settingRow.effectiveValue; focus = false }
                                            onActiveFocusChanged: if (!activeFocus) text = settingRow.effectiveValue
                                        }
                                    }

                                    // Color → color picker
                                    ColorPicker {
                                        visible: settingRow.modelData.type === "color"
                                        anchors.right: parent.right; anchors.rightMargin: 12
                                        anchors.verticalCenter: parent.verticalCenter
                                        value: settingRow.effectiveValue
                                        onColorPicked: (hex) => settingRow._dlg._setPending(
                                            settingRow._plugin, settingRow.modelData.key, hex)
                                    }
                                }
                            }

                            HoverHandler { id: rowHov }
                        }
                    }
                }
            }
        }

        // ── Footer: Revert / Save / Close ─────────────────────────────────────
        DialogFooter {
            Layout.fillWidth: true
            showRevert: true
            showSave:   true
            revertEnabled: settingsDialog.hasPendingChanges
            saveEnabled:   settingsDialog.hasPendingChanges
            onRevertClicked: settingsDialog.pendingChanges = ({})
            onSaveClicked:   settingsDialog._applyAndSave()
            onCloseClicked:  SettingsPanelViewModel.closePanel()
        }
    }
}
