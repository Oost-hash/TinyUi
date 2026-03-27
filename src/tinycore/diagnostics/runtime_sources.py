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

"""Core-owned runtime inspection assembly."""

from __future__ import annotations

from tinywidgets.fields import read_field

from tinycore.runtime.core_runtime import CoreRuntime

from .runtime_state import RuntimeInspector
from .snapshot_protocols import InspectionSnapshot


def _render_value(value: object) -> str:
    if isinstance(value, int | float):
        return f"{float(value):.6g}"
    return str(value)


def _provider_snapshot(provider: object) -> InspectionSnapshot:
    snapshot = getattr(provider, "inspect_snapshot", None)
    if snapshot is None:
        return [("provider.inspect", "err: provider does not implement inspect_snapshot()")]
    try:
        return snapshot()
    except Exception as exc:
        return [("provider.inspect", f"err: {exc}")]


def _field_snapshot(
    capability: str,
    provider: object,
    fields: list[str],
) -> InspectionSnapshot:
    entries: InspectionSnapshot = []
    for field in fields:
        try:
            value = read_field(capability, field, provider)
            entries.append((field, _render_value(value)))
        except Exception as exc:
            entries.append((field, f"err: {exc}"))
    return entries


def _runtime_unit_snapshot(core: CoreRuntime) -> InspectionSnapshot:
    entries: InspectionSnapshot = []
    for unit in core.unit_infos():
        prefix = unit.id
        entries.extend(
            [
                (f"{prefix}.role", unit.role),
                (f"{prefix}.kind", unit.kind),
                (f"{prefix}.owner", unit.owner),
                (f"{prefix}.policy", unit.execution_policy),
                (f"{prefix}.activation", unit.activation_policy),
                (f"{prefix}.transport", unit.transport),
                (f"{prefix}.schedule.kind", unit.schedule_kind),
                (f"{prefix}.schedule.clock", unit.schedule_clock),
                (f"{prefix}.schedule.driver", unit.schedule_driver or ""),
                (f"{prefix}.schedule.intervalMs", "" if unit.interval_ms is None else str(unit.interval_ms)),
                (f"{prefix}.schedule.delayMs", "" if unit.delay_ms is None else str(unit.delay_ms)),
                (f"{prefix}.state", unit.state),
                (f"{prefix}.pid", "" if unit.pid is None else str(unit.pid)),
                (f"{prefix}.parent", unit.parent_id or ""),
            ]
        )
    return entries


def _runtime_activation_snapshot(core: CoreRuntime) -> InspectionSnapshot:
    active_providers = ", ".join(core.provider_activity.active_provider_names()) or "-"
    active_participants = ", ".join(core.lifecycle.active_participant_names()) or "-"
    return [
        ("participants.active", active_participants),
        ("providers.active", active_providers),
    ]


def _runtime_scheduler_snapshot(core: CoreRuntime) -> InspectionSnapshot:
    task_ids = core.scheduled_task_ids()
    return [
        ("tasks.count", str(len(task_ids))),
        ("tasks.ids", ", ".join(task_ids) or "-"),
    ]


def build_runtime_inspector(
    core: CoreRuntime,
    widget_sources: list[tuple[str, str, str]],
) -> RuntimeInspector:
    """Build the core-owned runtime inspector for the current runtime graph."""
    runtime_inspector = RuntimeInspector()
    runtime_inspector.add_snapshot_source(
        "runtime:units",
        "Runtime: Units",
        "runtime",
        lambda: _runtime_unit_snapshot(core),
    )
    runtime_inspector.add_snapshot_source(
        "runtime:activation",
        "Runtime: Activation",
        "runtime",
        lambda: _runtime_activation_snapshot(core),
    )
    runtime_inspector.add_snapshot_source(
        "runtime:scheduler",
        "Runtime: Scheduler",
        "runtime",
        lambda: _runtime_scheduler_snapshot(core),
    )

    by_consumer: dict[str, dict[str, list[str]]] = {}
    for consumer_name, capability, field in widget_sources:
        by_consumer.setdefault(consumer_name, {}).setdefault(capability, []).append(field)

    for consumer_name, fields_by_capability in by_consumer.items():
        seen_provider_names: set[str] = set()
        for capability, fields in fields_by_capability.items():
            binding = core.runtime.plugin_facts.bindings_for(consumer_name).get(capability)
            if binding is None:
                continue

            if binding.provider_name not in seen_provider_names:
                handle = core.runtime.plugin_facts.provider(binding.provider_name)
                if handle is not None:
                    runtime_inspector.add_snapshot_source(
                        f"provider:{binding.provider_name}:telemetry",
                        f"Provider: {binding.provider_name}",
                        "provider",
                        lambda provider=handle.provider: _provider_snapshot(provider),
                    )
                    seen_provider_names.add(binding.provider_name)

            runtime_inspector.add_snapshot_source(
                f"field:{consumer_name}:{capability}",
                f"Fields: {consumer_name} [{capability}]",
                "field",
                lambda capability=capability, provider=binding.provider, fields=list(fields): (
                    _field_snapshot(capability, provider, fields)
                ),
            )

    return runtime_inspector
