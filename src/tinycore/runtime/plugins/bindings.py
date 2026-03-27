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

"""Runtime-owned binding helpers for plugin participation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tinycore.logging import get_logger
from tinycore.runtime.provider_activity import ProviderActivity

from .consumer import PluginParticipant

if TYPE_CHECKING:
    from tinycore.services import RuntimeServices

_log = get_logger(__name__)


def bind_plugin_participants(
    runtime: RuntimeServices,
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
                    f"{capability}->{binding.provider_name}"
                    for capability, binding in bindings.resolved.items()
                ),
            )
