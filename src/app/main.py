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
  1. Scan plugin manifests
  2. Build tinycore with discovered plugins
  3. Register host settings
  4. Load persisted config/settings from disk
  5. Start core
  6. Activate plugins, register host-side connectors
  7. Build widget overlay from manifest widget declarations
  8. Hand off to tinyui for the Qt event loop
"""

from __future__ import annotations

import multiprocessing as mp
import sys
from pathlib import Path

from tinycore import PluginLifecycleManager, PluginSpec, SubprocessPlugin, create_app
from tinycore.plugin.manifest import scan_plugins
from tinyui import TinyUIPlugin, launch
from tinywidgets.overlay import WidgetOverlay
from tinywidgets.spec import load_widgets_toml


def _config_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent / "config"
    return Path(__file__).resolve().parents[2] / "data" / "plugin-config"


def _plugins_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent / "plugins"
    return Path(__file__).resolve().parents[1] / "plugins"


def main() -> None:
    # ── 1. Discover plugins via manifests ─────────────────────────────────────
    manifests = scan_plugins(_plugins_dir())

    # ── 2. Build tinycore ─────────────────────────────────────────────────────
    core = create_app(
        _config_dir(),
        *[SubprocessPlugin(PluginSpec(m.module, m.class_name)) for m in manifests],
    )

    # ── 3. Register host settings ─────────────────────────────────────────────
    TinyUIPlugin().register(core)

    # ── 4. Load persisted config + settings ───────────────────────────────────
    core.loaders.load_all(core.config)
    core.settings.load_persisted()
    core.host_settings.load_persisted()

    # ── 5. Start core ─────────────────────────────────────────────────────────
    core.start(plugins=False)

    # ── 6. Activate plugins + register host-side connectors ───────────────────
    lifecycle = PluginLifecycleManager(core.plugins, grace_seconds=30.0)
    plugin_names = [p.name for p in core.plugins.plugins]
    if plugin_names:
        lifecycle.activate(plugin_names[0])

    for m in manifests:
        if m.connector is None:
            continue
        connector = m.connector.create()
        connector.open()
        core.connectors.register(m.name, connector)

    # ── 7. Build widget overlay ───────────────────────────────────────────────
    overlay = WidgetOverlay(core.connectors, config_dir=_config_dir())
    for m in manifests:
        wp = m.widgets_path()
        if wp and wp.exists():
            overlay.load(load_widgets_toml(wp), plugin_name=m.name)

    # ── 8. Hand off to tinyui ─────────────────────────────────────────────────
    exit_code = launch(core, lifecycle, pre_run=overlay.start,
                       extra_context={"widgetModel": overlay.model})
    overlay.stop()
    sys.exit(exit_code)


if __name__ == "__main__":
    mp.freeze_support()
    main()
