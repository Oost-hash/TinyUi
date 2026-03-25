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

import tinycore.log as _log_mod
_log_mod.configure()  # must run before any other import emits log records

from tinycore import PluginLifecycleManager, SubprocessPlugin, create_app
from tinycore.log import get_logger
from tinycore.plugin.manifest import scan_plugins
from tinyui import TinyUIPlugin, launch
from tinyui.viewmodels.state_monitor_viewmodel import StateMonitorViewModel
from tinywidgets.overlay import WidgetOverlay
from tinywidgets.spec import load_widgets_toml


_log = get_logger(__name__)


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
    consumer_manifests = [m for m in manifests if m.is_consumer]
    provider_manifests = [m for m in manifests if m.is_provider]

    core = create_app(
        _config_dir(),
        *[SubprocessPlugin(m.plugin_spec()) for m in consumer_manifests],
    )

    # ── 3. Register host settings ─────────────────────────────────────────────
    TinyUIPlugin().register(core)

    # ── 4. Load persisted config + settings ───────────────────────────────────
    core.loaders.load_all(core.config)
    core.settings.load_persisted()
    core.host_settings.load_persisted()

    # ── 5. Start core ─────────────────────────────────────────────────────────
    core.start(plugins=False)

    # ── 6. Activate consumer plugins + register host-side providers ──────────
    lifecycle = PluginLifecycleManager(core.plugins, grace_seconds=30.0)
    plugin_names = [p.name for p in core.plugins.plugins]
    if plugin_names:
        lifecycle.activate(plugin_names[0])

    for m in provider_manifests:
        if m.provider is None:
            continue
        real = m.provider.create()
        real.open()
        core.session.register_provider(m.name, real, m.exports)
        core.connectors.register(m.name, real)
        _log.info(
            "provider registered  plugin=%s  type=%s  exports=%s",
            m.name,
            type(real).__name__,
            ", ".join(m.exports) if m.exports else "-",
        )

    for m in consumer_manifests:
        bindings = core.session.bind_consumer(m.name, m.requires)
        if bindings.missing:
            _log.warning(
                "consumer requires missing  plugin=%s  missing=%s",
                m.name,
                ", ".join(bindings.missing),
            )
            continue
        if bindings.resolved:
            _log.info(
                "consumer bound  plugin=%s  requires=%s",
                m.name,
                ", ".join(
                    f"{capability}->{binding.provider_name}"
                    for capability, binding in bindings.resolved.items()
                ),
            )

    # ── 7. Build widget overlay ───────────────────────────────────────────────
    overlay = WidgetOverlay(core.connectors, core.session, config_dir=_config_dir())
    sources: list[tuple[str, str, str]] = []
    for m in consumer_manifests:
        wp = m.widgets_path()
        if wp and wp.exists():
            specs = load_widgets_toml(wp)
            overlay.load(specs, plugin_name=m.name)
            sources.extend((m.name, s.capability, s.source) for s in specs if s.source)

    # ── 8. State monitor for Dev Tools ────────────────────────────────────────
    state_monitor = StateMonitorViewModel()
    state_monitor.setup(core.connectors, core.session, sources)
    for ctx in overlay.model.contexts:
        state_monitor.register_object(f"Widget: {ctx.title}", ctx)

    # ── 9. Hand off to tinyui ─────────────────────────────────────────────────
    extra: dict = {
        "widgetModel":           overlay.model,
        "stateMonitorViewModel": state_monitor,
    }

    def _pre_run() -> None:
        overlay.start()
        state_monitor.start()   # QApplication exists here — safe to start QTimer

    exit_code = launch(core, lifecycle, pre_run=_pre_run, extra_context=extra)
    state_monitor.shutdown()
    overlay.stop()
    sys.exit(exit_code)


if __name__ == "__main__":
    mp.freeze_support()
    main()
