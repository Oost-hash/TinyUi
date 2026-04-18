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

"""Persistence backend exports."""

from pathlib import Path

from runtimeV2.persistence.backends.contracts import PersistenceBackend
from runtimeV2.persistence.backends.json_test import JsonTestPersistenceBackend
from runtimeV2.persistence.backends.sqlite_document import SQLiteDocumentBackend
from runtimeV2.persistence.contracts import BootstrapConfig


def create_persistence_backend(config: BootstrapConfig, *, sqlite_path: Path | None = None) -> PersistenceBackend:
    """Create the configured persistence backend."""

    if config.backend == "sqlite":
        if sqlite_path is None:
            raise RuntimeError("SQLite persistence requires a database path.")
        return SQLiteDocumentBackend(sqlite_path)
    if config.backend == "json":
        return JsonTestPersistenceBackend()
    raise ValueError(f"Unsupported persistence backend: {config.backend}")


__all__ = [
    "JsonTestPersistenceBackend",
    "PersistenceBackend",
    "SQLiteDocumentBackend",
    "create_persistence_backend",
]
