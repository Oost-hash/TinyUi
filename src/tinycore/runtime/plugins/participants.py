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

"""Runtime-owned plugin participation roles and assembly helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from tinycore.logging import get_logger
from tinycore.plugin.manifest import PluginManifest, ProviderRequest

from .subprocess import SubprocessPlugin
from .provider_activity import ProviderActivity

if TYPE_CHECKING:
    from tinycore.runtime.process_supervisor import ProcessSupervisor
    from tinycore.services import RuntimeServices
    from .facts import ParticipantBindingSet

_log = get_logger(__name__)


@dataclass(frozen=True)
class PluginParticipant:
    """Runtime-owned plugin participation plus its static declaration data."""

    manifest: PluginManifest
    plugin: SubprocessPlugin

    @property
    def name(self) -> str:
        return self.manifest.name

    @property
    def requires(self) -> tuple[str, ...]:
        return self.manifest.requires

    @property
    def provider_requests(self) -> tuple[ProviderRequest, ...]:
        return self.manifest.provider_requests

    def widgets_path(self) -> Path | None:
        return self.manifest.widgets_path()

    def bind(
        self,
        runtime: "RuntimeServices",
        provider_activity: ProviderActivity,
    ) -> "ParticipantBindingSet":
        """Resolve and store runtime export bindings for this participant."""
        bindings = runtime.plugin_facts.bind_participant(
            self.name,
            self.requires,
            self.provider_requests,
        )
        provider_activity.bindings_changed(self.name)
        return bindings


@dataclass(frozen=True)
class ProviderParticipant:
    """Live runtime participant for one provider plugin manifest."""

    manifest: PluginManifest

    @property
    def name(self) -> str:
        return self.manifest.name

    @property
    def exports(self) -> tuple[str, ...]:
        return self.manifest.exports

    def register(self, runtime: "RuntimeServices", provider_activity: ProviderActivity) -> None:
        """Instantiate, open, and register the provider into runtime participation."""
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


def build_plugin_participants(
    manifests: list[PluginManifest],
    *,
    process_supervisor: "ProcessSupervisor",
) -> list[PluginParticipant]:
    """Build live plugin participants from manifests for runtime composition."""
    participants: list[PluginParticipant] = []
    for manifest in manifests:
        if not manifest.is_consumer:
            continue
        participants.append(
            PluginParticipant(
                manifest=manifest,
                plugin=SubprocessPlugin(
                    manifest.consumer_runtime_spec(),
                    process_supervisor=process_supervisor,
                ),
            )
        )
    return participants


def build_provider_participants(
    manifests: list[PluginManifest],
) -> list[ProviderParticipant]:
    """Build live provider participants from manifests for runtime registration."""
    return [
        ProviderParticipant(manifest)
        for manifest in manifests
        if manifest.is_provider
    ]


def bind_plugin_participants(
    runtime: "RuntimeServices",
    participants: list[PluginParticipant],
    provider_activity: ProviderActivity,
) -> None:
    """Resolve and log runtime bindings for live plugin participants."""
    for participant in participants:
        bindings = participant.bind(runtime, provider_activity)
        if bindings.missing:
            _log.warning(
                "participant missing bindings  plugin=%s  missing=%s",
                participant.name,
                ", ".join(bindings.missing),
            )
            continue
        if bindings.resolved:
            _log.info(
                "participant bound  plugin=%s  bindings=%s",
                participant.name,
                ", ".join(
                    f"{export_name}->{binding.provider_name}"
                    for export_name, binding in bindings.resolved.items()
                ),
            )


def register_provider_participants(
    runtime: "RuntimeServices",
    participants: list[ProviderParticipant],
    provider_activity: ProviderActivity,
) -> None:
    """Register all live provider participants into runtime participation."""
    for participant in participants:
        participant.register(runtime, provider_activity)
