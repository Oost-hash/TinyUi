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

"""Overlay-owned document stores."""

from __future__ import annotations

from collections.abc import Callable

from runtimeV2.persistence.overlay_index import OverlayIndexStore
from runtimeV2.persistence.repository import PersistenceRepository

OVERLAY_THEME_SINGLETON_ID = "overlay_theme"
OVERLAY_LAYOUT_SINGLETON_ID = "overlay_layout"


class _OverlayRepositoryResolver:
    """Resolve runtime overlay ids to overlay-bound repositories."""

    def __init__(
        self,
        *,
        overlay_index: OverlayIndexStore,
        overlay_repository: Callable[[str], PersistenceRepository],
    ) -> None:
        self._overlay_index = overlay_index
        self._overlay_repository = overlay_repository

    def repository_for_overlay(self, overlay_id: str) -> PersistenceRepository:
        """Return a repository for one registered runtime overlay id."""

        record = self._overlay_index.overlay_by_id(overlay_id)
        if record is None:
            raise KeyError(f"Overlay is not registered in overlay_index: {overlay_id}")
        return self._overlay_repository(record.overlay_uuid)


class OverlayThemeStore:
    """Store overlay-owned theme documents."""

    def __init__(
        self,
        *,
        overlay_index: OverlayIndexStore,
        overlay_repository: Callable[[str], PersistenceRepository],
    ) -> None:
        self._resolver = _OverlayRepositoryResolver(
            overlay_index=overlay_index,
            overlay_repository=overlay_repository,
        )

    def get_theme(self, overlay_id: str) -> dict[str, object]:
        """Return the theme document for one overlay."""

        document = self._resolver.repository_for_overlay(overlay_id).read_one(
            "overlay_theme",
            {"singleton_id": OVERLAY_THEME_SINGLETON_ID},
        )
        return dict(document.get("theme", {})) if document is not None else {}

    def set_theme(self, overlay_id: str, theme: dict[str, object]) -> None:
        """Persist the theme document for one overlay."""

        self._resolver.repository_for_overlay(overlay_id).write_one(
            "overlay_theme",
            {"singleton_id": OVERLAY_THEME_SINGLETON_ID},
            {"theme": dict(theme)},
        )


class OverlayLayoutStore:
    """Store overlay-owned layout documents."""

    def __init__(
        self,
        *,
        overlay_index: OverlayIndexStore,
        overlay_repository: Callable[[str], PersistenceRepository],
    ) -> None:
        self._resolver = _OverlayRepositoryResolver(
            overlay_index=overlay_index,
            overlay_repository=overlay_repository,
        )

    def get_layout(self, overlay_id: str) -> dict[str, object]:
        """Return the layout document for one overlay."""

        document = self._resolver.repository_for_overlay(overlay_id).read_one(
            "overlay_layout",
            {"singleton_id": OVERLAY_LAYOUT_SINGLETON_ID},
        )
        return dict(document.get("layout", {})) if document is not None else {}

    def set_layout(self, overlay_id: str, layout: dict[str, object]) -> None:
        """Persist the layout document for one overlay."""

        self._resolver.repository_for_overlay(overlay_id).write_one(
            "overlay_layout",
            {"singleton_id": OVERLAY_LAYOUT_SINGLETON_ID},
            {"layout": dict(layout)},
        )


class HostPluginStyleStore:
    """Store overlay-owned host plugin style documents."""

    def __init__(
        self,
        *,
        overlay_index: OverlayIndexStore,
        overlay_repository: Callable[[str], PersistenceRepository],
    ) -> None:
        self._resolver = _OverlayRepositoryResolver(
            overlay_index=overlay_index,
            overlay_repository=overlay_repository,
        )

    def get_style(self, overlay_id: str, plugin_id: str) -> dict[str, object]:
        """Return host plugin style for one overlay."""

        document = self._resolver.repository_for_overlay(overlay_id).read_one(
            "host_plugin_style",
            {"plugin_id": plugin_id},
        )
        return dict(document.get("style", {})) if document is not None else {}

    def set_style(self, overlay_id: str, plugin_id: str, style: dict[str, object]) -> None:
        """Persist host plugin style for one overlay."""

        self._resolver.repository_for_overlay(overlay_id).write_one(
            "host_plugin_style",
            {"plugin_id": plugin_id},
            {"style": dict(style)},
        )
