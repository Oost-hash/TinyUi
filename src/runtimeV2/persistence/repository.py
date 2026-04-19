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

"""Schema-aware repository for runtime V2 persistence."""

from __future__ import annotations

from typing import Any

from runtimeV2.persistence.backends import PersistenceBackend
from runtimeV2.persistence.registry import PersistenceRegistry, PersistenceSchema


class PersistenceRepository:
    """Read and write persisted documents through registered schemas."""

    def __init__(self, registry: PersistenceRegistry, backend: PersistenceBackend) -> None:
        self._registry = registry
        self._backend = backend

    def read_one(self, schema_name: str, key: dict[str, Any]) -> dict[str, Any] | None:
        """Read one document for a registered schema."""

        schema = self._registry.schema(schema_name)
        self._validate_key(schema, key)
        return self._backend.read_one(schema.collection, key)

    def list_documents(self, schema_name: str, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """List documents for a registered schema."""

        schema = self._registry.schema(schema_name)
        if filters is not None:
            self._validate_filter(schema, filters)
        return self._backend.list_documents(schema.collection, filters)

    def write_one(self, schema_name: str, key: dict[str, Any], document: dict[str, Any]) -> None:
        """Write one document for a registered schema."""

        schema = self._registry.schema(schema_name)
        self._validate_key(schema, key)
        prepared = self._prepare_document(schema, key, document)
        self._backend.write_one(schema.collection, key, prepared)

    def delete_one(self, schema_name: str, key: dict[str, Any]) -> None:
        """Delete one document for a registered schema."""

        schema = self._registry.schema(schema_name)
        self._validate_key(schema, key)
        self._backend.delete_one(schema.collection, key)

    def delete_many(self, schema_name: str, filters: dict[str, Any]) -> None:
        """Delete documents matching filters for a registered schema."""

        schema = self._registry.schema(schema_name)
        self._validate_filter(schema, filters)
        self._backend.delete_many(schema.collection, filters)

    def _prepare_document(
        self,
        schema: PersistenceSchema,
        key: dict[str, Any],
        document: dict[str, Any],
    ) -> dict[str, Any]:
        prepared = {
            **schema.default_document,
            **document,
            **key,
            "schema_name": schema.name,
            "schema_version": schema.version,
            "owner_domain": schema.owner_domain,
        }
        missing = [
            field
            for field in schema.required_fields
            if field not in prepared
        ]
        if missing:
            raise ValueError(f"Document for schema '{schema.name}' misses required fields: {', '.join(missing)}")
        return prepared

    def _validate_key(self, schema: PersistenceSchema, key: dict[str, Any]) -> None:
        key_fields = set(key)
        expected_fields = set(schema.key_fields)
        if key_fields != expected_fields:
            missing = sorted(expected_fields - key_fields)
            extra = sorted(key_fields - expected_fields)
            details: list[str] = []
            if missing:
                details.append(f"missing: {', '.join(missing)}")
            if extra:
                details.append(f"extra: {', '.join(extra)}")
            raise ValueError(f"Invalid key for schema '{schema.name}' ({'; '.join(details)})")

    def _validate_filter(self, schema: PersistenceSchema, filters: dict[str, Any]) -> None:
        allowed = set(schema.key_fields)
        unknown = sorted(set(filters) - allowed)
        if unknown:
            raise ValueError(f"Invalid filter for schema '{schema.name}' (unknown: {', '.join(unknown)})")
