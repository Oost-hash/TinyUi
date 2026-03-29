import QtQuick
import QtQuick.Window

Window {
    id: settingsDialog

    title: "Settings"
    width: 720
    height: 520
    minimumWidth: 540
    minimumHeight: 380
    visible: settingsPanelViewModel.open
    color: Theme.surface
    flags: Qt.Window

    onVisibleChanged: {
        if (!visible)
            settingsPanelViewModel.closePanel()
    }

    SettingsDialogContent {
        anchors.fill: parent
    }
}
