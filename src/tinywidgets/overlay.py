#  TinyUI
#  Copyright (C) 2026 Oost-hash
#
#  This file is part of TinyUI.
#
#  TinyUI is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  TinyUI is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  TinyUI builds on TinyPedal by s-victor (https://github.com/s-victor/TinyPedal),
#  licensed under GPLv3.
"""WidgetOverlay — manages widget windows and the poll loop.

Each widget is its own small top-level window (Qt.Tool), so click-through on
the background is free — no overlay window or setMask() needed.

Called from the composition root; tinyui knows nothing about it.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QUrl

from tinycore.log import get_logger
from tinycore.qt import create_engine
from tinycore.qt.loop import PollLoop
from .context import WidgetContext, WidgetModel
from .runner import ConnectorUpdater, TextWidgetRunner
from .spec import WidgetSpec

if TYPE_CHECKING:
    from tinycore.telemetry.registry import ConnectorRegistry

_QML_DIR = Path(__file__).resolve().parent / "qml"
_log = get_logger(__name__)


class WidgetOverlay:
    """Creates and manages all widget windows.

    Usage (from composition root):
        overlay = WidgetOverlay(connectors)
        overlay.load(specs, plugin_name="demo")
        exit_code = tinyui.launch(core, lifecycle, pre_run=overlay.start)
    """

    def __init__(self, connectors: ConnectorRegistry) -> None:
        self._connectors = connectors
        self._poll_loop  = PollLoop(interval_ms=100)
        self._model      = WidgetModel()
        self._engine     = None

        self._poll_loop.register(ConnectorUpdater(connectors))

    def load(self, specs: list[WidgetSpec], plugin_name: str) -> None:
        """Create a runner + context for every enabled widget spec."""
        for spec in specs:
            if not spec.enable or not spec.source:
                continue
            ctx    = WidgetContext(spec)
            runner = TextWidgetRunner(spec, self._connectors, plugin_name, ctx.update)
            self._model.add(ctx)
            self._poll_loop.register(runner)
            _log.overlay("loaded widget", id=spec.id, source=spec.source)

    def start(self) -> None:
        """Create widget windows and start polling.

        Must be called after QApplication exists (i.e. inside pre_run).
        """
        from PySide6.QtWidgets import QApplication
        QApplication.instance().aboutToQuit.connect(self.stop)

        self._engine = create_engine()
        self._engine.rootContext().setContextProperty("widgetModel", self._model)

        qml_dir = (
            Path(sys._MEIPASS) / "tinywidgets" / "qml"
            if getattr(sys, "frozen", False)
            else _QML_DIR
        )
        self._engine.load(QUrl.fromLocalFile(str(qml_dir / "WidgetHost.qml")))
        _log.overlay("engine started", widgets=self._model.rowCount())
        self._poll_loop.start()

    def stop(self) -> None:
        if self._engine is None:
            return
        _log.overlay("stopping")
        self._poll_loop.stop()
        self._engine.deleteLater()
        self._engine = None
