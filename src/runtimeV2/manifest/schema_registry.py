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

"""Schema registry for runtime V2 plugin manifests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ManifestSchemaRecord:
    """One manifest schema registered by an owning domain."""

    name: str
    owner_domain: str
    schema_type: type[Any]


class ManifestSchemaRegistry:
    """Registry of manifest schemas owned by runtime V2 domains."""

    def __init__(self) -> None:
        self._records: dict[str, ManifestSchemaRecord] = {}

    def register_schema(self, name: str, *, owner_domain: str, schema_type: type[Any]) -> None:
        """Register one manifest schema contract."""

        self._records[name] = ManifestSchemaRecord(
            name=name,
            owner_domain=owner_domain,
            schema_type=schema_type,
        )

    def records(self) -> list[ManifestSchemaRecord]:
        """Return all registered schema records."""

        return list(self._records.values())

    def record(self, name: str) -> ManifestSchemaRecord:
        """Return one registered schema record."""

        try:
            return self._records[name]
        except KeyError as exc:
            raise KeyError(f"Manifest schema is not registered: {name}") from exc
