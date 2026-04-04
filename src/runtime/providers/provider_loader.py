"""Provider loader for manifest-declared providers."""

from __future__ import annotations

import importlib


def load_provider(module_name: str, class_name: str):
    """Instantiate a provider object from a module/class reference."""
    module = importlib.import_module(module_name)
    provider_type = getattr(module, class_name)
    return provider_type()
