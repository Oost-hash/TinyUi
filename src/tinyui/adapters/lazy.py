#  TinyUI - A mod for TinyPedal
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
#  licensed under GPLv3. TinyPedal is included as a submodule.

"""Base classes for lazy loading and adaptation."""

import importlib
from typing import Any, Optional


class LazyModule:
    """Lazy proxy that imports the real module on first attribute access.

    This breaks circular imports and speeds up startup by only loading
    what's actually used.
    """

    def __init__(self, module_path: str, attr: Optional[str] = None):
        """
        Args:
            module_path: Full dotted path, e.g. 'tinypedal.api_control'
            attr: Optional attribute to extract from module (e.g. 'api')
        """
        self._path = module_path
        self._attr = attr
        self._real: Any = None
        self._loaded = False

    def _load(self) -> Any:
        """Import and cache the real module/object."""
        if not self._loaded:
            module = importlib.import_module(self._path)
            self._real = getattr(module, self._attr) if self._attr else module
            self._loaded = True
        return self._real

    def __getattr__(self, name: str) -> Any:
        """Forward attribute access to real module."""
        real = self._load()
        return getattr(real, name)

    def __call__(self, *args, **kwargs):
        """Allow calling if the wrapped object is callable."""
        real = self._load()
        return real(*args, **kwargs)

    def __repr__(self) -> str:
        status = "loaded" if self._loaded else "lazy"
        target = f".{self._attr}" if self._attr else ""
        return f"<LazyModule {status}: {self._path}{target}>"


class LazyCallable:
    """Lazy wrapper for a specific callable (function/method)."""

    def __init__(self, module_path: str, func_name: str):
        self._module_path = module_path
        self._func_name = func_name
        self._func: Optional[callable] = None

    def _load(self):
        if self._func is None:
            module = importlib.import_module(self._module_path)
            self._func = getattr(module, self._func_name)
        return self._func

    def __call__(self, *args, **kwargs):
        return self._load()(*args, **kwargs)
