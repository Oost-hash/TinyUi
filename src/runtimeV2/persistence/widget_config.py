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

"""Widget config store for runtime V2 persistence."""

from __future__ import annotations

from collections.abc import Callable
from uuid import UUID, uuid5

from runtimeV2.persistence.contracts import WidgetInstanceConfig
from runtimeV2.persistence.overlay_index import OverlayIndexStore
from runtimeV2.persistence.repository import PersistenceRepository

WIDGET_INSTANCE_NAMESPACE = UUID("a3deceeb-d97c-4e55-b087-c7c436cc5268")
WIDGET_VISIBILITY_SINGLETON_ID = "widget_visibility"


class WidgetConfigStore:
    """Store widget configuration values."""

    def __init__(
        self,
        repository: PersistenceRepository,
        overlay_repository: Callable[[str], PersistenceRepository] | None = None,
        overlay_index: OverlayIndexStore | None = None,
    ) -> None:
        self._repository = repository
        self._overlay_repository = overlay_repository
        self._overlay_index = overlay_index

    def load_for_overlay(self, overlay_id: str) -> list[WidgetInstanceConfig]:
        """Load widget configuration for an overlay."""

        documents = self._repository_for_overlay(overlay_id).list_documents("widget_instances")
        return [
            WidgetInstanceConfig.from_dict(document)
            for document in documents
        ]

    def save_for_overlay(self, overlay_id: str, configs: list[WidgetInstanceConfig]) -> None:
        """Save widget configuration for an overlay."""

        repository = self._repository_for_overlay(overlay_id)
        for document in repository.list_documents("widget_instances"):
            widget_instance_id = document.get("widget_instance_id")
            if isinstance(widget_instance_id, str):
                repository.delete_one("widget_instances", {"widget_instance_id": widget_instance_id})
        for config in configs:
            widget_instance_id = self._widget_instance_uuid(overlay_id, config.widget_id)
            repository.write_one(
                "widget_instances",
                {"widget_instance_id": widget_instance_id},
                {
                    "widget_id": config.widget_id,
                    "enabled": config.enabled,
                    "position": [config.position[0], config.position[1]],
                    "values": config.values,
                },
            )

    def get_widget(self, overlay_id: str, widget_id: str) -> WidgetInstanceConfig | None:
        """Return one widget config."""

        document = self._repository_for_overlay(overlay_id).read_one(
            "widget_instances",
            {"widget_instance_id": self._widget_instance_uuid(overlay_id, widget_id)},
        )
        if document is None:
            return None
        return WidgetInstanceConfig.from_dict(document)

    def set_widget_enabled(self, overlay_id: str, widget_id: str, enabled: bool) -> bool:
        """Set widget enabled state."""

        config = self.get_widget(overlay_id, widget_id) or WidgetInstanceConfig(widget_id=widget_id)
        config.enabled = enabled
        self._save_one(overlay_id, config)
        return True

    def set_widget_position(self, overlay_id: str, widget_id: str, x: int, y: int) -> bool:
        """Set widget position."""

        config = self.get_widget(overlay_id, widget_id) or WidgetInstanceConfig(widget_id=widget_id)
        config.position = (x, y)
        self._save_one(overlay_id, config)
        return True

    def set_widget_values(self, overlay_id: str, widget_id: str, values: dict[str, object]) -> bool:
        """Set widget config values."""

        config = self.get_widget(overlay_id, widget_id) or WidgetInstanceConfig(widget_id=widget_id)
        config.values.update(values)
        self._save_one(overlay_id, config)
        return True

    def reset_widget_values(self, overlay_id: str, widget_id: str) -> bool:
        """Reset widget config values to empty."""

        config = self.get_widget(overlay_id, widget_id)
        if config is None:
            return False
        config.values = {}
        self._save_one(overlay_id, config)
        return True

    def get_global_visible(self) -> bool:
        """Return the global widget visibility flag."""

        data = self._repository.read_one(
            "widget_visibility",
            {"singleton_id": WIDGET_VISIBILITY_SINGLETON_ID},
        )
        if data is None:
            return False
        return bool(data.get("global_visible", False))

    def set_global_visible(self, visible: bool) -> None:
        """Store the global widget visibility flag."""

        self._repository.write_one(
            "widget_visibility",
            {"singleton_id": WIDGET_VISIBILITY_SINGLETON_ID},
            {"global_visible": visible},
        )

    def _save_one(self, overlay_id: str, config: WidgetInstanceConfig) -> None:
        widget_instance_id = self._widget_instance_uuid(overlay_id, config.widget_id)
        self._repository_for_overlay(overlay_id).write_one(
            "widget_instances",
            {"widget_instance_id": widget_instance_id},
            {
                "widget_id": config.widget_id,
                "enabled": config.enabled,
                "position": [config.position[0], config.position[1]],
                "values": config.values,
            },
        )

    def _repository_for_overlay(self, overlay_id: str) -> PersistenceRepository:
        if self._overlay_repository is None:
            return self._repository
        return self._overlay_repository(self._overlay_store_uuid(overlay_id))

    def _overlay_store_uuid(self, overlay_id: str) -> str:
        if self._overlay_index is None:
            if self._overlay_repository is not None:
                raise RuntimeError("Overlay repository routing requires an overlay index.")
            return overlay_id
        record = self._overlay_index.overlay_by_id(overlay_id)
        if record is None:
            raise KeyError(f"Overlay is not registered in overlay_index: {overlay_id}")
        return record.overlay_uuid

    def _widget_instance_uuid(self, overlay_id: str, widget_id: str) -> str:
        return widget_instance_uuid(self._overlay_store_uuid(overlay_id), widget_id)


def widget_instance_uuid(overlay_id: str, widget_id: str) -> str:
    """Return a stable UUID for a widget instance."""

    return str(uuid5(WIDGET_INSTANCE_NAMESPACE, f"{overlay_id}:{widget_id}"))
