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

"""Public persistence contracts used outside the persistence domain."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from runtimeV2.persistence.contracts import WidgetInstanceConfig
from runtimeV2.persistence.manifest.settings import SettingDecl


@runtime_checkable
class SettingsReader(Protocol):
    """Public contract for reading setting specs and values."""

    def get(self, namespace: str, key: str) -> Any:
        """Return one setting value."""
        ...

    def by_namespace(self) -> dict[str, list[SettingDecl]]:
        """Return specs by namespace."""
        ...

    def values_by_namespace(self) -> dict[str, dict[str, Any]]:
        """Return current values by namespace."""
        ...

    def namespace_values(self, namespace: str) -> dict[str, Any]:
        """Return current values for one namespace."""
        ...


@runtime_checkable
class SettingsWriter(Protocol):
    """Public contract for writing setting values."""

    def set(self, namespace: str, key: str, value: Any) -> None:
        """Set one setting value."""
        ...

    def save(self, namespace: str) -> None:
        """Save one namespace."""
        ...

    def save_all(self) -> None:
        """Save all namespaces."""
        ...


@runtime_checkable
class WidgetConfigReader(Protocol):
    """Public contract for reading widget configuration values."""

    def get_overlay(self, overlay_id: str) -> list[WidgetInstanceConfig]:
        """Return config for one overlay."""
        ...

    def get_widget(self, overlay_id: str, widget_id: str) -> WidgetInstanceConfig | None:
        """Return config for one widget."""
        ...

    def widget_values(self, overlay_id: str, widget_id: str) -> dict[str, object]:
        """Return config values for one widget."""
        ...

    def widget_type_defaults(self, overlay_id: str, widget_type: str) -> dict[str, object]:
        """Return defaults for one widget type in an overlay."""
        ...

    def global_widgets_visible(self) -> bool:
        """Return global widget visibility."""
        ...


@runtime_checkable
class WidgetConfigWriter(Protocol):
    """Public contract for writing widget configuration values."""

    def set_widget_enabled(self, overlay_id: str, widget_id: str, enabled: bool) -> bool:
        """Set widget enabled state."""
        ...

    def set_widget_position(self, overlay_id: str, widget_id: str, x: int, y: int) -> bool:
        """Set widget position."""
        ...

    def set_widget_values(self, overlay_id: str, widget_id: str, values: dict[str, object]) -> bool:
        """Set widget config values."""
        ...

    def reset_widget_values(self, overlay_id: str, widget_id: str) -> bool:
        """Reset widget config values."""
        ...

    def set_widget_type_defaults(self, overlay_id: str, widget_type: str, defaults: dict[str, object]) -> bool:
        """Set defaults for one widget type in an overlay."""
        ...

    def reset_widget_type_defaults(self, overlay_id: str, widget_type: str) -> bool:
        """Reset defaults for one widget type in an overlay."""
        ...

    def set_global_widgets_visible(self, visible: bool) -> None:
        """Set global widget visibility."""
        ...

