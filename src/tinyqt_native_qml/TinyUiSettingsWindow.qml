import QtQuick
import QtQuick.Window

Window {
    id: root

    property string windowTitle: "Settings"

    width: 720
    height: 520
    minimumWidth: 540
    minimumHeight: 380
    visible: true
    title: root.windowTitle
    color: "#17181c"
    flags: Qt.Window
}
