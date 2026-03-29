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

"""Plugin participation-owned provider refresh participant."""

from __future__ import annotations

from typing import Protocol, cast

from tinyruntime_schema import get_logger

from .provider_activity import ProviderActivity

_log = get_logger(__name__)


class _ProviderStateLike(Protocol):
    def active(self) -> bool: ...
    def paused(self) -> bool: ...


class _StatefulProvider(Protocol):
    state: _ProviderStateLike


class ProviderRefreshParticipant:
    """Refresh active providers and log provider state transitions per update cycle."""

    def __init__(self, provider_activity: ProviderActivity) -> None:
        self._provider_activity = provider_activity
        self._prev: dict[str, dict[str, bool | None]] = {}

    def tick(self) -> None:
        errors = self._provider_activity.update_providers()
        for name, error in errors:
            _log.connector("update error", plugin=name, error=error)
        for name, handle in self._provider_activity.active_provider_items():
            self._check_state(name, handle.provider)

    def _check_state(self, name: str, provider: object) -> None:
        """Detect and log active/paused transitions for one provider runtime."""
        try:
            stateful = cast(_StatefulProvider, provider)
            active = stateful.state.active()
            paused = stateful.state.paused()
        except Exception:
            return

        prev = self._prev.get(name)
        if prev is None:
            self._prev[name] = {"active": active, "paused": paused}
            return

        if active != prev["active"]:
            prev["active"] = active
            if active:
                _log.connector("game started", plugin=name)
            else:
                _log.connector("game stopped", plugin=name)

        if paused != prev["paused"]:
            prev["paused"] = paused
            if paused:
                _log.connector("game paused", plugin=name)
            else:
                _log.connector("game resumed", plugin=name)
