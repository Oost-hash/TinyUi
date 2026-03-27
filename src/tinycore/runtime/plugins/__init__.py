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

"""Runtime-owned plugin participation layer."""

from .bindings import bind_consumer_participants
from .consumer import ConsumerPluginParticipant, SubprocessPlugin, build_consumer_participants
from .facts import PluginParticipationFacts
from .lifecycle import PluginLifecycleManager
from .provider import (
    ProviderPluginParticipant,
    build_provider_participants,
    register_provider_participants,
)
from .registry import PluginRegistry

__all__ = [
    "bind_consumer_participants",
    "ConsumerPluginParticipant",
    "PluginParticipationFacts",
    "SubprocessPlugin",
    "build_consumer_participants",
    "PluginLifecycleManager",
    "ProviderPluginParticipant",
    "build_provider_participants",
    "register_provider_participants",
    "PluginRegistry",
]
