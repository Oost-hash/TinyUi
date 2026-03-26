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
    Declares a subprocess plugin with logic, widget assets, and capability
    requirements.

``plugin.provider``
    Declares a host-side provider that exports capabilities and owns the
    integration/runtime surface.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from .runtime_loader import load_runtime_class
from .spec import ConsumerRuntimeSpec


_CONSUMER_TYPE = "plugin.consumer"
_PROVIDER_TYPE = "plugin.provider"


@dataclass(frozen=True)
class RuntimeDecl:
    """Import target for a manifest-declared runtime object."""

    module: str
    class_name: str
    artifact_path: str | None = None

    def create(self):
        """Import and instantiate the declared class."""
        cls = load_runtime_class(self.module, self.class_name, self.artifact_path)
        return cls()


@dataclass(frozen=True)
class RuntimeSection:
    """Packaged runtime metadata declared in ``[runtime]``."""

    kind: str
    entry_module: str
    entry_class: str
    artifact_path: str


@dataclass(frozen=True)
class WidgetManifest:
    """Widget-facing assets declared by a plugin."""

    widgets_file: str | None = None


@dataclass(frozen=True)
class UserFileDecl:
    """A user-facing file shipped by a packaged plugin."""

    source: str
    target: str
    kind: str
    copy_if_missing: bool = False


@dataclass(frozen=True)
class UserFilesManifest:
    """Packaged user-file rules declared by a plugin."""

    preserve_user_files: bool = False
    files: tuple[UserFileDecl, ...] = ()


@dataclass(frozen=True)
class ProviderRequest:
    """Consumer-side provider selection hint for one capability."""

    capability: str
    provider: str | None = None
    source: str | None = None


@dataclass(frozen=True)
class PluginManifest:
    """Parsed contents of a ``plugin.toml`` file."""

    name: str
    plugin_type: str
    version: str
    plugin_dir: Path
    manifest_path: Path
    requires: tuple[str, ...] = field(default_factory=tuple)
    exports: tuple[str, ...] = field(default_factory=tuple)
    provider_requests: tuple[ProviderRequest, ...] = field(default_factory=tuple)
    runtime: RuntimeSection | None = None
    logic: RuntimeDecl | None = None
    provider: RuntimeDecl | None = None
    widgets: WidgetManifest = field(default_factory=WidgetManifest)
    editors_file: str | None = None
    user_files: UserFilesManifest = field(default_factory=UserFilesManifest)

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
        if not self.widgets.widgets_file:
            return None
        return self.plugin_dir / self.widgets.widgets_file

    def editors_path(self) -> Path | None:
        """Absolute path to the editors TOML file, or ``None`` if absent."""
        if not self.editors_file:
            return None
        return self.plugin_dir / self.editors_file

    def consumer_runtime_spec(self) -> ConsumerRuntimeSpec:
        """Build the subprocess runtime spec for a consumer plugin."""
        runtime = self.runtime
        logic = self.logic
        if runtime is not None:
            module = runtime.entry_module
            class_name = runtime.entry_class
            artifact_path = runtime.artifact_path
        elif logic is not None:
            module = logic.module
            class_name = logic.class_name
            artifact_path = None
        else:
            raise ValueError(f"Plugin '{self.name}' has no [logic] or [runtime] declaration")

        return ConsumerRuntimeSpec(
            module,
            class_name,
            name=self.name,
            requires=self.requires,
            artifact_path=artifact_path,
        )


def _runtime_decl(data: dict, section: str) -> RuntimeDecl:
    try:
        return RuntimeDecl(module=data["module"], class_name=data["class"])
    except KeyError as exc:
        raise ValueError(f"Manifest section [{section}] is missing '{exc.args[0]}'") from exc


def _runtime_section(data: dict, plugin_dir: Path) -> RuntimeSection | None:
    section = data.get("runtime")
    if section is None:
        return None

    try:
        artifact = section["artifact"]
        return RuntimeSection(
            kind=section["kind"],
            entry_module=section["entry_module"],
            entry_class=section["entry_class"],
            artifact_path=str((plugin_dir / artifact).resolve()),
        )
    except KeyError as exc:
        raise ValueError(f"Manifest section [runtime] is missing '{exc.args[0]}'") from exc


def _tuple_of_strings(data: dict, key: str) -> tuple[str, ...]:
    values = data.get(key, [])
    if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
        raise ValueError(f"Manifest key '{key}' must be a list of strings")
    return tuple(values)


def _user_files_manifest(data: dict) -> UserFilesManifest:
    section = data.get("user_files")
    if not isinstance(section, dict):
        return UserFilesManifest()

    files_data = section.get("files", [])
    if not isinstance(files_data, list):
        raise ValueError("Manifest section [user_files] key 'files' must be an array of tables")

    files: list[UserFileDecl] = []
    for entry in files_data:
        if not isinstance(entry, dict):
            raise ValueError("Manifest section [user_files] contains an invalid file entry")
        try:
            files.append(
                UserFileDecl(
                    source=entry["source"],
                    target=entry["target"],
                    kind=entry["kind"],
                    copy_if_missing=bool(entry.get("copy_if_missing", False)),
                )
            )
        except KeyError as exc:
            raise ValueError(
                f"Manifest section [user_files.files] is missing '{exc.args[0]}'"
            ) from exc

    return UserFilesManifest(
        preserve_user_files=bool(section.get("preserve_user_files", False)),
        files=tuple(files),
    )


def _provider_requests(data: dict) -> tuple[ProviderRequest, ...]:
    requests = data.get("provider_requests", [])
    if not isinstance(requests, list):
        raise ValueError("Manifest key 'provider_requests' must be an array of tables")

    parsed: list[ProviderRequest] = []
    for entry in requests:
        if not isinstance(entry, dict):
            raise ValueError("Manifest key 'provider_requests' contains an invalid entry")
        capability = entry.get("capability")
        provider = entry.get("provider")
        source = entry.get("source")
        if not isinstance(capability, str):
            raise ValueError("Manifest key 'provider_requests' requires 'capability' as a string")
        if provider is not None and not isinstance(provider, str):
            raise ValueError("Manifest key 'provider_requests' field 'provider' must be a string")
        if source is not None and not isinstance(source, str):
            raise ValueError("Manifest key 'provider_requests' field 'source' must be a string")
        parsed.append(ProviderRequest(capability=capability, provider=provider, source=source))
    return tuple(parsed)


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

    widgets_data = data.get("widgets", {})
    widgets = WidgetManifest(widgets_file=widgets_data.get("file"))

    plugin_dir = _plugin_root(path)
    runtime = _runtime_section(data, plugin_dir)

    logic = _runtime_decl(data["logic"], "logic") if "logic" in data else None
    provider = _runtime_decl(data["provider"], "provider") if "provider" in data else None
    if runtime and logic is not None:
        logic = RuntimeDecl(
            module=runtime.entry_module,
            class_name=runtime.entry_class,
            artifact_path=runtime.artifact_path,
        )
    if runtime and logic is None and plugin_type == _CONSUMER_TYPE:
        logic = RuntimeDecl(
            module=runtime.entry_module,
            class_name=runtime.entry_class,
            artifact_path=runtime.artifact_path,
        )
    if runtime and provider is not None:
        provider = RuntimeDecl(
            module=runtime.entry_module,
            class_name=runtime.entry_class,
            artifact_path=runtime.artifact_path,
        )
    if runtime and provider is None and plugin_type == _PROVIDER_TYPE:
        provider = RuntimeDecl(
            module=runtime.entry_module,
            class_name=runtime.entry_class,
            artifact_path=runtime.artifact_path,
        )

    manifest = PluginManifest(
        name=data["name"],
        plugin_type=plugin_type,
        version=data["version"],
        plugin_dir=plugin_dir,
        manifest_path=path,
        requires=_tuple_of_strings(data, "requires"),
        exports=_tuple_of_strings(data, "exports"),
        provider_requests=_provider_requests(data),
        runtime=runtime,
        logic=logic,
        provider=provider,
        widgets=widgets,
        editors_file=data.get("editors", {}).get("file"),
        user_files=_user_files_manifest(data),
    )

    if manifest.is_consumer and manifest.logic is None and manifest.runtime is None:
        raise ValueError(f"Consumer plugin '{manifest.name}' must declare [logic] or [runtime]")
    if manifest.is_provider and manifest.provider is None and manifest.runtime is None:
        raise ValueError(f"Provider plugin '{manifest.name}' must declare [provider] or [runtime]")
    if manifest.is_consumer and manifest.exports:
        raise ValueError(f"Consumer plugin '{manifest.name}' cannot declare exports")
    if manifest.is_provider and manifest.requires:
        raise ValueError(f"Provider plugin '{manifest.name}' cannot declare requires")
    if manifest.is_provider and manifest.provider_requests:
        raise ValueError(f"Provider plugin '{manifest.name}' cannot declare provider_requests")

    return manifest


def _plugin_root(path: Path) -> Path:
    """Return the plugin root for either legacy or packaged manifest layouts."""
    if path.parent.name == "_internal":
        return path.parent.parent
    return path.parent


def scan_plugins(plugins_dir: Path) -> list[PluginManifest]:
    """Return manifests for all plugins found in ``plugins_dir``.

    Preferred packaged layout:
      plugins/<name>/_internal/plugin.toml

    Legacy source layout:
      plugins/<name>/plugin.toml
    """
    manifests = []
    manifest_paths: set[Path] = set(plugins_dir.glob("*/_internal/plugin.toml"))
    manifest_paths.update(plugins_dir.glob("*/plugin.toml"))
    for manifest_path in sorted(manifest_paths):
        manifests.append(load_manifest(manifest_path))
    return manifests
