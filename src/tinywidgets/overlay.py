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
from typing import cast

from PySide6.QtCore import QUrl

from tinycore.log import get_logger
from tinycore.qt.engine import create_engine
from tinycore.qt.loop import PollLoop
from tinycore.session.runtime import SessionRuntime
from .config_store import WidgetConfigStore
from .context import WidgetContext, WidgetModel, WidgetOverlayState
from .runner import ProviderUpdater, TextWidgetRunner
from .spec import WidgetSpec

_QML_DIR = Path(__file__).resolve().parent / "qml"
_log = get_logger(__name__)


class WidgetOverlay:
    """Creates and manages all widget windows.

    Usage (from composition root):
        overlay = WidgetOverlay(session, config_dir=_config_dir())
        overlay.load(specs, plugin_name="demo")
        exit_code = tinyui.launch(core, lifecycle, pre_run=overlay.start,
                                  extra_context={"widgetModel": overlay.model})
    """

    def __init__(self, session: SessionRuntime,
                 config_dir: Path | None = None) -> None:
        self._session = session
        self._config_dir = config_dir
        self._poll_loop  = PollLoop(interval_ms=100)
        self._model      = WidgetModel()
        self._state      = WidgetOverlayState()
        self._engine     = None

        self._poll_loop.register(ProviderUpdater(session))

    @property
    def model(self) -> WidgetModel:
        """The widget model — can be registered in any QML engine."""
        return self._model

    @property
    def state(self) -> WidgetOverlayState:
        """Shared overlay state used by both the main UI and widget engine."""
        return self._state

    def load(self, specs: list[WidgetSpec], plugin_name: str) -> None:
        """Create a runner + context for every enabled widget spec."""
        store = (
            WidgetConfigStore(self._config_dir, plugin_name)
            if self._config_dir else None
        )

        for spec in specs:
            if not spec.capability or not spec.field:
                continue

            # Override spec defaults with persisted user config
            if store:
                saved = store.get(spec.id)
                if saved:
                    spec.enable      = saved.get("enable", spec.enable)
                    spec.x           = saved.get("x", spec.x)
                    spec.y           = saved.get("y", spec.y)
                    spec.label       = saved.get("label", spec.label)
                    if "thresholds" in saved:
                        from .threshold import ThresholdEntry
                        spec.thresholds = [
                            ThresholdEntry(
                                t["value"],
                                t["color"],
                                t.get("flash",                        False),
                                t.get("flashSpeed",  t.get("flash_speed",  5)),
                                t.get("flashTarget", t.get("flash_target", "value")),
                            )
                            for t in saved["thresholds"]
                        ]

            ctx    = WidgetContext(spec, self._session.controls, plugin_name)
            runner = TextWidgetRunner(spec, self._session, plugin_name, ctx.update)

            if store:
                def _save(cx: WidgetContext = ctx, s: WidgetConfigStore = store) -> None:
                    s.save(
                        cx._spec.id,
                        cx._spec.enable,
                        cx._spec.x,
                        cx._spec.y,
                        cx._spec.label,
                        cast(list[dict[str, object]], cx.thresholds),
                    )

                ctx.positionChanged.connect(_save)
                ctx.configChanged.connect(_save)

            self._model.add(ctx)
            self._poll_loop.register(runner)
            _log.overlay(
                "loaded widget",
                id=spec.id,
                capability=spec.capability,
                field=spec.field,
            )

    def start(self) -> None:
        """Create widget windows and start polling.

        Must be called after QApplication exists (i.e. inside pre_run).
        """
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is not None:
            app.aboutToQuit.connect(self.stop)

        self._engine = create_engine()
        self._engine.rootContext().setContextProperty("widgetModel", self._model)
        self._engine.rootContext().setContextProperty("widgetOverlayState", self._state)

        frozen_root = getattr(sys, "_MEIPASS", None)
        qml_dir = (
            Path(frozen_root) / "tinywidgets" / "qml"
            if getattr(sys, "frozen", False) and isinstance(frozen_root, str)
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
