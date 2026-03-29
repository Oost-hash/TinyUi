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

"""Runtime-owned subprocess execution for plugin participation."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tinyplugins.spec import ConsumerRuntimeSpec

if TYPE_CHECKING:
    from tinyplugins.context import PluginContext
    from tinycore.runtime.process_supervisor import ProcessSupervisor, SpawnedProcessHandle


class SubprocessPlugin:
    """Host-side subprocess execution for one plugin-declared subprocess runtime."""

    def __init__(self, spec: ConsumerRuntimeSpec, *, process_supervisor: "ProcessSupervisor") -> None:
        self._spec = spec
        self._process_supervisor = process_supervisor
        self._handle: SpawnedProcessHandle | None = None

    @property
    def name(self) -> str:
        return self._spec.name

    @property
    def pid(self) -> int | None:
        return self._handle.pid if self._handle is not None else None

    def register(self, ctx: PluginContext) -> None:
        self._handle = self._process_supervisor.spawn_plugin_subprocess(
            self._spec,
            extra_paths=list(sys.path),
        )
        conn = self._handle.conn

        try:
            msg = conn.recv()
            if msg.get("type") != "hello":
                raise RuntimeError(f"Plugin '{self._spec.name}': expected hello, got {msg}")
            if msg["name"] != self._spec.name:
                raise RuntimeError(
                    f"Plugin name mismatch: spec='{self._spec.name}' plugin='{msg['name']}'. "
                    f"Update ConsumerRuntimeSpec to use name='{msg['name']}'."
                )

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
            self._handle.conn.recv()

    def stop(self) -> None:
        if self._handle is None:
            return

        handle = self._handle
        failed = False
        try:
            handle.conn.send({"type": "stop"})
            handle.conn.recv()
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

    def _dispatch(self, msg: dict, ctx: PluginContext) -> None:
        t = msg["type"]

        if t == "settings.register":
            ctx.settings.register(msg["spec"])
        elif t == "editors.register":
            ctx.editors.register(msg["spec"])
        elif t == "config.register":
            ctx.config.register(msg["key"], msg["filename"], msg.get("defaults"))
        elif t == "config.load_all":
            ctx.config.load_all()
        elif t == "config.load":
            ctx.config.load(msg["key"])
        elif t == "config.save":
            ctx.config.save(msg["key"])
