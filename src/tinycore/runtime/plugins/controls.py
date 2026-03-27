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

"""Runtime-owned control facade for provider-bound plugin participation."""

from __future__ import annotations

from tinycore.session.control import DemoConfig

from .protocols import PluginParticipationControlsBackend


class PluginParticipationControls:
    """Expose provider-bound control actions through a runtime-owned seam."""

    def __init__(self, controls: PluginParticipationControlsBackend) -> None:
        self._controls = controls

    def provider_name_for(self, consumer_name: str, capability: str) -> str:
        return self._controls.provider_name_for(consumer_name, capability)

    def supports_demo_mode(self, consumer_name: str, capability: str) -> bool:
        return self._controls.supports_demo_mode(consumer_name, capability)

    def request_demo_mode(self, consumer_name: str, capability: str, owner: str) -> bool:
        return self._controls.request_demo_mode(consumer_name, capability, owner)

    def release_demo_mode(self, consumer_name: str, capability: str, owner: str) -> bool:
        return self._controls.release_demo_mode(consumer_name, capability, owner)

    def provider_mode(self, consumer_name: str, capability: str) -> str:
        return self._controls.provider_mode(consumer_name, capability)

    def active_game(self, consumer_name: str, capability: str) -> str:
        return self._controls.active_game(consumer_name, capability)

    def demo_config(self, consumer_name: str, capability: str) -> DemoConfig:
        return self._controls.demo_config(consumer_name, capability)

    def set_demo_min(self, consumer_name: str, capability: str, value: float) -> bool:
        return self._controls.set_demo_min(consumer_name, capability, value)

    def set_demo_max(self, consumer_name: str, capability: str, value: float) -> bool:
        return self._controls.set_demo_max(consumer_name, capability, value)

    def set_demo_speed(self, consumer_name: str, capability: str, value: float) -> bool:
        return self._controls.set_demo_speed(consumer_name, capability, value)
