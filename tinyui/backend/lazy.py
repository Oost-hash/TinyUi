# tinyui/backend/lazy.py
"""Lazy loading proxies voor TinyPedal modules."""

import importlib
from typing import Any


class LazyModule:
    """Importeert een module pas bij eerste gebruik van een attribuut."""

    def __init__(self, module_name: str, attr_name: str = None):
        """
        Args:
            module_name: Volledige module naam, bv. 'tinypedal_repo.tinypedal.api_control'
            attr_name: Optioneel, als we een specifiek attribuut uit de module willen (bv. 'api')
        """
        self._module_name = module_name
        self._attr_name = attr_name
        self._module = None

    def _load(self):
        if self._module is None:
            self._module = importlib.import_module(self._module_name)

    def __getattr__(self, name: str) -> Any:
        self._load()
        if self._attr_name:
            obj = getattr(self._module, self._attr_name)
            return getattr(obj, name)
        return getattr(self._module, name)

    def __call__(self, *args, **kwargs):
        self._load()
        if self._attr_name:
            obj = getattr(self._module, self._attr_name)
            return obj(*args, **kwargs)
        return self._module(*args, **kwargs)
