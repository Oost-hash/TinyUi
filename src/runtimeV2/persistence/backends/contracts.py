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

"""Persistence backend contracts."""

from __future__ import annotations

from typing import Any, Protocol


class PersistenceBackend(Protocol):
    """Storage boundary used by the persistence repository."""

    name: str

    def read_one(self, collection: str, key: dict[str, Any]) -> dict[str, Any] | None:
        """Read one persisted document."""
        ...

    def list_documents(self, collection: str, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Read persisted documents matching filters."""
        ...

    def write_one(self, collection: str, key: dict[str, Any], document: dict[str, Any]) -> None:
        """Write one persisted document."""
        ...

    def delete_one(self, collection: str, key: dict[str, Any]) -> None:
        """Delete one persisted document."""
        ...

    def delete_many(self, collection: str, filters: dict[str, Any]) -> None:
        """Delete persisted documents matching filters."""
        ...

    def close(self) -> None:
        """Close backend resources."""
        ...
