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
    id: root

    readonly property var hostWindow: Window.window
    readonly property var theme: hostWindow && hostWindow.theme ? hostWindow.theme : null
    readonly property var runtimeContext: hostWindow && hostWindow.runtimeContext ? hostWindow.runtimeContext : null
    readonly property var imageSources: runtimeContext && runtimeContext.imageSources ? runtimeContext.imageSources : null
    readonly property var settingsRead: runtimeContext && runtimeContext.settingsRead ? runtimeContext.settingsRead : null
    readonly property var settingsWrite: runtimeContext && runtimeContext.settingsWrite ? runtimeContext.settingsWrite : null

    property int activeTab: 0
    property var pendingChanges: ({})
    property var savedOverrides: ({})

    readonly property bool hasPendingChanges: {
        for (var namespace in pendingChanges) {
            if (Object.keys(pendingChanges[namespace] || {}).length > 0)
                return true;
        }
        return false;
    }

    anchors.fill: parent

    function c(token, fallback) {
        return theme ? theme[token] : fallback;
    }

    function f(token, fallback) {
        return theme ? theme[token] : fallback;
    }

    function settings() {
        return settingsRead ? settingsRead.settings : [];
    }

    function namespaceGroups() {
        var groups = [];
        var byNamespace = ({});
        var items = settings();

        for (var i = 0; i < items.length; i++) {
            var setting = items[i];
            var namespace = setting.namespace || "tinyui";
            if (byNamespace[namespace] === undefined) {
                byNamespace[namespace] = {
                    "namespace": namespace,
                    "settings": []
                };
                groups.push(byNamespace[namespace]);
            }
            byNamespace[namespace].settings.push(setting);
        }

        return groups;
    }

    function activeGroup() {
        var groups = namespaceGroups();
        if (groups.length === 0)
            return null;
        if (activeTab >= groups.length)
            activeTab = 0;
        return groups[activeTab];
    }

    function activeSettings() {
        var group = activeGroup();
        return group ? group.settings : [];
    }

    function rawSettingValue(setting) {
        if (!setting)
            return "";

        var namespaceOverrides = savedOverrides[setting.namespace];
        if (namespaceOverrides && namespaceOverrides[setting.key] !== undefined)
            return namespaceOverrides[setting.key];

        return setting.currentValue;
    }

    function effectiveValue(setting) {
        if (!setting)
            return "";

        var namespaceChanges = pendingChanges[setting.namespace];
        if (namespaceChanges && namespaceChanges[setting.key] !== undefined)
            return namespaceChanges[setting.key];

        return rawSettingValue(setting);
    }

    function displayValue(setting) {
        var value = effectiveValue(setting);
        if (setting && setting.type === "bool")
            return boolValue(value) ? "true" : "false";
        return String(value);
    }

    function boolValue(value) {
        return value === true || value === "true" || value === "True" || value === "1";
    }

    function intValue(value) {
        var parsed = parseInt(value);
        return isNaN(parsed) ? 0 : parsed;
    }

    function setPending(namespace, key, value) {
        var next = Object.assign({}, pendingChanges);
        next[namespace] = Object.assign({}, next[namespace] || {});
        next[namespace][key] = value;
        pendingChanges = next;
    }

    function isPending(setting) {
        var namespaceChanges = setting ? pendingChanges[setting.namespace] : null;
        return namespaceChanges !== null && namespaceChanges !== undefined && namespaceChanges[setting.key] !== undefined;
    }

    function pendingCount(namespace) {
        var namespaceChanges = pendingChanges[namespace];
        return namespaceChanges ? Object.keys(namespaceChanges).length : 0;
    }

    function applyPending() {
        if (!settingsWrite)
            return;
        var nextSaved = Object.assign({}, savedOverrides);
        for (var namespace in pendingChanges) {
            var changes = pendingChanges[namespace];
            nextSaved[namespace] = Object.assign({}, nextSaved[namespace] || {});
            for (var key in changes) {
                settingsWrite.setValue(namespace, key, changes[key]);
                nextSaved[namespace][key] = changes[key];
            }
            settingsWrite.save(namespace);
        }
        savedOverrides = nextSaved;
        pendingChanges = ({});
    }

    Rectangle {
        anchors.fill: parent
        color: root.c("surface", "#17181c")
    }

    Row {
        anchors.fill: parent
        spacing: 0

        Rectangle {
            id: tabPane
            width: 176
            height: parent.height
            color: root.c("surfaceAlt", "#2f343e")

            ListView {
                id: tabList
                anchors.fill: parent
                model: root.namespaceGroups()
                clip: true

                delegate: Rectangle {
                    id: tabItem
                    required property var modelData
                    required property int index

                    readonly property bool active: root.activeTab === index

                    width: tabList.width
                    height: 40
                    color: active ? root.c("surface", "#17181c") : (tabHover.hovered ? root.c("surfaceRaised", "#3b414d") : "transparent")
                    Behavior on color {
                        ColorAnimation {
                            duration: 80
                        }
                    }

                    Rectangle {
                        width: 2
                        height: parent.height
                        color: root.c("accent", "#4a9eff")
                        visible: tabItem.active
                    }

                    Text {
                        anchors.left: parent.left
                        anchors.leftMargin: 16
                        anchors.right: pendingDot.left
                        anchors.rightMargin: 8
                        anchors.verticalCenter: parent.verticalCenter
                        text: tabItem.modelData.namespace
                        color: tabItem.active ? root.c("text", "#dce0e5") : root.c("textMuted", "#878a98")
                        font.pixelSize: root.f("fontSizeBase", 13)
                        font.family: root.f("fontFamily", "sans-serif")
                        font.weight: tabItem.active ? Font.DemiBold : Font.Normal
                        elide: Text.ElideRight
                        Behavior on color {
                            ColorAnimation {
                                duration: 80
                            }
                        }
                    }

                    Text {
                        id: pendingDot
                        anchors.right: parent.right
                        anchors.rightMargin: 12
                        anchors.verticalCenter: parent.verticalCenter
                        text: "*"
                        color: root.c("accent", "#4a9eff")
                        font.pixelSize: 6
                        font.family: root.f("fontFamily", "sans-serif")
                        visible: root.pendingCount(tabItem.modelData.namespace) > 0
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: root.activeTab = tabItem.index
                    }

                    HoverHandler {
                        id: tabHover
                    }
                }
            }

            Rectangle {
                anchors.right: parent.right
                width: 1
                height: parent.height
                color: root.c("border", "#464b57")
            }
        }

        Item {
            width: parent.width - tabPane.width
            height: parent.height

            Rectangle {
                id: header
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: parent.right
                height: 56
                color: "transparent"

                Column {
                    anchors.left: parent.left
                    anchors.leftMargin: 16
                    anchors.right: parent.right
                    anchors.rightMargin: 16
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 3

                    Text {
                        width: parent.width
                        text: root.activeGroup() ? root.activeGroup().namespace : "Settings"
                        color: root.c("text", "#dce0e5")
                        font.pixelSize: root.f("fontSizeBase", 13)
                        font.family: root.f("fontFamily", "sans-serif")
                        font.weight: Font.DemiBold
                        elide: Text.ElideRight
                    }

                    Text {
                        width: parent.width
                        text: root.hasPendingChanges ? "Unsaved changes" : "Application settings"
                        color: root.hasPendingChanges ? root.c("accent", "#4a9eff") : root.c("textMuted", "#878a98")
                        font.pixelSize: root.f("fontSizeSmall", 11)
                        font.family: root.f("fontFamily", "sans-serif")
                        elide: Text.ElideRight
                        Behavior on color {
                            ColorAnimation {
                                duration: 120
                            }
                        }
                    }
                }

                Rectangle {
                    anchors.bottom: parent.bottom
                    width: parent.width
                    height: 1
                    color: root.c("border", "#464b57")
                }
            }

            Flickable {
                id: contentFlick
                anchors.top: header.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: footer.top
                contentHeight: settingsColumn.implicitHeight + 16
                clip: true

                Column {
                    id: settingsColumn
                    anchors.left: parent.left
                    anchors.right: parent.right
                    spacing: 0

                    SectionHeader {
                        text: "Settings"
                    }

                    Repeater {
                        model: root.activeSettings()

                        EditRow {
                            id: settingRow
                            required property var modelData

                            label: modelData.label || modelData.key
                            description: modelData.key
                            value: root.displayValue(modelData)
                            pending: root.isPending(modelData)

                            ToggleSwitch {
                                visible: settingRow.modelData.type === "bool"
                                anchors.right: parent.right
                                anchors.verticalCenter: parent.verticalCenter
                                checked: root.boolValue(root.effectiveValue(settingRow.modelData))
                                enabled: root.settingsWrite !== null
                                onToggled: v => root.setPending(settingRow.modelData.namespace, settingRow.modelData.key, v)
                            }

                            ChoiceBox {
                                visible: settingRow.modelData.type === "choice"
                                anchors.right: parent.right
                                anchors.verticalCenter: parent.verticalCenter
                                choices: settingRow.modelData.choices || []
                                currentValue: root.displayValue(settingRow.modelData)
                                enabled: root.settingsWrite !== null
                                onPicked: v => root.setPending(settingRow.modelData.namespace, settingRow.modelData.key, v)
                            }

                            NumberStepper {
                                visible: settingRow.modelData.type === "int"
                                anchors.right: parent.right
                                anchors.verticalCenter: parent.verticalCenter
                                value: root.intValue(root.effectiveValue(settingRow.modelData))
                                enabled: root.settingsWrite !== null
                                onCommit: v => root.setPending(settingRow.modelData.namespace, settingRow.modelData.key, v)
                            }

                            TextField {
                                visible: settingRow.modelData.type === "str"
                                anchors.right: parent.right
                                anchors.verticalCenter: parent.verticalCenter
                                value: root.displayValue(settingRow.modelData)
                                enabled: root.settingsWrite !== null
                                onCommit: v => root.setPending(settingRow.modelData.namespace, settingRow.modelData.key, v)
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
                height: 48
                color: root.c("surfaceAlt", "#2f343e")

                Rectangle {
                    anchors.top: parent.top
                    width: parent.width
                    height: 1
                    color: root.c("border", "#464b57")
                }

                Row {
                    anchors.right: parent.right
                    anchors.rightMargin: 12
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 8

                    FooterButton {
                        text: "Revert"
                        enabled: root.hasPendingChanges
                        onClicked: root.pendingChanges = ({})
                    }

                    FooterButton {
                        text: "Save"
                        accent: true
                        enabled: root.hasPendingChanges && root.settingsWrite !== null
                        onClicked: root.applyPending()
                    }
                }
            }
        }
    }

    component SectionHeader: Rectangle {
        id: sectionHeaderRoot
        property string text: ""

        anchors.left: parent ? parent.left : undefined
        anchors.right: parent ? parent.right : undefined
        height: 28
        color: root.c("surfaceAlt", "#2f343e")

        Text {
            anchors.left: parent.left
            anchors.leftMargin: 16
            anchors.verticalCenter: parent.verticalCenter
            text: sectionHeaderRoot.text
            color: root.c("textSecondary", "#a9afbc")
            font.pixelSize: root.f("fontSizeSmall", 11)
            font.family: root.f("fontFamily", "sans-serif")
            font.weight: Font.Medium
        }

        Rectangle {
            anchors.bottom: parent.bottom
            width: parent.width
            height: 1
            color: root.c("border", "#464b57")
        }
    }

    component EditRow: Rectangle {
        id: editRowRoot
        property string label: ""
        property string description: ""
        property string value: ""
        property bool pending: false
        default property alias rightContent: rightSlot.data

        anchors.left: parent ? parent.left : undefined
        anchors.right: parent ? parent.right : undefined
        implicitHeight: 52
        color: "transparent"

        Rectangle {
            anchors.fill: parent
            opacity: rowHover.hovered ? 1 : 0
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
            color: root.c("border", "#464b57")
            opacity: 0.4
        }

        Column {
            anchors.left: parent.left
            anchors.leftMargin: 16
            anchors.right: rightSlot.left
            anchors.rightMargin: 8
            anchors.verticalCenter: parent.verticalCenter
            spacing: 3

            Row {
                width: parent.width
                spacing: 6

                Text {
                    width: parent.width - (editPendingDot.visible ? editPendingDot.width + 6 : 0)
                    text: editRowRoot.label
                    color: editRowRoot.pending ? root.c("accent", "#4a9eff") : root.c("text", "#dce0e5")
                    font.pixelSize: root.f("fontSizeBase", 13)
                    font.family: root.f("fontFamily", "sans-serif")
                    elide: Text.ElideRight
                    Behavior on color {
                        ColorAnimation {
                            duration: 120
                        }
                    }
                }

                Text {
                    id: editPendingDot
                    visible: editRowRoot.pending
                    text: "*"
                    color: root.c("accent", "#4a9eff")
                    font.pixelSize: 6
                    font.family: root.f("fontFamily", "sans-serif")
                    anchors.bottom: parent.bottom
                    anchors.bottomMargin: 3
                }
            }

            Text {
                width: parent.width
                text: editRowRoot.description !== "" ? editRowRoot.description : editRowRoot.value
                color: rowHover.hovered ? "#dec184" : root.c("textMuted", "#878a98")
                font.pixelSize: root.f("fontSizeSmall", 11)
                font.family: root.f("fontFamily", "sans-serif")
                elide: Text.ElideRight
                Behavior on color {
                    ColorAnimation {
                        duration: 120
                    }
                }
            }
        }

        Item {
            id: rightSlot
            anchors.right: parent.right
            anchors.rightMargin: 12
            anchors.verticalCenter: parent.verticalCenter
            width: 128
            height: parent.height
        }

        HoverHandler {
            id: rowHover
        }
    }

    component TextField: Rectangle {
        id: textFieldRoot
        property string value: ""
        signal commit(string value)

        width: 120
        height: 28
        radius: 4
        color: enabled ? root.c("surfaceFloating", "#20242b") : root.c("surfaceAlt", "#2f343e")
        border.width: 1
        border.color: input.activeFocus ? root.c("accent", "#4a9eff") : root.c("border", "#464b57")
        opacity: enabled ? 1 : 0.6
        Behavior on border.color {
            ColorAnimation {
                duration: 80
            }
        }

        TextInput {
            id: input
            anchors.fill: parent
            anchors.leftMargin: 8
            anchors.rightMargin: 8
            verticalAlignment: TextInput.AlignVCenter
            text: textFieldRoot.value
            color: root.c("text", "#dce0e5")
            font.pixelSize: root.f("fontSizeSmall", 11)
            font.family: root.f("fontFamily", "sans-serif")
            selectByMouse: true
            enabled: textFieldRoot.enabled
            onEditingFinished: textFieldRoot.commit(text)
            Keys.onEscapePressed: {
                text = textFieldRoot.value;
                focus = false;
            }
        }
    }

    component ChoiceBox: Rectangle {
        id: choiceRoot
        property var choices: []
        property string currentValue: ""
        property bool open: false
        signal picked(string value)

        width: 120
        height: 28
        radius: 4
        color: enabled ? root.c("surfaceFloating", "#20242b") : root.c("surfaceAlt", "#2f343e")
        border.width: 1
        border.color: open ? root.c("accent", "#4a9eff") : root.c("border", "#464b57")
        opacity: enabled ? 1 : 0.6
        clip: false
        z: open ? 20 : 0
        Behavior on border.color {
            ColorAnimation {
                duration: 80
            }
        }

        Text {
            anchors.left: parent.left
            anchors.leftMargin: 8
            anchors.right: arrow.left
            anchors.rightMargin: 6
            anchors.verticalCenter: parent.verticalCenter
            text: choiceRoot.currentValue
            color: root.c("text", "#dce0e5")
            font.pixelSize: root.f("fontSizeSmall", 11)
            font.family: root.f("fontFamily", "sans-serif")
            elide: Text.ElideRight
        }

        Image {
            id: arrow
            anchors.right: parent.right
            anchors.rightMargin: 8
            anchors.verticalCenter: parent.verticalCenter
            width: 10
            height: 6
            source: root.imageSources ? root.imageSources.imageUrl("ui.caret-down") : ""
            sourceSize.width: 10
            sourceSize.height: 6
            fillMode: Image.PreserveAspectFit
            rotation: choiceRoot.open ? 180 : 0
            opacity: enabled ? 1.0 : 0.6
            Behavior on rotation {
                NumberAnimation {
                    duration: 80
                }
            }
        }

        MouseArea {
            anchors.fill: parent
            enabled: choiceRoot.enabled
            onClicked: choiceRoot.open = !choiceRoot.open
        }

        Column {
            anchors.top: parent.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            visible: choiceRoot.open
            z: 30

            Repeater {
                model: choiceRoot.choices

                Rectangle {
                    id: choiceItem
                    required property string modelData

                    width: choiceRoot.width
                    height: 28
                    color: choiceHover.hovered ? root.c("surfaceRaised", "#3b414d") : root.c("surfaceFloating", "#20242b")
                    border.width: 1
                    border.color: root.c("border", "#464b57")

                    Text {
                        anchors.left: parent.left
                        anchors.leftMargin: 8
                        anchors.right: parent.right
                        anchors.rightMargin: 8
                        anchors.verticalCenter: parent.verticalCenter
                        text: choiceItem.modelData
                        color: choiceItem.modelData === choiceRoot.currentValue ? root.c("accent", "#4a9eff") : root.c("text", "#dce0e5")
                        font.pixelSize: root.f("fontSizeSmall", 11)
                        font.family: root.f("fontFamily", "sans-serif")
                        elide: Text.ElideRight
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            choiceRoot.open = false;
                            choiceRoot.picked(choiceItem.modelData);
                        }
                    }

                    HoverHandler {
                        id: choiceHover
                    }
                }
            }
        }
    }

    component NumberStepper: Rectangle {
        id: stepperRoot
        property int value: 0
        property int step: 1
        signal commit(int value)

        width: 120
        height: 28
        radius: 4
        color: enabled ? root.c("surfaceFloating", "#20242b") : root.c("surfaceAlt", "#2f343e")
        border.width: 1
        border.color: valueInput.activeFocus ? root.c("accent", "#4a9eff") : root.c("border", "#464b57")
        opacity: enabled ? 1 : 0.6
        Behavior on border.color {
            ColorAnimation {
                duration: 80
            }
        }

        Row {
            anchors.fill: parent

            StepperButton {
                label: "-"
                enabled: stepperRoot.enabled
                onPressed: {
                    stepperRoot.value = stepperRoot.value - stepperRoot.step;
                    stepperRoot.commit(stepperRoot.value);
                }
            }

            TextInput {
                id: valueInput
                width: parent.width - 48
                height: parent.height
                verticalAlignment: TextInput.AlignVCenter
                horizontalAlignment: TextInput.AlignHCenter
                text: String(stepperRoot.value)
                color: root.c("text", "#dce0e5")
                font.pixelSize: root.f("fontSizeSmall", 11)
                font.family: root.f("fontFamily", "sans-serif")
                selectByMouse: true
                validator: IntValidator {}
                enabled: stepperRoot.enabled
                onEditingFinished: {
                    var parsed = parseInt(text);
                    if (!isNaN(parsed)) {
                        stepperRoot.value = parsed;
                        stepperRoot.commit(parsed);
                    } else {
                        text = String(stepperRoot.value);
                    }
                }
            }

            StepperButton {
                label: "+"
                enabled: stepperRoot.enabled
                onPressed: {
                    stepperRoot.value = stepperRoot.value + stepperRoot.step;
                    stepperRoot.commit(stepperRoot.value);
                }
            }
        }
    }

    component StepperButton: Item {
        id: stepperButtonRoot
        property string label: ""
        signal pressed

        width: 24
        height: parent ? parent.height : 28
        opacity: enabled ? 1 : 0.5

        Rectangle {
            anchors.fill: parent
            color: stepperHover.hovered ? root.c("surfaceRaised", "#3b414d") : "transparent"
            Behavior on color {
                ColorAnimation {
                    duration: 80
                }
            }
        }

        Text {
            anchors.centerIn: parent
            text: stepperButtonRoot.label
            color: root.c("textSecondary", "#a9afbc")
            font.pixelSize: root.f("fontSizeBase", 13)
            font.family: root.f("fontFamily", "sans-serif")
        }

        MouseArea {
            anchors.fill: parent
            enabled: stepperButtonRoot.enabled
            onClicked: stepperButtonRoot.pressed()
        }

        HoverHandler {
            id: stepperHover
        }
    }

    component ToggleSwitch: Item {
        id: toggleRoot
        property bool checked: false
        signal toggled(bool checked)

        width: 34
        height: 18
        opacity: enabled ? 1 : 0.45

        Rectangle {
            anchors.fill: parent
            radius: height / 2
            color: toggleRoot.checked ? root.c("accent", "#4a9eff") : root.c("surfaceFloating", "#20242b")
            border.width: 1
            border.color: toggleRoot.checked ? root.c("accentHover", "#6bb6ff") : root.c("border", "#464b57")
            Behavior on color {
                ColorAnimation {
                    duration: 100
                }
            }
            Behavior on border.color {
                ColorAnimation {
                    duration: 100
                }
            }
        }

        Rectangle {
            width: 14
            height: 14
            radius: 7
            y: 2
            x: toggleRoot.checked ? toggleRoot.width - width - 2 : 2
            color: toggleRoot.checked ? root.c("accentText", "#ffffff") : root.c("textMuted", "#878a98")
            Behavior on x {
                NumberAnimation {
                    duration: 120
                    easing.type: Easing.OutCubic
                }
            }
            Behavior on color {
                ColorAnimation {
                    duration: 100
                }
            }
        }

        MouseArea {
            anchors.fill: parent
            enabled: toggleRoot.enabled
            onClicked: {
                toggleRoot.checked = !toggleRoot.checked;
                toggleRoot.toggled(toggleRoot.checked);
            }
        }
    }

    component FooterButton: Rectangle {
        id: footerButtonRoot
        property string text: ""
        property bool accent: false
        signal clicked

        width: 84
        height: 28
        radius: 4
        color: enabled ? (accent ? root.c("accent", "#4a9eff") : root.c("surfaceFloating", "#20242b")) : root.c("surface", "#17181c")
        border.width: 1
        border.color: enabled ? (accent ? root.c("accentHover", "#6bb6ff") : root.c("border", "#464b57")) : root.c("border", "#464b57")
        opacity: enabled ? 1 : 0.55
        Behavior on color {
            ColorAnimation {
                duration: 80
            }
        }

        Text {
            anchors.centerIn: parent
            text: footerButtonRoot.text
            color: footerButtonRoot.accent ? root.c("accentText", "#ffffff") : root.c("text", "#dce0e5")
            font.pixelSize: root.f("fontSizeSmall", 11)
            font.family: root.f("fontFamily", "sans-serif")
            font.weight: Font.DemiBold
        }

        MouseArea {
            anchors.fill: parent
            enabled: footerButtonRoot.enabled
            onClicked: footerButtonRoot.clicked()
        }
    }
}
