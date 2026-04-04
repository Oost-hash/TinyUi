"""Connector service loader for manifest-declared connector services."""

from __future__ import annotations

import importlib


def load_connector_service(module_name: str, class_name: str):
    """Instantiate a connector service object from a module/class reference."""
    module = importlib.import_module(module_name)
    service_type = getattr(module, class_name)
    return service_type()
