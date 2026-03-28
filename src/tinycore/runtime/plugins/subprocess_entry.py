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

"""Runtime-owned subprocess entrypoint for plugin participation."""

from __future__ import annotations

import importlib
import sys
from multiprocessing.connection import Connection

from tinycore.plugin.runtime_loader import ensure_runtime_import_path


class _ProxySettings:
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    def register(self, spec) -> None:
        self._conn.send({"type": "settings.register", "spec": spec})

    def get(self, key: str):
        raise NotImplementedError("settings.get is not available during register phase")

    def set(self, key: str, value) -> None:
        raise NotImplementedError("settings.set is not available during register phase")


class _ProxyConfig:
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    def register(self, key: str, filename: str, defaults: dict | None = None) -> None:
        self._conn.send(
            {
                "type": "config.register",
                "key": key,
                "filename": filename,
                "defaults": defaults,
            }
        )

    def load_all(self) -> None:
        self._conn.send({"type": "config.load_all"})

    def load(self, key: str) -> None:
        self._conn.send({"type": "config.load", "key": key})

    def save(self, key: str) -> None:
        self._conn.send({"type": "config.save", "key": key})

    def get(self, key: str, default=None):
        raise NotImplementedError("config.get is not available during register phase")

    def set(self, key: str, value) -> None:
        raise NotImplementedError("config.set is not available during register phase")


class _ProxyEditors:
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    def register(self, spec) -> None:
        self._conn.send({"type": "editors.register", "spec": spec})


class _ProxyExports:
    """Read-only view of declared export requirements inside the subprocess."""

    def __init__(self, required: tuple[str, ...]) -> None:
        self._required = required

    def required(self) -> tuple[str, ...]:
        return self._required

    def get(self, export_name: str):
        raise NotImplementedError("export resolution is not available during register phase")

    def require(self, export_name: str):
        raise NotImplementedError("export resolution is not available during register phase")


class _ProxyContext:
    """Proxy PluginContext inside the subprocess."""

    def __init__(self, conn: Connection, plugin_name: str, requires: tuple[str, ...]) -> None:
        self.name = plugin_name
        self.settings = _ProxySettings(conn)
        self.config = _ProxyConfig(conn)
        self.editors = _ProxyEditors(conn)
        self.exports = _ProxyExports(requires)


def run(
    conn: Connection,
    module_path: str,
    class_name: str,
    requires: tuple[str, ...],
    artifact_path: str | None,
    extra_paths: list[str],
) -> None:
    """Load and run one plugin subprocess runtime."""
    for path in extra_paths:
        if path not in sys.path:
            sys.path.insert(0, path)

    ensure_runtime_import_path(artifact_path)
    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)
    plugin = cls()

    ctx = _ProxyContext(conn, plugin.name, requires)
    conn.send({"type": "hello", "name": plugin.name})
    plugin.register(ctx)
    conn.send({"type": "register.done"})

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
