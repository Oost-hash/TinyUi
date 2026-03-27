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

"""Shared runtime unit id helpers."""

from __future__ import annotations


def plugin_process_unit_id(plugin_name: str) -> str:
    """Return the runtime unit id for one plugin subprocess."""
    return f"plugin.process:{plugin_name}"


def plugin_participant_unit_id(plugin_name: str) -> str:
    """Return the runtime unit id for one plugin participation adapter."""
    return f"plugin.participant:{plugin_name}"


def provider_runtime_unit_id(provider_name: str) -> str:
    """Return the runtime unit id for one provider host runtime."""
    return f"provider.runtime:{provider_name}"


def provider_export_unit_id(provider_name: str, export_name: str) -> str:
    """Return the runtime unit id for one provider-exported surface."""
    return f"provider.export:{provider_name}:{export_name}"


def boot_phase_unit_id(phase_name: str) -> str:
    """Return the runtime unit id for one boot orchestration phase."""
    return f"boot.phase:{phase_name}"
