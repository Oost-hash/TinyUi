"""ui_api action projection above runtimeV2."""

from __future__ import annotations

from collections.abc import Callable

from ui_api.api.app_actions import AppActions

from runtimeV2.capabilities.runtime_shutdown import RuntimeShutdown
from runtimeV2.ui.capabilities.window_actions_write import WindowActionsWrite
from runtimeV2.widgets.capabilities.widget_visibility_read import WidgetVisibilityRead
from runtimeV2.widgets.capabilities.widget_visibility_write import WidgetVisibilityWrite


class UIActionsCapability:
    """Register ui_api host actions from runtime-owned capabilities."""

    def __init__(
        self,
        *,
        window_actions: WindowActionsWrite,
        widget_visibility_read: WidgetVisibilityRead,
        widget_visibility_write: WidgetVisibilityWrite,
        shutdown: RuntimeShutdown,
    ) -> None:
        self._window_actions = window_actions
        self._widget_visibility_read = widget_visibility_read
        self._widget_visibility_write = widget_visibility_write
        self._shutdown = shutdown

    def register(
        self,
        actions: AppActions,
        *,
        open_window: Callable[[str], None],
    ) -> None:
        """Register runtime-backed action handlers into ui_api."""

        actions.register("close", self._request_close)
        actions.register("widgetVisibility.toggle", self._toggle_widget_visibility)

        for window_id in self._window_actions.openable_window_ids():
            actions.register(f"open:{window_id}", self._make_open_handler(window_id, open_window))

    def _make_open_handler(self, window_id: str, open_window: Callable[[str], None]) -> Callable[[], None]:
        def handler() -> None:
            if self._window_actions.request_open_window(window_id):
                open_window(window_id)

        return handler

    def _request_close(self) -> None:
        self._shutdown.begin_shutdown("main_window_close")

    def _toggle_widget_visibility(self) -> None:
        current = self._widget_visibility_read.global_visible()
        self._widget_visibility_write.set_global_visible(not current)
