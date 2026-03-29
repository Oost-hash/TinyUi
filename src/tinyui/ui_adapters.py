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

#  TinyUI
"""TinyUI-owned UI adapter helpers."""

from __future__ import annotations

from typing import Any, Protocol, cast

from PySide6.QtCore import QObject


class _ThemeLike(Protocol):
    def load(self, name: str, /) -> None: ...


def _maybe_int(value: object) -> int | None:
    return int(value) if isinstance(value, int | float | str) else None


def bind_statusbar_plugin_switching(core, statusbar_view_model: object) -> None:
    """Drive plugin lifecycle activation from the status bar selection surface."""
    if not isinstance(statusbar_view_model, QObject):
        return

    plugin_names = [
        participant.name for participant in core.runtime.plugin_runtime.registered_participants
    ]
    if not plugin_names:
        return

    def _on_plugin_switch() -> None:
        index = _maybe_int(statusbar_view_model.property("activePluginIndex"))
        if index is None:
            return
        if 0 <= index < len(plugin_names):
            core.activation.activate(plugin_names[index])

    active_changed = cast(Any, getattr(statusbar_view_model, "activePluginIndexChanged", None))
    if active_changed is not None:
        active_changed.connect(_on_plugin_switch)


def bind_tab_plugin_switching(core, tab_view_model: object) -> None:
    """Drive plugin lifecycle activation from the tab bar selection surface."""
    if not isinstance(tab_view_model, QObject):
        return

    plugin_names = [
        participant.name for participant in core.runtime.plugin_runtime.registered_participants
    ]
    if not plugin_names:
        return

    def _on_tab_switch() -> None:
        index = _maybe_int(tab_view_model.property("currentIndex"))
        if index is None:
            return
        if 0 <= index < len(plugin_names):
            core.activation.activate(plugin_names[index])

    current_index_changed = cast(Any, getattr(tab_view_model, "currentIndexChanged", None))
    if current_index_changed is not None:
        current_index_changed.connect(_on_tab_switch)


def bind_theme_settings(
    core,
    core_view_model: object,
    settings_panel_view_model: object,
    theme: _ThemeLike,
) -> None:
    """Apply and persist TinyUI theme/settings wiring through host persistence."""
    if not isinstance(core_view_model, QObject) or not isinstance(
        settings_panel_view_model, QObject
    ):
        return

    def _apply_tinyui_settings() -> None:
        theme_name = core.host.persistence.get_setting("TinyUI", "theme")
        if theme_name:
            theme.load(str(theme_name))

    def _save_setting(plugin_name: str) -> None:
        core.host.persistence.save_settings(plugin_name)

    settings_changed = cast(Any, getattr(core_view_model, "settingsChanged", None))
    setting_value_changed = cast(
        Any, getattr(core_view_model, "settingValueChanged", None)
    )
    setting_change_requested = cast(
        Any, getattr(settings_panel_view_model, "settingChangeRequested", None)
    )
    set_setting_value = cast(Any, getattr(core_view_model, "setSettingValue", None))

    if settings_changed is not None:
        settings_changed.connect(_apply_tinyui_settings)
    if setting_value_changed is not None:
        setting_value_changed.connect(_save_setting)
    if setting_change_requested is not None and callable(set_setting_value):
        setting_change_requested.connect(set_setting_value)

    _apply_tinyui_settings()
