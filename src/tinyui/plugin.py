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
"""TinyUIPlugin — registers host settings directly on App.host_settings.

TinyUI is the host application, not a plugin. It registers its settings
on App.host_settings which is not exposed to plugins via PluginContext.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tinycore import SettingsSpec

if TYPE_CHECKING:
    from tinycore import App


class TinyUIPlugin:
    """Registers TinyUI host settings outside the plugin system."""

    name = "TinyUI"

    def register(self, app: App) -> None:
        _r = app.host_settings.register
        _n = self.name

        # ── Application ───────────────────────────────────────────────────
        _r(_n, SettingsSpec(
            key="theme", label="Theme", type="enum",
            default="dark", options=["dark", "light"],
            description="Application color theme",
            section="Application",
        ))
        # TODO: implement language switching
        _r(_n, SettingsSpec(
            key="language", label="Language", type="enum",
            default="en", options=["en", "nl"],
            description="Interface language (not yet implemented)",
            section="Application",
        ))

        # ── Window ────────────────────────────────────────────────────────
        _r(_n, SettingsSpec(
            key="remember_position", label="Remember position", type="bool",
            default=True,
            description="Restore window position on startup",
            section="Window",
        ))
        _r(_n, SettingsSpec(
            key="remember_size", label="Remember size", type="bool",
            default=True,
            description="Restore window size on startup",
            section="Window",
        ))

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass
