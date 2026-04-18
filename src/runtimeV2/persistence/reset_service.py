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

"""Persistence reset and delete operations."""

from __future__ import annotations

from runtimeV2.persistence.overlay_index import OverlayIndexStore
from runtimeV2.persistence.store_provider import PersistenceStoreProvider
from runtimeV2.persistence.widget_config import WidgetConfigStore


class PersistenceResetService:
    """Coordinate persistence reset and delete operations."""

    def __init__(
        self,
        *,
        overlay_index: OverlayIndexStore,
        store_provider: PersistenceStoreProvider,
        widget_config: WidgetConfigStore,
    ) -> None:
        self._overlay_index = overlay_index
        self._store_provider = store_provider
        self._widget_config = widget_config

    def reset_widget_values(self, overlay_id: str, widget_id: str) -> bool:
        """Reset one widget document's values."""

        return self._widget_config.reset_widget_values(overlay_id, widget_id)

    def reset_overlay(self, overlay_id: str) -> None:
        """Delete one overlay store while keeping its app-owned index record."""

        record = self._overlay_record(overlay_id)
        self._store_provider.delete_overlay_store(record.overlay_uuid)

    def delete_overlay(self, overlay_id: str) -> None:
        """Delete one overlay store and remove its app-owned index record."""

        record = self._overlay_record(overlay_id)
        self._store_provider.delete_overlay_store(record.overlay_uuid)
        self._overlay_index.remove_overlay(record.overlay_uuid)

    def factory_reset(self) -> None:
        """Delete all persistence database files."""

        self._store_provider.delete_all_stores()

    def _overlay_record(self, overlay_id: str):
        record = self._overlay_index.overlay_by_id(overlay_id)
        if record is None:
            raise KeyError(f"Overlay is not registered in overlay_index: {overlay_id}")
        return record
