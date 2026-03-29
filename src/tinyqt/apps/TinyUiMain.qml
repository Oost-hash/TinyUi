import QtQuick
import QtQuick.Window
import TinyQt 1.0

Window {
    id: root

    width: 900
    height: 600
    minimumWidth: 480
    minimumHeight: 320
    visible: true

    title: "TinyUI"
    readonly property bool nativeChrome: Qt.platform.os === "linux" || Qt.platform.os === "osx"
    flags: nativeChrome ? Qt.Window : Qt.Window | Qt.FramelessWindowHint
    color: "#17181c"

    WindowMenuBar {
        x: 0
        y: 0
        width: root.width
    }
}
