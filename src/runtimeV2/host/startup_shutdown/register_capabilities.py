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

"""Capability registration for runtime V2 host."""

from __future__ import annotations

from dataclasses import dataclass

from runtimeV2.host.capabilities.app_identity_read import AppIdentityRead
from runtimeV2.host.capabilities.host_shell_read import HostShellRead
from runtimeV2.host.capabilities.main_window_read import MainWindowRead
from runtimeV2.host.contracts import HostShell


@dataclass(frozen=True)
class HostCapabilities:
    """Capabilities exposed by the host domain."""

    app_identity_read: AppIdentityRead
    host_shell_read: HostShellRead
    main_window_read: MainWindowRead


def register_host_capabilities(host_shell: HostShell) -> HostCapabilities:
    """Create host domain capabilities."""

    return HostCapabilities(
        app_identity_read=AppIdentityRead(host_shell),
        host_shell_read=HostShellRead(host_shell),
        main_window_read=MainWindowRead(host_shell),
    )
