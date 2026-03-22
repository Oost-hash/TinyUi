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
"""SubprocessPlugin — host-side wrapper for a subprocess-isolated plugin.

The plugin module is never imported in the host process. All communication
goes through a multiprocessing.Pipe (pickle-serialised).
"""

from __future__ import annotations

import multiprocessing as mp
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from multiprocessing.connection import Connection

    from tinycore.plugin.context import PluginContext
    from tinycore.plugin.spec import PluginSpec


class SubprocessPlugin:
    """Host-side manager for a plugin running in an isolated subprocess.

    Implements the Plugin protocol (name / register / start / stop) so it
    drops in wherever a regular plugin is expected.
    """

    def __init__(self, spec: PluginSpec) -> None:
        self._spec = spec
        self._proc: mp.Process | None = None
        self._conn: Connection | None = None   # parent-side pipe end

    # ── Plugin protocol ───────────────────────────────────────────────────

    @property
    def name(self) -> str:
        return self._spec.name

    def register(self, ctx: PluginContext) -> None:
        """Spawn the plugin subprocess and collect its registrations."""
        from tinycore.plugin import runner

        parent_conn, child_conn = mp.Pipe(duplex=True)

        self._proc = mp.Process(
            target=runner.run,
            args=(child_conn, self._spec.module, self._spec.cls, sys.path),
            daemon=True,
            name=f"plugin-{self._spec.name}",
        )
        self._proc.start()
        child_conn.close()   # host does not use the child end
        self._conn = parent_conn

        # ── Hello ─────────────────────────────────────────────────────────
        msg = parent_conn.recv()
        if msg.get("type") != "hello":
            raise RuntimeError(f"Plugin '{self._spec.name}': expected hello, got {msg}")
        if msg["name"] != self._spec.name:
            raise RuntimeError(
                f"Plugin name mismatch: spec='{self._spec.name}' plugin='{msg['name']}'. "
                f"Update PluginSpec to use name='{msg['name']}'."
            )

        # ── Collect registrations ─────────────────────────────────────────
        while True:
            msg = parent_conn.recv()
            if msg["type"] == "register.done":
                break
            self._dispatch(msg, ctx)

    def start(self) -> None:
        if self._conn:
            self._conn.send({"type": "start"})
            self._conn.recv()   # wait for ack

    def stop(self) -> None:
        if self._conn:
            self._conn.send({"type": "stop"})
            self._conn.recv()   # wait for ack
            if self._proc:
                self._proc.join(timeout=5)
                if self._proc.is_alive():
                    self._proc.terminate()
            self._conn = None

    # ── Internal ──────────────────────────────────────────────────────────

    def _dispatch(self, msg: dict, ctx: PluginContext) -> None:
        """Route a registration message from the subprocess to the host registries."""
        t = msg["type"]

        if t == "settings.register":
            ctx.settings.register(msg["spec"])

        elif t == "widgets.register":
            ctx.widgets.register(msg["spec"])

        elif t == "editors.register":
            ctx.editors.register(msg["spec"])

        elif t == "loaders.register":
            ctx.loaders.register(msg["key"], msg["filename"], msg.get("defaults"))

        elif t == "loaders.load_all":
            ctx.loaders.load_all(ctx.config)

        elif t == "loaders.load":
            ctx.loaders.load(ctx.config, msg["key"])

        elif t == "loaders.save":
            ctx.loaders.save(ctx.config, msg["key"])
