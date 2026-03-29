import QtQuick
import QtQuick.Window
import TinyUI 1.0

Window {
    id: settingsDialog

    title: "Settings"
    width: 720
    height: 520
    minimumWidth: 540
    minimumHeight: 380
    visible: SettingsPanelViewModel.open
    color: Theme.surface
    flags: Qt.Window

    onVisibleChanged: {
        if (!visible)
            SettingsPanelViewModel.closePanel()
    }
}
