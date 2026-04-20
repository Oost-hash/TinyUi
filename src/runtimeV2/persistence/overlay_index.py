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

"""Overlay store index persisted in the app store."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any
from uuid import UUID, uuid5

from runtimeV2.persistence.repository import PersistenceRepository

TINYUI_OVERLAY_NAMESPACE = UUID("6459cd55-6a8d-4df0-bbc0-f9d6771b1f10")


@dataclass(frozen=True)
class OverlayIndexRecord:
    """App-owned metadata for one overlay store."""

    overlay_uuid: str
    plugin_id: str
    overlay_id: str
    enabled: bool = True

    def to_document(self) -> dict[str, object]:
        """Convert the record to persisted document data."""

        return {
            "plugin_id": self.plugin_id,
            "overlay_id": self.overlay_id,
            "enabled": self.enabled,
        }

    @classmethod
    def from_document(cls, document: dict[str, object]) -> "OverlayIndexRecord":
        """Build a record from persisted document data."""

        return cls(
            overlay_uuid=str(UUID(str(document["overlay_uuid"]))),
            plugin_id=str(document.get("plugin_id", "")),
            overlay_id=str(document.get("overlay_id", "")),
            enabled=bool(document.get("enabled", True)),
        )


class OverlayIndexStore:
    """Store the app-owned index of known overlay stores."""

    def __init__(self, repository: PersistenceRepository) -> None:
        self._repository = repository

    def register_overlay(
        self,
        *,
        plugin_id: str,
        overlay_id: str,
        overlay_uuid: str | None = None,
        enabled: bool = True,
    ) -> OverlayIndexRecord:
        """Register or update one overlay store metadata record."""

        record = OverlayIndexRecord(
            overlay_uuid=str(UUID(overlay_uuid)) if overlay_uuid is not None else overlay_store_uuid(
                plugin_id=plugin_id,
                overlay_id=overlay_id,
            ),
            plugin_id=plugin_id,
            overlay_id=overlay_id,
            enabled=enabled,
        )
        self._repository.write_one(
            "overlay_index",
            {"overlay_uuid": record.overlay_uuid},
            record.to_document(),
        )
        return record

    def register_manifest_overlays(self, declarations: Mapping[str, Any]) -> list[OverlayIndexRecord]:
        """Register manifest-declared overlays and return their records."""

        return [
            self.register_overlay(
                plugin_id=plugin_id,
                overlay_id=plugin_id,
            )
            for plugin_id in declarations
        ]

    def overlay(self, overlay_uuid: str) -> OverlayIndexRecord | None:
        """Return one overlay metadata record."""

        document = self._repository.read_one(
            "overlay_index",
            {"overlay_uuid": str(UUID(overlay_uuid))},
        )
        if document is None:
            return None
        return OverlayIndexRecord.from_document(document)

    def overlays(self) -> list[OverlayIndexRecord]:
        """Return all known overlay metadata records."""

        return [
            OverlayIndexRecord.from_document(document)
            for document in self._repository.list_documents("overlay_index")
        ]

    def overlay_by_id(self, overlay_id: str) -> OverlayIndexRecord | None:
        """Return one overlay metadata record by runtime overlay id."""

        for record in self.overlays():
            if record.overlay_id == overlay_id:
                return record
        return None

    def remove_overlay(self, overlay_uuid: str) -> None:
        """Remove one overlay metadata record."""

        self._repository.delete_one(
            "overlay_index",
            {"overlay_uuid": str(UUID(overlay_uuid))},
        )


def overlay_store_uuid(*, plugin_id: str, overlay_id: str) -> str:
    """Return the stable store UUID for one plugin overlay."""

    return str(uuid5(TINYUI_OVERLAY_NAMESPACE, f"{plugin_id}:{overlay_id}"))
