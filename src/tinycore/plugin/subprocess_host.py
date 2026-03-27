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
"""SubprocessPlugin — host-side wrapper for a subprocess-isolated consumer plugin.

The plugin module is never imported in the host process. All communication
goes through a multiprocessing.Pipe (pickle-serialised).
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tinycore.plugin.context import PluginContext
    from tinycore.plugin.spec import ConsumerRuntimeSpec
    from tinycore.runtime.process_supervisor import ProcessSupervisor, SpawnedProcessHandle


class SubprocessPlugin:
    """Host-side manager for a consumer plugin running in an isolated subprocess.

    Implements the Plugin protocol (name / register / start / stop) so it
    drops in wherever a regular plugin is expected.
    """

    def __init__(self, spec: ConsumerRuntimeSpec, *, process_supervisor: "ProcessSupervisor") -> None:
        self._spec = spec
        self._process_supervisor = process_supervisor
        self._handle: SpawnedProcessHandle | None = None

    # ── Plugin protocol ───────────────────────────────────────────────────

    @property
    def name(self) -> str:
        return self._spec.name

    @property
    def pid(self) -> int | None:
        """Return the child PID when the subprocess has been spawned."""
        return self._handle.pid if self._handle is not None else None

    def register(self, ctx: PluginContext) -> None:
        """Spawn the plugin subprocess and collect its registrations."""
        self._handle = self._process_supervisor.spawn_consumer_plugin(
            self._spec,
            extra_paths=list(sys.path),
        )
        conn = self._handle.conn

        try:
            # ── Hello ─────────────────────────────────────────────────────────
            msg = conn.recv()
            if msg.get("type") != "hello":
                raise RuntimeError(f"Plugin '{self._spec.name}': expected hello, got {msg}")
            if msg["name"] != self._spec.name:
                raise RuntimeError(
                    f"Plugin name mismatch: spec='{self._spec.name}' plugin='{msg['name']}'. "
                    f"Update ConsumerRuntimeSpec to use name='{msg['name']}'."
                )

            # ── Collect registrations ─────────────────────────────────────────
            while True:
                msg = conn.recv()
                if msg["type"] == "register.done":
                    break
                self._dispatch(msg, ctx)
            self._process_supervisor.mark_running(self._handle.unit_id)
        except Exception:
            handle = self._handle
            if handle is not None:
                self._process_supervisor.mark_failed(handle.unit_id)
                try:
                    self._process_supervisor.stop(handle, timeout=0.5)
                except Exception:
                    try:
                        handle.conn.close()
                    finally:
                        if handle.process.is_alive():
                            handle.process.terminate()
                            handle.process.join(timeout=0.5)
                finally:
                    self._handle = None
            raise

    def start(self) -> None:
        if self._handle is not None:
            self._handle.conn.send({"type": "start"})
            self._handle.conn.recv()   # wait for ack

    def stop(self) -> None:
        if self._handle is None:
            return

        handle = self._handle
        failed = False
        try:
            handle.conn.send({"type": "stop"})
            handle.conn.recv()   # wait for ack
        except Exception:
            failed = True
            self._process_supervisor.mark_failed(handle.unit_id)
            raise
        finally:
            try:
                self._process_supervisor.stop(handle)
                if failed:
                    self._process_supervisor.mark_failed(handle.unit_id)
            finally:
                self._handle = None

    # ── Internal ──────────────────────────────────────────────────────────

    def _dispatch(self, msg: dict, ctx: PluginContext) -> None:
        """Route a registration message from the subprocess to the host registries."""
        t = msg["type"]

        if t == "settings.register":
            ctx.settings.register(msg["spec"])

        elif t == "editors.register":
            ctx.editors.register(msg["spec"])

        elif t == "loaders.register":
            ctx.config.register(msg["key"], msg["filename"], msg.get("defaults"))

        elif t == "loaders.load_all":
            ctx.config.load_all()

        elif t == "loaders.load":
            ctx.config.load(msg["key"])

        elif t == "loaders.save":
            ctx.config.save(msg["key"])
