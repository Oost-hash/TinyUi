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

"""JSON backend for tests and migration helpers."""

from __future__ import annotations

from typing import Any


class JsonTestPersistenceBackend:
    """In-memory document backend kept for tests and migration scaffolding."""

    name = "json_test"

    def __init__(self) -> None:
        self._documents: dict[str, dict[str, dict[str, Any]]] = {}

    def read_one(self, collection: str, key: dict[str, Any]) -> dict[str, Any] | None:
        """Read one persisted document."""

        document = self._documents.get(collection, {}).get(self._key(key))
        return dict(document) if document is not None else None

    def list_documents(self, collection: str, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Read persisted documents matching filters."""

        filters = filters or {}
        return [
            dict(document)
            for document in self._documents.get(collection, {}).values()
            if all(document.get(field) == value for field, value in filters.items())
        ]

    def write_one(self, collection: str, key: dict[str, Any], document: dict[str, Any]) -> None:
        """Write one persisted document."""

        self._documents.setdefault(collection, {})[self._key(key)] = dict(document)

    def delete_one(self, collection: str, key: dict[str, Any]) -> None:
        """Delete one persisted document."""

        self._documents.get(collection, {}).pop(self._key(key), None)

    def delete_many(self, collection: str, filters: dict[str, Any]) -> None:
        """Delete persisted documents matching filters."""

        documents = self._documents.get(collection, {})
        for key, document in list(documents.items()):
            if all(document.get(field) == value for field, value in filters.items()):
                del documents[key]

    def close(self) -> None:
        """Close backend resources."""

        return None

    def _key(self, key: dict[str, Any]) -> str:
        return repr(sorted(key.items()))
