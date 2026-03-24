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
"""LogSettingsViewModel — runtime control of debug categories for Dev Tools.

Exposes tinycore's category-based debug subscriptions to QML so the user can
toggle individual channels on/off without restarting the application.
"""

from __future__ import annotations

import tinycore.log as _core_log
from PySide6.QtCore import Property, QObject, Signal, Slot


class LogSettingsViewModel(QObject):
    """Bridges tinycore debug-category control to QML.

    Registered as ``logSettingsViewModel`` in the QML engine context.

    QML usage::

        logSettingsViewModel.setDevMode(true)
        logSettingsViewModel.setCategoryEnabled("connector_polling", false)
        // bind to logSettingsViewModel.categories  →  [{name, enabled}, ...]
    """

    categoriesChanged = Signal()
    devModeChanged    = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

    # ── Dev mode master toggle ────────────────────────────────────────────────

    @Property(bool, notify=devModeChanged)
    def devMode(self) -> bool:
        """True when DEBUG-level output is globally enabled."""
        return _core_log.get_dev_mode()

    @Slot(bool)
    def setDevMode(self, enabled: bool) -> None:
        _core_log.set_dev_mode(enabled)
        self.devModeChanged.emit()
        # Category enabled-state display depends on devMode — refresh the list
        self.categoriesChanged.emit()

    # ── Per-category toggles ──────────────────────────────────────────────────

    @Property("QVariantList", notify=categoriesChanged)
    def categories(self) -> list:
        """List of ``{name, enabled}`` dicts for every known debug category."""
        return [{"name": name, "enabled": enabled}
                for name, enabled in _core_log.get_category_states()]

    @Slot(str, bool)
    def setCategoryEnabled(self, name: str, enabled: bool) -> None:
        _core_log.set_category_enabled(name, enabled)
        self.categoriesChanged.emit()
