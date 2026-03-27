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

"""Runtime-owned provider plugin participation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from tinycore.logging import get_logger
from tinycore.plugin.manifest import PluginManifest
from tinycore.runtime.provider_activity import ProviderActivity

if TYPE_CHECKING:
    from tinycore.services import RuntimeServices

_log = get_logger(__name__)


@dataclass(frozen=True)
class ProviderPluginParticipant:
    """Live runtime participant for one provider plugin manifest."""

    manifest: PluginManifest

    @property
    def name(self) -> str:
        return self.manifest.name

    @property
    def exports(self) -> tuple[str, ...]:
        return self.manifest.exports

    def register(self, runtime: RuntimeServices, provider_activity: ProviderActivity) -> None:
        """Instantiate, open, and register the provider into session/runtime."""
        provider_decl = self.manifest.provider
        if provider_decl is None:
            return
        provider = provider_decl.create()
        provider.open()
        runtime.plugin_facts.register_provider(self.name, provider, self.exports)
        provider_activity.provider_registered(self.name)
        _log.info(
            "provider registered  plugin=%s  type=%s  exports=%s",
            self.name,
            type(provider).__name__,
            ", ".join(self.exports) if self.exports else "-",
        )


def build_provider_participants(
    manifests: list[PluginManifest],
) -> list[ProviderPluginParticipant]:
    """Build live provider participants from manifests for runtime registration."""
    return [
        ProviderPluginParticipant(manifest)
        for manifest in manifests
        if manifest.is_provider
    ]


def register_provider_participants(
    runtime: RuntimeServices,
    participants: list[ProviderPluginParticipant],
    provider_activity: ProviderActivity,
) -> None:
    """Register all live provider participants into session/runtime."""
    for participant in participants:
        participant.register(runtime, provider_activity)
