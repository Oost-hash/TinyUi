"""Shared runtime host projection capabilities."""

from shared_runtime_host.capabilities.ui_host import UIHostCapability
from shared_runtime_host.capabilities.window_host import WindowHostCapability
from shared_runtime_host.capabilities.widget_host import WidgetHostCapability

__all__ = ["UIHostCapability", "WindowHostCapability", "WidgetHostCapability"]
