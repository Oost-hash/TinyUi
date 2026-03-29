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
"""tinyplugins — static plugin description boundary."""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .context import PluginContext
    from .protocol import Plugin
    from .spec import ConsumerRuntimeSpec


_EXPORTS: dict[str, tuple[str, str]] = {
    "ConsumerRuntimeSpec": (".spec", "ConsumerRuntimeSpec"),
    "Plugin": (".protocol", "Plugin"),
    "PluginContext": (".context", "PluginContext"),
}

__all__ = (
    "ConsumerRuntimeSpec",
    "Plugin",
    "PluginContext",
)


def __getattr__(name: str):
    target = _EXPORTS.get(name)
    if target is None:
        raise AttributeError(f"module 'tinyplugins' has no attribute '{name}'")
    module_name, attr_name = target
    module = import_module(module_name, __name__)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value
