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

"""Runtime-owned export registry and resolved export types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ExportBinding:
    """Resolved provider for one exported runtime surface."""

    export_name: str
    provider_name: str
    provider: Any


@dataclass(frozen=True)
class ExportProvider:
    """Registered provider for one exported runtime surface."""

    export_name: str
    provider_name: str
    provider: Any


class ExportRegistry:
    """Register exported surfaces and resolve providers by export name."""

    def __init__(self) -> None:
        self._exports: dict[str, ExportProvider] = {}

    def register(
        self,
        export_name: str,
        provider_name: str,
        provider: Any,
    ) -> None:
        """Register one exported surface for a provider."""
        existing = self._exports.get(export_name)
        if existing is not None and existing.provider_name != provider_name:
            raise ValueError(
                f"Export '{export_name}' is already owned by provider "
                f"'{existing.provider_name}', cannot also register '{provider_name}'"
            )
        self._exports[export_name] = ExportProvider(
            export_name=export_name,
            provider_name=provider_name,
            provider=provider,
        )

    def register_many(
        self,
        provider_name: str,
        export_names: tuple[str, ...],
        provider: Any,
    ) -> None:
        """Register all exported surfaces for one provider."""
        for export_name in export_names:
            self.register(export_name, provider_name, provider)

    def provider_for(self, export_name: str) -> ExportProvider | None:
        """Return the registered provider for an exported surface, if any."""
        return self._exports.get(export_name)

    def all(self) -> list[ExportProvider]:
        """Return all registered export-provider pairs."""
        return list(self._exports.values())
