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
"""ConsumerRuntimeSpec — descriptor for a subprocess-isolated consumer plugin."""

from dataclasses import dataclass, field


@dataclass
class ConsumerRuntimeSpec:
    """Describes a consumer plugin that will run in an isolated subprocess.

    The host never imports the plugin module — only the subprocess does.
    Name is derived from the class name if omitted: "DemoPlugin" → "demo".

    Usage:
        ConsumerRuntimeSpec("plugins.demo", "DemoPlugin")
        ConsumerRuntimeSpec("acme.laptime", "LapTimePlugin", name="laptime")
    """

    module: str         # Python module path, e.g. "plugins.demo"
    cls:    str         # Class name, e.g. "DemoPlugin"
    name:   str = ""    # Plugin name; auto-derived from cls if empty
    requires: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.name:
            n = self.cls
            if n.endswith("Plugin"):
                n = n[:-6]
            self.name = n.lower() or self.cls.lower()
