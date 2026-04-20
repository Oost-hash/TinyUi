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

"""Persistence schema registry for runtime V2."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class PersistenceScope(StrEnum):
    """Scope for a persistent document."""

    APP = "app"
    NAMESPACE = "namespace"
    SINGLETON = "singleton"
    WIDGET_INSTANCE = "widget_instance"
    WIDGET_TYPE = "widget_type"
    PLUGIN = "plugin"
    CONNECTOR = "connector"


@dataclass(frozen=True)
class PersistenceSchema:
    """Registered persistent document shape."""

    name: str
    owner_domain: str
    collection: str
    scope: PersistenceScope
    version: int
    key_fields: tuple[str, ...]
    required_fields: tuple[str, ...] = ()
    default_document: dict[str, Any] = field(default_factory=dict)


class PersistenceRegistry:
    """Registry of domain-owned persistence schemas."""

    def __init__(self) -> None:
        self._schemas: dict[str, PersistenceSchema] = {}

    def register_schema(self, schema: PersistenceSchema, *, registering_domain: str) -> None:
        """Register one persistence schema for a domain."""

        if schema.owner_domain != registering_domain:
            raise ValueError(
                f"Schema '{schema.name}' owner '{schema.owner_domain}' "
                f"does not match registering domain '{registering_domain}'"
            )
        if schema.name in self._schemas:
            raise ValueError(f"Persistence schema already registered: {schema.name}")
        if schema.version < 1:
            raise ValueError(f"Persistence schema '{schema.name}' must start at version 1")
        if not schema.key_fields:
            raise ValueError(f"Persistence schema '{schema.name}' must define key fields")
        self._schemas[schema.name] = schema

    def schema(self, name: str) -> PersistenceSchema:
        """Return one registered schema."""

        try:
            return self._schemas[name]
        except KeyError as exc:
            raise KeyError(f"Unknown persistence schema: {name}") from exc

    def schemas(self) -> tuple[PersistenceSchema, ...]:
        """Return all registered schemas."""

        return tuple(self._schemas.values())
