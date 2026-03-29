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
"""Shared QML singleton registration helpers for the Qt host layer."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import TypeAlias

from PySide6.QtQml import qmlRegisterSingletonInstance


RegistrationEntry: TypeAlias = tuple[type, str, object]
RegistrationMap: TypeAlias = dict[str, RegistrationEntry]
_registered_instances: list[object] = []


@dataclass(frozen=True)
class SingletonRegistration:
    cls: type
    module: str
    name: str
    instance: object
    major_version: int = 1
    minor_version: int = 0


def register_singletons(registrations: Iterable[SingletonRegistration]) -> None:
    """Register multiple singleton instances into the global QML type system."""
    for registration in registrations:
        _registered_instances.append(registration.instance)
        # PySide 6.10 accepts the QML name as str at runtime even though the stub
        # still advertises the older bytes-only shape.
        qmlRegisterSingletonInstance(
            registration.cls,
            registration.module,
            registration.major_version,
            registration.minor_version,
            registration.name,  # pyright: ignore[reportArgumentType]
            registration.instance,
        )


def registrations_from_map(context: RegistrationMap) -> list[SingletonRegistration]:
    """Convert the legacy extra-context map into shared singleton registrations."""
    return [
        SingletonRegistration(cls, module, name, instance)
        for name, (cls, module, instance) in context.items()
    ]


def register_context_map(context: RegistrationMap) -> None:
    """Register all singleton instances described by the legacy extra-context map."""
    register_singletons(registrations_from_map(context))
