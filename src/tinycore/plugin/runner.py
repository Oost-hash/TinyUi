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
"""Plugin subprocess runner.

This module is the entry point for plugin subprocesses. It runs inside the
isolated process — the host never calls these functions directly.

Protocol (over multiprocessing.Pipe, pickle-serialised):
  subprocess → host:
    {"type": "hello",            "name": <str>}
    {"type": "settings.register","spec": <SettingsSpec>}
    {"type": "editors.register", "spec": <EditorSpec>}
    {"type": "loaders.register", "key": <str>, "filename": <str>, "defaults": <dict|None>}
    {"type": "loaders.load_all"}
    {"type": "register.done"}
    {"type": "ack"}

  host → subprocess:
    {"type": "start"}
    {"type": "stop"}
"""

from __future__ import annotations

import importlib
import sys
from multiprocessing.connection import Connection

from .runtime_loader import ensure_runtime_import_path

# ── Proxy context — used inside the subprocess ────────────────────────────────

class _ProxySettings:
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    def register(self, spec) -> None:
        self._conn.send({"type": "settings.register", "spec": spec})

    def get(self, key: str):
        raise NotImplementedError("settings.get is not available during register phase")

    def set(self, key: str, value) -> None:
        raise NotImplementedError("settings.set is not available during register phase")


class _ProxyLoaders:
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    def register(self, key: str, filename: str, defaults: dict | None = None) -> None:
        self._conn.send({
            "type": "loaders.register",
            "key": key,
            "filename": filename,
            "defaults": defaults,
        })

    def load_all(self) -> None:
        self._conn.send({"type": "loaders.load_all"})

    def load(self, key: str) -> None:
        self._conn.send({"type": "loaders.load", "key": key})

    def save(self, key: str) -> None:
        self._conn.send({"type": "loaders.save", "key": key})


class _ProxyEditors:
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    def register(self, spec) -> None:
        self._conn.send({"type": "editors.register", "spec": spec})


class _ProxyCapabilities:
    """Read-only view of declared requirements inside the subprocess."""

    def __init__(self, required: tuple[str, ...]) -> None:
        self._required = required

    def required(self) -> tuple[str, ...]:
        return self._required

    def get(self, capability: str):
        raise NotImplementedError("capability resolution is not available during register phase")

    def require(self, capability: str):
        raise NotImplementedError("capability resolution is not available during register phase")


class _ProxyContext:
    """Proxy PluginContext inside the subprocess.

    Implements the same surface as PluginContext — every call is forwarded
    to the host via the pipe. The plugin code sees no difference.
    """

    def __init__(self, conn: Connection, plugin_name: str, requires: tuple[str, ...]) -> None:
        self.name      = plugin_name
        self.settings  = _ProxySettings(conn)
        self.loaders   = _ProxyLoaders(conn)
        self.editors   = _ProxyEditors(conn)
        self.capabilities = _ProxyCapabilities(requires)


# ── Entry point — called by multiprocessing.Process ───────────────────────────

def run(
    conn: Connection,
    module_path: str,
    class_name: str,
    requires: tuple[str, ...],
    artifact_path: str | None,
    extra_paths: list[str],
) -> None:
    """Load and run a plugin inside a subprocess.

    Args:
        conn:        Child-side Pipe connection to the host.
        module_path: Importable module path, e.g. "plugins.demo".
        class_name:  Plugin class name, e.g. "DemoPlugin".
        extra_paths: sys.path entries from the parent to ensure imports work.
    """
    for p in extra_paths:
        if p not in sys.path:
            sys.path.insert(0, p)

    ensure_runtime_import_path(artifact_path)
    mod = importlib.import_module(module_path)
    cls = getattr(mod, class_name)
    plugin = cls()

    ctx = _ProxyContext(conn, plugin.name, requires)

    # ── Registration phase ────────────────────────────────────────────────
    conn.send({"type": "hello", "name": plugin.name})
    plugin.register(ctx)
    conn.send({"type": "register.done"})

    # ── Lifecycle loop ────────────────────────────────────────────────────
    while True:
        try:
            msg = conn.recv()
        except (BrokenPipeError, EOFError):
            break
        if msg["type"] == "start":
            plugin.start()
            conn.send({"type": "ack"})
        elif msg["type"] == "stop":
            plugin.stop()
            try:
                conn.send({"type": "ack"})
            except (BrokenPipeError, EOFError):
                pass
            break
