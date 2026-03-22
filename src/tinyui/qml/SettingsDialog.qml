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
import QtQuick.Controls
import "components"

BaseDialog {
    id: settingsDialog

    dialogTitle: "Settings"
    width: 720; height: 520
    minimumWidth: 540; minimumHeight: 380
    visible: settingsPanelViewModel.open
    onCloseRequested: settingsPanelViewModel.closePanel()

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
        // Object.assign maakt nieuwe referenties — anders detecteert QML geen wijziging
        // en updaten bindings die afhangen van pendingChanges niet.
        var p = Object.assign({}, pendingChanges)
        p[plugin] = Object.assign({}, p[plugin] || {})
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

        // ── Hoofdgebied: tabs links, instellingen rechts ──────────────────────
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 0

            // Verticale tab lijst
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
                            ? theme.surface : (tabHov.containsMouse ? theme.surfaceRaised : "transparent")
                        Behavior on color { ColorAnimation { duration: 80 } }

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

                        Text {
                            anchors.right: parent.right; anchors.rightMargin: 12
                            anchors.verticalCenter: parent.verticalCenter
                            text: "●"; font.pixelSize: 6; font.family: theme.fontFamily
                            color: theme.accent
                            visible: {
                                var pc = settingsDialog.pendingChanges[tabItem.modelData.plugin]
                                return pc ? Object.keys(pc).length > 0 : false
                            }
                        }

                        MouseArea { id: tabHov; anchors.fill: parent; hoverEnabled: true
                            onClicked: settingsDialog.activeTab = tabItem.index }
                    }
                }

                Rectangle { anchors.right: parent.right; width: 1; height: parent.height; color: theme.border }
            }

            // ── Content: secties + setting rijen ─────────────────────────────
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

                    Repeater {
                        model: sectionBlock.modelData.settings

                        Rectangle {
                            id: settingRow
                            required property var modelData

                            readonly property string _plugin: coreViewModel.settingsByPlugin.length > settingsDialog.activeTab
                                ? coreViewModel.settingsByPlugin[settingsDialog.activeTab].plugin : ""

                            property var effectiveValue: settingsDialog._effectiveValue(
                                _plugin, modelData.key, modelData.value)

                            readonly property bool isPending: {
                                var pc = settingsDialog.pendingChanges[_plugin]
                                return pc !== undefined && pc[modelData.key] !== undefined
                            }

                            width: contentList.width; height: 44
                            color: "transparent"

                            // Hover gradient — zelfde patroon als WidgetTab
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

                            Rectangle { anchors.bottom: parent.bottom; width: parent.width; height: 1; color: theme.border; opacity: 0.4 }

                            Row {
                                anchors.fill: parent; leftPadding: 16

                                // Label + omschrijving
                                Column {
                                    width: parent.width - 16 - 128
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

                                // ── Controls (128px) ──────────────────────────────────────────
                                Item {
                                    width: 128; height: parent.height

                                    // Bool → ToggleSwitch
                                    ToggleSwitch {
                                        visible: settingRow.modelData.type === "bool"
                                        anchors.right: parent.right; anchors.rightMargin: 12
                                        anchors.verticalCenter: parent.verticalCenter
                                        checked: settingRow.effectiveValue === true
                                        onToggled: (v) => settingsDialog._setPending(
                                            settingRow._plugin, settingRow.modelData.key, v)
                                    }

                                    // Enum → ComboBox popup
                                    ComboBox {
                                        id: enumCombo
                                        visible: settingRow.modelData.type === "enum"
                                        anchors.right: parent.right; anchors.rightMargin: 12
                                        anchors.verticalCenter: parent.verticalCenter
                                        width: 120; height: 28
                                        model: settingRow.modelData.options
                                        currentIndex: {
                                            var idx = settingRow.modelData.options.indexOf(settingRow.effectiveValue)
                                            return idx >= 0 ? idx : 0
                                        }
                                        onActivated: (idx) => settingsDialog._setPending(
                                            settingRow._plugin, settingRow.modelData.key,
                                            settingRow.modelData.options[idx])

                                        contentItem: Text {
                                            leftPadding: 8
                                            rightPadding: enumCombo.indicator.width + 4
                                            text: enumCombo.displayText
                                            color: theme.text
                                            font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
                                            verticalAlignment: Text.AlignVCenter
                                            elide: Text.ElideRight
                                        }

                                        indicator: Text {
                                            x: enumCombo.width - width - 8
                                            anchors.verticalCenter: enumCombo.verticalCenter
                                            text: "▾"
                                            color: theme.textMuted
                                            font.pixelSize: 10
                                        }

                                        background: Rectangle {
                                            color: theme.surfaceFloating
                                            border.width: 1
                                            border.color: enumCombo.popup.opened ? theme.accent : theme.border
                                            radius: 4
                                            Behavior on border.color { ColorAnimation { duration: 80 } }
                                        }

                                        popup: Popup {
                                            y: enumCombo.height + 2
                                            width: enumCombo.width
                                            padding: 0

                                            contentItem: ListView {
                                                clip: true
                                                implicitHeight: Math.min(contentHeight, 200)
                                                model: enumCombo.delegateModel
                                                currentIndex: enumCombo.highlightedIndex
                                            }

                                            background: Rectangle {
                                                color: theme.surfaceFloating
                                                border.width: 1; border.color: theme.border
                                                radius: 4
                                            }
                                        }

                                        delegate: ItemDelegate {
                                            width: enumCombo.popup.width
                                            height: 32
                                            highlighted: enumCombo.highlightedIndex === index

                                            contentItem: Text {
                                                text: modelData
                                                color: highlighted ? "#dec184" : theme.text
                                                font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
                                                verticalAlignment: Text.AlignVCenter
                                                leftPadding: 8
                                                Behavior on color { ColorAnimation { duration: 80 } }
                                            }

                                            background: Rectangle {
                                                color: highlighted ? theme.surfaceRaised : "transparent"
                                            }
                                        }
                                    }

                                    // Int / Float → stepper met inline edit op klik
                                    Row {
                                        id: stepperRow
                                        visible: settingRow.modelData.type === "int"
                                               || settingRow.modelData.type === "float"
                                        anchors.right: parent.right; anchors.rightMargin: 12
                                        anchors.verticalCenter: parent.verticalCenter
                                        spacing: 6

                                        property bool _editing: false
                                        property real _step: settingRow.modelData.step != null
                                            ? settingRow.modelData.step
                                            : (settingRow.modelData.type === "int" ? 1 : 0.1)
                                        property real _min: settingRow.modelData.min != null ? settingRow.modelData.min : -1e9
                                        property real _max: settingRow.modelData.max != null ? settingRow.modelData.max :  1e9

                                        function _clamp(v) { return Math.min(_max, Math.max(_min, v)) }
                                        function _round(v) {
                                            var dec = (_step.toString().split(".")[1] || "").length
                                            return parseFloat(v.toFixed(dec))
                                        }
                                        function _commit(text) {
                                            var val = settingRow.modelData.type === "int"
                                                ? parseInt(text) : parseFloat(text)
                                            if (!isNaN(val))
                                                settingsDialog._setPending(settingRow._plugin, settingRow.modelData.key,
                                                    _round(_clamp(val)))
                                            _editing = false
                                        }

                                        // − knop
                                        Item {
                                            width: 24; height: 26
                                            anchors.verticalCenter: parent.verticalCenter
                                            Text {
                                                anchors.centerIn: parent
                                                text: "\u2212"
                                                color: decArea.containsMouse ? theme.text : theme.textMuted
                                                font.pixelSize: theme.fontSizeBase; font.family: theme.fontFamily
                                                Behavior on color { ColorAnimation { duration: 80 } }
                                            }
                                            MouseArea {
                                                id: decArea; anchors.fill: parent; hoverEnabled: true
                                                onClicked: settingsDialog._setPending(settingRow._plugin, settingRow.modelData.key,
                                                    stepperRow._round(stepperRow._clamp(settingRow.effectiveValue - stepperRow._step)))
                                            }
                                        }

                                        // Waarde: altijd een box, readOnly totdat je klikt
                                        Rectangle {
                                            width: 72; height: 26
                                            anchors.verticalCenter: parent.verticalCenter
                                            radius: 3
                                            color: stepperRow._editing ? theme.surfaceFloating : "transparent"
                                            border.width: 1
                                            border.color: stepperRow._editing ? theme.accent
                                                        : numHov.hovered      ? theme.border
                                                        : "transparent"
                                            Behavior on border.color { ColorAnimation { duration: 80 } }
                                            Behavior on color        { ColorAnimation { duration: 80 } }

                                            TextInput {
                                                id: stepEdit
                                                anchors.fill: parent
                                                anchors.leftMargin: 5; anchors.rightMargin: 5
                                                horizontalAlignment: TextInput.AlignHCenter
                                                verticalAlignment: TextInput.AlignVCenter
                                                text: settingRow.effectiveValue.toString()
                                                color: stepperRow._editing ? theme.accent : theme.text
                                                font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
                                                selectByMouse: true
                                                readOnly: !stepperRow._editing
                                                inputMethodHints: Qt.ImhFormattedNumbersOnly
                                                Behavior on color { ColorAnimation { duration: 80 } }

                                                Keys.onReturnPressed: stepperRow._commit(text)
                                                Keys.onEscapePressed: {
                                                    text = settingRow.effectiveValue.toString()
                                                    stepperRow._editing = false
                                                }
                                                onActiveFocusChanged: {
                                                    if (!activeFocus && stepperRow._editing) {
                                                        text = settingRow.effectiveValue.toString()
                                                        stepperRow._editing = false
                                                    }
                                                }
                                            }

                                            HoverHandler {
                                                id: numHov
                                                enabled: !stepperRow._editing
                                                cursorShape: Qt.IBeamCursor
                                            }

                                            MouseArea {
                                                anchors.fill: parent
                                                enabled: !stepperRow._editing
                                                acceptedButtons: Qt.LeftButton
                                                onClicked: {
                                                    stepperRow._editing = true
                                                    stepEdit.forceActiveFocus()
                                                    stepEdit.selectAll()
                                                }
                                            }
                                        }

                                        // + knop
                                        Item {
                                            width: 24; height: 26
                                            anchors.verticalCenter: parent.verticalCenter
                                            Text {
                                                anchors.centerIn: parent
                                                text: "+"
                                                color: incArea.containsMouse ? theme.text : theme.textMuted
                                                font.pixelSize: theme.fontSizeBase; font.family: theme.fontFamily
                                                Behavior on color { ColorAnimation { duration: 80 } }
                                            }
                                            MouseArea {
                                                id: incArea; anchors.fill: parent; hoverEnabled: true
                                                onClicked: settingsDialog._setPending(settingRow._plugin, settingRow.modelData.key,
                                                    stepperRow._round(stepperRow._clamp(settingRow.effectiveValue + stepperRow._step)))
                                            }
                                        }
                                    }

                                    // Str → tekst-invoervak
                                    Rectangle {
                                        visible: settingRow.modelData.type === "str"
                                        anchors.right: parent.right; anchors.rightMargin: 12
                                        anchors.verticalCenter: parent.verticalCenter
                                        width: 120; height: 28; radius: 4
                                        color: theme.surfaceFloating
                                        border.width: 1
                                        border.color: strInput.activeFocus ? theme.accent : theme.border
                                        Behavior on border.color { ColorAnimation { duration: 80 } }

                                        TextInput {
                                            id: strInput
                                            anchors.fill: parent; anchors.leftMargin: 8; anchors.rightMargin: 8
                                            verticalAlignment: TextInput.AlignVCenter
                                            text: settingRow.effectiveValue
                                            color: theme.text
                                            font.pixelSize: theme.fontSizeSmall; font.family: theme.fontFamily
                                            selectByMouse: true
                                            Keys.onReturnPressed: settingsDialog._setPending(
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
                                        onColorPicked: (hex) => settingsDialog._setPending(
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
            onCloseClicked:  settingsPanelViewModel.closePanel()
        }
    }
}
