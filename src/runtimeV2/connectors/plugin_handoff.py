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

"""Connector plugin.py handoff for manifest-declared game-state hooks."""

from __future__ import annotations

import importlib
from collections.abc import Callable

from runtimeV2.connectors.capabilities.connector_read import ConnectorRead
from runtimeV2.connectors.contracts import ConnectorGameStateDecision, ConnectorGameStateUpdate
from runtimeV2.connectors.decision_store import ConnectorGameStateDecisionStore
from runtimeV2.connectors.schemas.manifest import ConnectorManifest
from runtimeV2.widgets.capabilities.widget_manual_override import WidgetManualOverride
from runtimeV2.widgets.capabilities.widget_visibility_write import WidgetVisibilityWrite


class ConnectorGameStateHookDispatcher:
    """Dispatch connector game-state changes into plugin.py hooks."""

    def __init__(
        self,
        declarations: dict[str, ConnectorManifest],
        connector_read: ConnectorRead,
        decision_store: ConnectorGameStateDecisionStore,
        widget_visibility_write: WidgetVisibilityWrite | None = None,
        widget_manual_override: WidgetManualOverride | None = None,
    ) -> None:
        self._declarations = declarations
        self._connector_read = connector_read
        self._decision_store = decision_store
        self._widget_visibility_write = widget_visibility_write
        self._widget_manual_override = widget_manual_override

    def sync_connector(self, connector_id: str) -> bool:
        """Dispatch one connector update when the manifest declares a hook."""

        hook = self._resolve_hook(connector_id)
        if hook is None:
            return False
        update = self._build_update(connector_id)
        decision = self._normalize_decision(hook(update))
        # Override decision for mock source: always show widgets when mock is active
        if update.active_source == "mock":
            decision = ConnectorGameStateDecision(show_widgets=True)
        if decision is not None:
            self._decision_store.set(connector_id, decision)
            self._apply_decision(decision)
        return True

    def apply_no_game(self, connector_id: str) -> None:
        """Apply the generic no-game connector decision."""

        decision = ConnectorGameStateDecision(show_widgets=False)
        self._decision_store.set(connector_id, decision)
        self._apply_decision(decision)

    def _apply_decision(self, decision: ConnectorGameStateDecision) -> None:
        if self._widget_visibility_write is None:
            return
        if decision.show_widgets is not None:
            # Use connector-specific method that respects manual override.
            # Connectors can show widgets (when game is live) but cannot hide
            # them if the user has manually enabled widgets.
            self._widget_visibility_write.set_global_visible_from_connector(decision.show_widgets)

    def _build_update(self, connector_id: str) -> ConnectorGameStateUpdate:
        active_source = self._connector_read.active_source(connector_id) or "none"
        active_game = self._connector_read.active_game(connector_id) or "none"
        state_active = self._connector_read.state_active(connector_id)
        state_paused = self._connector_read.state_paused(connector_id)
        return ConnectorGameStateUpdate(
            connector_id=connector_id,
            plugin_id=connector_id,
            active_source=active_source,
            active_game=active_game,
            is_live=active_source not in {"none", "mock"},
            state_active=bool(state_active),
            state_paused=bool(state_paused),
        )

    def _resolve_hook(
        self,
        connector_id: str,
    ) -> Callable[[ConnectorGameStateUpdate], object | None] | None:
        declaration = self._declarations.get(connector_id)
        if declaration is None or declaration.runtime is None:
            return None
        hook_name = declaration.runtime.game_state_hook.strip()
        if not hook_name:
            return None
        try:
            module = importlib.import_module(f"plugins.{connector_id}.plugin")
        except ModuleNotFoundError:
            return None
        hook = getattr(module, hook_name, None)
        return hook if callable(hook) else None

    @staticmethod
    def _normalize_decision(raw: object) -> ConnectorGameStateDecision | None:
        if raw is None:
            return None
        if isinstance(raw, ConnectorGameStateDecision):
            return raw
        if isinstance(raw, dict):
            show_widgets = raw.get("show_widgets")
            if show_widgets is None:
                return None
            if isinstance(show_widgets, bool):
                return ConnectorGameStateDecision(show_widgets=show_widgets)
        return None
