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
"""Plugin manifest parser for the runtime architecture.

Each plugin directory contains a ``plugin.toml`` that declares one of the
runtime roles:

``plugin.consumer``
    Declares a subprocess plugin with logic, UI assets, and capability
    requirements.

``plugin.provider``
    Declares a host-side provider that exports capabilities and owns the
    integration/runtime surface.
"""

from __future__ import annotations

import importlib
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from .spec import ConsumerRuntimeSpec


_CONSUMER_TYPE = "plugin.consumer"
_PROVIDER_TYPE = "plugin.provider"


@dataclass(frozen=True)
class RuntimeDecl:
    """Import target for a manifest-declared runtime object."""

    module: str
    class_name: str

    def create(self):
        """Import and instantiate the declared class."""
        mod = importlib.import_module(self.module)
        cls = getattr(mod, self.class_name)
        return cls()


@dataclass(frozen=True)
class UIManifest:
    """UI-facing assets declared by a plugin."""

    widgets_file: str | None = None


@dataclass(frozen=True)
class PluginManifest:
    """Parsed contents of a ``plugin.toml`` file."""

    name: str
    plugin_type: str
    version: str
    plugin_dir: Path
    requires: tuple[str, ...] = field(default_factory=tuple)
    exports: tuple[str, ...] = field(default_factory=tuple)
    logic: RuntimeDecl | None = None
    provider: RuntimeDecl | None = None
    ui: UIManifest = field(default_factory=UIManifest)
    editors_file: str | None = None

    @property
    def is_consumer(self) -> bool:
        """Return ``True`` when this manifest declares a consumer plugin."""
        return self.plugin_type == _CONSUMER_TYPE

    @property
    def is_provider(self) -> bool:
        """Return ``True`` when this manifest declares a provider plugin."""
        return self.plugin_type == _PROVIDER_TYPE

    def widgets_path(self) -> Path | None:
        """Absolute path to the widgets TOML file, or ``None`` if absent."""
        if not self.ui.widgets_file:
            return None
        return self.plugin_dir / self.ui.widgets_file

    def editors_path(self) -> Path | None:
        """Absolute path to the editors TOML file, or ``None`` if absent."""
        if not self.editors_file:
            return None
        return self.plugin_dir / self.editors_file

    def consumer_runtime_spec(self) -> ConsumerRuntimeSpec:
        """Build the subprocess runtime spec for a consumer plugin."""
        if self.logic is None:
            raise ValueError(f"Plugin '{self.name}' has no [logic] declaration")
        return ConsumerRuntimeSpec(
            self.logic.module,
            self.logic.class_name,
            name=self.name,
            requires=self.requires,
        )


def _runtime_decl(data: dict, section: str) -> RuntimeDecl:
    try:
        return RuntimeDecl(module=data["module"], class_name=data["class"])
    except KeyError as exc:
        raise ValueError(f"Manifest section [{section}] is missing '{exc.args[0]}'") from exc


def _tuple_of_strings(data: dict, key: str) -> tuple[str, ...]:
    values = data.get(key, [])
    if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
        raise ValueError(f"Manifest key '{key}' must be a list of strings")
    return tuple(values)


def load_manifest(path: Path) -> PluginManifest:
    """Parse a ``plugin.toml`` file and return a validated PluginManifest."""
    with path.open("rb") as f:
        data = tomllib.load(f)

    plugin_type = data.get("type")
    if plugin_type not in {_CONSUMER_TYPE, _PROVIDER_TYPE}:
        raise ValueError(
            f"Plugin '{path.parent.name}' must declare type '{_CONSUMER_TYPE}' "
            f"or '{_PROVIDER_TYPE}'"
        )

    ui_data = data.get("ui", {})
    ui = UIManifest(widgets_file=ui_data.get("widgets"))

    manifest = PluginManifest(
        name=data["name"],
        plugin_type=plugin_type,
        version=data["version"],
        plugin_dir=path.parent,
        requires=_tuple_of_strings(data, "requires"),
        exports=_tuple_of_strings(data, "exports"),
        logic=_runtime_decl(data["logic"], "logic") if "logic" in data else None,
        provider=_runtime_decl(data["provider"], "provider") if "provider" in data else None,
        ui=ui,
        editors_file=data.get("editors", {}).get("file"),
    )

    if manifest.is_consumer and manifest.logic is None:
        raise ValueError(f"Consumer plugin '{manifest.name}' must declare [logic]")
    if manifest.is_provider and manifest.provider is None:
        raise ValueError(f"Provider plugin '{manifest.name}' must declare [provider]")
    if manifest.is_consumer and manifest.exports:
        raise ValueError(f"Consumer plugin '{manifest.name}' cannot declare exports")
    if manifest.is_provider and manifest.requires:
        raise ValueError(f"Provider plugin '{manifest.name}' cannot declare requires")

    return manifest


def scan_plugins(plugins_dir: Path) -> list[PluginManifest]:
    """Return manifests for all plugins found in ``plugins_dir``."""
    manifests = []
    for manifest_path in sorted(plugins_dir.glob("*/plugin.toml")):
        manifests.append(load_manifest(manifest_path))
    return manifests
