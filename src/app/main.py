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
"""Composition root — the only place that knows about all layers.

Boot order:
  1. Build tinycore (plugins register their specs)
  2. Each component registers its host settings
  3. Load persisted config/settings from disk
  4. Start core (emit app.started)
  5. Create lifecycle manager, activate first plugin
  6. Hand off to tinyui for the Qt event loop
"""

from __future__ import annotations

import multiprocessing as mp
import sys
from pathlib import Path

from pathlib import Path

from tinycore import PluginLifecycleManager, PluginSpec, SubprocessPlugin, create_app
from tinyui import TinyUIPlugin, launch
from tinywidgets.overlay import WidgetOverlay
from tinywidgets.spec import load_widgets_toml


def _config_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent / "config"
    return Path(__file__).resolve().parents[2] / "data" / "plugin-config"


def main() -> None:
    # ── 1. Build tinycore ─────────────────────────────────────────────────────
    core = create_app(
        _config_dir(),
        SubprocessPlugin(PluginSpec("plugins.demo", "DemoPlugin")),
    )

    # ── 2. Register host settings ─────────────────────────────────────────────
    # Must happen before load_persisted so specs exist when values are loaded.
    TinyUIPlugin().register(core)

    # ── 3. Load persisted config + settings ───────────────────────────────────
    core.loaders.load_all(core.config)
    core.settings.load_persisted()
    core.host_settings.load_persisted()

    # ── 4. Start core ─────────────────────────────────────────────────────────
    core.start(plugins=False)

    # ── 5. Lifecycle — activate first plugin immediately ──────────────────────
    lifecycle = PluginLifecycleManager(core.plugins, grace_seconds=30.0)
    plugin_names = [p.name for p in core.plugins.plugins]
    if plugin_names:
        lifecycle.activate(plugin_names[0])

    # ── 6. Register connectors (host-side — cannot cross the subprocess pipe) ─
    from plugins.demo.connector.lmu import LMUConnector
    _lmu = LMUConnector()
    _lmu.open()
    core.connectors.register("demo", _lmu)

    # ── 7. Build widget overlay ───────────────────────────────────────────────
    overlay = WidgetOverlay(core.connectors)
    _demo_widgets = Path(__file__).resolve().parents[1] / "plugins" / "demo" / "widgets.toml"
    overlay.load(load_widgets_toml(_demo_widgets), plugin_name="demo")

    # ── 8. Hand off to tinyui ─────────────────────────────────────────────────
    exit_code = launch(core, lifecycle, pre_run=overlay.start)
    overlay.stop()
    sys.exit(exit_code)


if __name__ == "__main__":
    mp.freeze_support()
    main()
