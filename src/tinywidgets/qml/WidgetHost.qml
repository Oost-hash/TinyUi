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
import TinyWidgets

// Hidden anchor window — Qt.Tool windows need a parent to be visible.
// Each TextWidget sets transientParent: null so it uses screen coordinates.
Window {
    id: anchor
    flags:   Qt.Tool | Qt.FramelessWindowHint
    color:   "transparent"
    width:   0
    height:  0
    visible: true   // must be visible so child windows can appear

    // Expose singleton as property so pragma ComponentBehavior: Bound can resolve it
    readonly property var _model: WidgetModel

    Instantiator {
        model: anchor._model
        delegate: TextWidget {
            required property var widgetContext
            transientParent: null
        }
        onObjectAdded:   (index, object) => { var w = object as Window; if (w) w.show() }
        onObjectRemoved: (index, object) => { var w = object as Window; if (w) w.close() }
    }
}
