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
"""Static manifest contracts for first-party TinyQt hosted surfaces."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

_VALID_LOAD_POLICIES = frozenset({"lazy", "eager"})


@dataclass(frozen=True)
class TinyQtPanelManifest:
    panel_id: str
    label: str
    qml_type: str
    package: str
    load_policy: str = "lazy"
    required_singletons: tuple[str, ...] = ()


@dataclass(frozen=True)
class TinyQtShellManifest:
    use_window_menu_bar: bool = True
    use_tab_bar: bool = False
    use_status_bar: bool = False
    lazy_panel_loading: bool = True
    native_chrome_platforms: tuple[str, ...] = ("linux", "osx")


@dataclass(frozen=True)
class TinyQtAppManifest:
    app_id: str
    title: str
    root_qml: Path | None
    shell: TinyQtShellManifest
    panels: tuple[TinyQtPanelManifest, ...] = ()
    required_singletons: tuple[str, ...] = ()
    optional_features: tuple[str, ...] = ()


def _normalize_names(values: tuple[str, ...], *, field_name: str, app_id: str) -> tuple[str, ...]:
    normalized: list[str] = []
    seen: set[str] = set()
    for raw in values:
        value = raw.strip()
        if not value:
            raise ValueError(f"Invalid TinyQt manifest '{app_id}': {field_name} contains an empty name")
        if value in seen:
            raise ValueError(f"Invalid TinyQt manifest '{app_id}': duplicate {field_name} entry '{value}'")
        seen.add(value)
        normalized.append(value)
    return tuple(normalized)


def validate_manifest(manifest: TinyQtAppManifest) -> TinyQtAppManifest:
    """Validate and normalize a TinyQt app manifest."""
    app_id = manifest.app_id.strip()
    title = manifest.title.strip()
    if not app_id:
        raise ValueError("Invalid TinyQt manifest: app_id must not be empty")
    if not title:
        raise ValueError(f"Invalid TinyQt manifest '{app_id}': title must not be empty")

    if manifest.shell.use_status_bar and not manifest.shell.use_window_menu_bar:
        raise ValueError(
            f"Invalid TinyQt manifest '{app_id}': status shell requires shared window/menu chrome"
        )
    if manifest.panels and not manifest.shell.use_tab_bar and len(manifest.panels) > 1:
        raise ValueError(
            f"Invalid TinyQt manifest '{app_id}': multiple panels require the shared tab bar"
        )

    panel_ids: set[str] = set()
    normalized_panels: list[TinyQtPanelManifest] = []
    for panel in manifest.panels:
        panel_id = panel.panel_id.strip()
        label = panel.label.strip()
        qml_type = panel.qml_type.strip()
        package = panel.package.strip()
        if not panel_id:
            raise ValueError(f"Invalid TinyQt manifest '{app_id}': panel_id must not be empty")
        if panel_id in panel_ids:
            raise ValueError(f"Invalid TinyQt manifest '{app_id}': duplicate panel_id '{panel_id}'")
        panel_ids.add(panel_id)
        if not label:
            raise ValueError(f"Invalid TinyQt manifest '{app_id}': panel '{panel_id}' has an empty label")
        if not qml_type:
            raise ValueError(f"Invalid TinyQt manifest '{app_id}': panel '{panel_id}' has an empty qml_type")
        if not package:
            raise ValueError(f"Invalid TinyQt manifest '{app_id}': panel '{panel_id}' has an empty package")
        load_policy = panel.load_policy.strip().lower()
        if load_policy not in _VALID_LOAD_POLICIES:
            raise ValueError(
                f"Invalid TinyQt manifest '{app_id}': panel '{panel_id}' has unsupported load_policy '{panel.load_policy}'"
            )
        normalized_panels.append(
            TinyQtPanelManifest(
                panel_id=panel_id,
                label=label,
                qml_type=qml_type,
                package=package,
                load_policy=load_policy,
                required_singletons=_normalize_names(
                    panel.required_singletons,
                    field_name=f"panel '{panel_id}' required_singletons",
                    app_id=app_id,
                ),
            )
        )

    return TinyQtAppManifest(
        app_id=app_id,
        title=title,
        root_qml=manifest.root_qml,
        shell=manifest.shell,
        panels=tuple(normalized_panels),
        required_singletons=_normalize_names(
            manifest.required_singletons,
            field_name="required_singletons",
            app_id=app_id,
        ),
        optional_features=_normalize_names(
            manifest.optional_features,
            field_name="optional_features",
            app_id=app_id,
        ),
    )


def validate_required_singletons(
    manifest: TinyQtAppManifest,
    available_singletons: set[str],
) -> tuple[str, ...]:
    """Return missing singleton names for diagnostics and host checks."""
    required = set(manifest.required_singletons)
    for panel in manifest.panels:
        required.update(panel.required_singletons)
    missing = sorted(name for name in required if name not in available_singletons)
    return tuple(missing)


def manifest_panel_labels(manifest: TinyQtAppManifest) -> list[str]:
    """Return panel labels in manifest order."""
    return [panel.label for panel in manifest.panels]


def manifest_eager_panel_indexes(manifest: TinyQtAppManifest) -> list[int]:
    """Return panel indexes that should load eagerly."""
    return [
        index
        for index, panel in enumerate(manifest.panels)
        if panel.load_policy == "eager"
    ]


def manifest_has_optional_feature(manifest: TinyQtAppManifest, feature_name: str) -> bool:
    """Return whether one optional feature is declared by the manifest."""
    return feature_name in manifest.optional_features
