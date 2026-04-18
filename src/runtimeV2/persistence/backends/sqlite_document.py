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

"""SQLite document persistence backend."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


class SQLiteDocumentBackend:
    """SQLite-backed document persistence backend."""

    name = "sqlite"

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        database_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(database_path)
        self._connection.row_factory = sqlite3.Row
        self._ensure_schema()

    def read_one(self, collection: str, key: dict[str, Any]) -> dict[str, Any] | None:
        """Read one persisted document."""

        row = self._connection.execute(
            """
            select document_json
            from persistence_documents
            where collection = ? and key_json = ?
            """,
            (collection, self._key_json(key)),
        ).fetchone()
        if row is None:
            return None
        return dict(json.loads(str(row["document_json"])))

    def list_documents(self, collection: str, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Read persisted documents matching filters."""

        filters = filters or {}
        rows = self._connection.execute(
            """
            select document_json
            from persistence_documents
            where collection = ?
            """,
            (collection,),
        ).fetchall()
        documents = [dict(json.loads(str(row["document_json"]))) for row in rows]
        return [
            document
            for document in documents
            if all(document.get(field) == value for field, value in filters.items())
        ]

    def write_one(self, collection: str, key: dict[str, Any], document: dict[str, Any]) -> None:
        """Write one persisted document."""

        self._connection.execute(
            """
            insert into persistence_documents(collection, key_json, document_json, updated_at)
            values (?, ?, json(?), datetime('now'))
            on conflict(collection, key_json) do update set
                document_json = excluded.document_json,
                updated_at = excluded.updated_at
            """,
            (
                collection,
                self._key_json(key),
                json.dumps(document, ensure_ascii=False, sort_keys=True),
            ),
        )
        self._connection.commit()

    def delete_one(self, collection: str, key: dict[str, Any]) -> None:
        """Delete one persisted document."""

        self._connection.execute(
            """
            delete from persistence_documents
            where collection = ? and key_json = ?
            """,
            (collection, self._key_json(key)),
        )
        self._connection.commit()

    def delete_many(self, collection: str, filters: dict[str, Any]) -> None:
        """Delete persisted documents matching filters."""

        rows = self._connection.execute(
            """
            select key_json, document_json
            from persistence_documents
            where collection = ?
            """,
            (collection,),
        ).fetchall()
        for row in rows:
            document = dict(json.loads(str(row["document_json"])))
            if not all(document.get(field) == value for field, value in filters.items()):
                continue
            self._connection.execute(
                """
                delete from persistence_documents
                where collection = ? and key_json = ?
                """,
                (collection, str(row["key_json"])),
            )
        self._connection.commit()

    def close(self) -> None:
        """Close the SQLite connection."""

        self._connection.close()

    def _ensure_schema(self) -> None:
        self._connection.execute(
            """
            create table if not exists persistence_documents (
                collection text not null,
                key_json text not null,
                document_json text not null check (json_valid(document_json)),
                updated_at text not null,
                primary key (collection, key_json)
            )
            """
        )
        self._connection.execute(
            """
            create index if not exists persistence_documents_collection_idx
            on persistence_documents(collection)
            """
        )
        self._connection.commit()

    def _key_json(self, key: dict[str, Any]) -> str:
        return json.dumps(key, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
