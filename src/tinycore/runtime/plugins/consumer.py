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

"""Runtime-owned plugin participation."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from tinycore.plugin.manifest import PluginManifest, ProviderRequest
from tinycore.plugin.spec import ConsumerRuntimeSpec
from tinycore.runtime.provider_activity import ProviderActivity

if TYPE_CHECKING:
    from tinycore.plugin.context import PluginContext
    from tinycore.runtime.process_supervisor import ProcessSupervisor, SpawnedProcessHandle
    from tinycore.services import RuntimeServices
    from .facts import ConsumerParticipationBindings


class SubprocessPlugin:
    """Host-side runtime participant for a subprocess-isolated consumer plugin."""

    def __init__(self, spec: ConsumerRuntimeSpec, *, process_supervisor: "ProcessSupervisor") -> None:
        self._spec = spec
        self._process_supervisor = process_supervisor
        self._handle: SpawnedProcessHandle | None = None

    @property
    def name(self) -> str:
        return self._spec.name

    @property
    def pid(self) -> int | None:
        """Return the child PID when the subprocess has been spawned."""
        return self._handle.pid if self._handle is not None else None

    def register(self, ctx: PluginContext) -> None:
        """Spawn the plugin subprocess and collect its registrations."""
        self._handle = self._process_supervisor.spawn_consumer_plugin(
            self._spec,
            extra_paths=list(sys.path),
        )
        conn = self._handle.conn

        try:
            msg = conn.recv()
            if msg.get("type") != "hello":
                raise RuntimeError(f"Plugin '{self._spec.name}': expected hello, got {msg}")
            if msg["name"] != self._spec.name:
                raise RuntimeError(
                    f"Plugin name mismatch: spec='{self._spec.name}' plugin='{msg['name']}'. "
                    f"Update ConsumerRuntimeSpec to use name='{msg['name']}'."
                )

            while True:
                msg = conn.recv()
                if msg["type"] == "register.done":
                    break
                self._dispatch(msg, ctx)
            self._process_supervisor.mark_running(self._handle.unit_id)
        except Exception:
            handle = self._handle
            if handle is not None:
                self._process_supervisor.mark_failed(handle.unit_id)
                try:
                    self._process_supervisor.stop(handle, timeout=0.5)
                except Exception:
                    try:
                        handle.conn.close()
                    finally:
                        if handle.process.is_alive():
                            handle.process.terminate()
                            handle.process.join(timeout=0.5)
                finally:
                    self._handle = None
            raise

    def start(self) -> None:
        if self._handle is not None:
            self._handle.conn.send({"type": "start"})
            self._handle.conn.recv()

    def stop(self) -> None:
        if self._handle is None:
            return

        handle = self._handle
        failed = False
        try:
            handle.conn.send({"type": "stop"})
            handle.conn.recv()
        except Exception:
            failed = True
            self._process_supervisor.mark_failed(handle.unit_id)
            raise
        finally:
            try:
                self._process_supervisor.stop(handle)
                if failed:
                    self._process_supervisor.mark_failed(handle.unit_id)
            finally:
                self._handle = None

    def _dispatch(self, msg: dict, ctx: PluginContext) -> None:
        """Route a registration message from the subprocess to the host registries."""
        t = msg["type"]

        if t == "settings.register":
            ctx.settings.register(msg["spec"])
        elif t == "editors.register":
            ctx.editors.register(msg["spec"])
        elif t == "loaders.register":
            ctx.config.register(msg["key"], msg["filename"], msg.get("defaults"))
        elif t == "loaders.load_all":
            ctx.config.load_all()
        elif t == "loaders.load":
            ctx.config.load(msg["key"])
        elif t == "loaders.save":
            ctx.config.save(msg["key"])


@dataclass(frozen=True)
class PluginParticipant:
    """Runtime-owned plugin participant plus its static declaration data."""

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
    ) -> "ConsumerParticipationBindings":
        """Resolve and store runtime capability bindings for this consumer."""
        bindings = runtime.plugin_facts.bind_consumer(
            self.name,
            self.requires,
            self.provider_requests,
        )
        provider_activity.bindings_changed(self.name)
        return bindings


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
