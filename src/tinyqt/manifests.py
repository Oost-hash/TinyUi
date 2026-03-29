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
_VALID_MENU_ACTIONS = frozenset({"settings", "devtools", "close"})
_VALID_WINDOW_KINDS = frozenset({"main", "tool", "dialog"})
_VALID_WINDOW_PRESENTATIONS = frozenset({"qml", "native"})
_VALID_BUTTON_ROLES = frozenset({"primary", "secondary"})


@dataclass(frozen=True)
class TinyQtMenuItemManifest:
    label: str
    action: str | None = None
    separator: bool = False
    requires_feature: str | None = None


@dataclass(frozen=True)
class TinyQtButtonManifest:
    button_id: str
    label: str
    role: str = "secondary"


@dataclass(frozen=True)
class TinyQtToolbarManifest:
    toolbar_id: str
    panel_id: str
    compact: bool = False
    buttons: tuple[TinyQtButtonManifest, ...] = ()


@dataclass(frozen=True)
class TinyQtPanelManifest:
    panel_id: str
    label: str
    qml_type: str
    package: str
    subtitle: str = ""
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
class TinyQtChromeManifest:
    show_menu_button: bool = True
    show_title_text: bool = True
    show_caption_buttons: bool = True
    show_status_left_items: bool = True
    show_status_plugin_picker: bool = True


@dataclass(frozen=True)
class TinyQtWindowManifest:
    window_kind: str = "main"
    presentation: str = "qml"
    restore_state_scope: str | None = None
    eyebrow: str = ""
    subtitle: str = ""
    default_width: int | None = None
    default_height: int | None = None
    min_width: int | None = None
    min_height: int | None = None


@dataclass(frozen=True)
class TinyQtAppManifest:
    app_id: str
    title: str
    root_qml: Path | None
    shell: TinyQtShellManifest
    chrome: TinyQtChromeManifest = TinyQtChromeManifest()
    window: TinyQtWindowManifest = TinyQtWindowManifest()
    menu_items: tuple[TinyQtMenuItemManifest, ...] = ()
    buttons: tuple[TinyQtButtonManifest, ...] = ()
    toolbars: tuple[TinyQtToolbarManifest, ...] = ()
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
    window_kind = manifest.window.window_kind.strip().lower()
    presentation = manifest.window.presentation.strip().lower()
    eyebrow = manifest.window.eyebrow.strip()
    subtitle = manifest.window.subtitle.strip()
    if window_kind not in _VALID_WINDOW_KINDS:
        raise ValueError(
            f"Invalid TinyQt manifest '{app_id}': unsupported window_kind '{manifest.window.window_kind}'"
        )
    if presentation not in _VALID_WINDOW_PRESENTATIONS:
        raise ValueError(
            f"Invalid TinyQt manifest '{app_id}': unsupported presentation '{manifest.window.presentation}'"
        )
    if presentation == "native" and manifest.root_qml is not None:
        raise ValueError(
            f"Invalid TinyQt manifest '{app_id}': native window manifests must not declare root_qml"
        )
    if presentation == "qml" and manifest.root_qml is None:
        raise ValueError(
            f"Invalid TinyQt manifest '{app_id}': qml window manifests require root_qml"
        )
    for field_name in ("default_width", "default_height", "min_width", "min_height"):
        value = getattr(manifest.window, field_name)
        if value is not None and value <= 0:
            raise ValueError(
                f"Invalid TinyQt manifest '{app_id}': {field_name} must be positive when set"
            )

    if manifest.shell.use_status_bar and not manifest.shell.use_window_menu_bar:
        raise ValueError(
            f"Invalid TinyQt manifest '{app_id}': status shell requires shared window/menu chrome"
        )
    if manifest.panels and not manifest.shell.use_tab_bar and len(manifest.panels) > 1:
        raise ValueError(
            f"Invalid TinyQt manifest '{app_id}': multiple panels require the shared tab bar"
        )

    panel_ids: set[str] = set()
    button_ids: set[str] = set()
    normalized_panels: list[TinyQtPanelManifest] = []
    normalized_menu_items: list[TinyQtMenuItemManifest] = []
    normalized_buttons: list[TinyQtButtonManifest] = []
    normalized_toolbars: list[TinyQtToolbarManifest] = []

    for item in manifest.menu_items:
        label = item.label.strip()
        requires_feature = item.requires_feature.strip() if item.requires_feature else None
        action = item.action.strip().lower() if item.action else None
        if item.separator:
            normalized_menu_items.append(
                TinyQtMenuItemManifest(label="", action=None, separator=True)
            )
            continue
        if not label:
            raise ValueError(f"Invalid TinyQt manifest '{app_id}': menu item label must not be empty")
        if action not in _VALID_MENU_ACTIONS:
            raise ValueError(
                f"Invalid TinyQt manifest '{app_id}': unsupported menu action '{item.action}'"
            )
        normalized_menu_items.append(
            TinyQtMenuItemManifest(
                label=label,
                action=action,
                separator=False,
                requires_feature=requires_feature,
            )
        )

    for button in manifest.buttons:
        button_id = button.button_id.strip()
        label = button.label.strip()
        role = button.role.strip().lower()
        if not button_id:
            raise ValueError(f"Invalid TinyQt manifest '{app_id}': button_id must not be empty")
        if button_id in button_ids:
            raise ValueError(f"Invalid TinyQt manifest '{app_id}': duplicate button_id '{button_id}'")
        button_ids.add(button_id)
        if not label:
            raise ValueError(
                f"Invalid TinyQt manifest '{app_id}': button '{button_id}' has an empty label"
            )
        if role not in _VALID_BUTTON_ROLES:
            raise ValueError(
                f"Invalid TinyQt manifest '{app_id}': button '{button_id}' has unsupported role '{button.role}'"
            )
        normalized_buttons.append(
            TinyQtButtonManifest(
                button_id=button_id,
                label=label,
                role=role,
            )
        )

    for toolbar in manifest.toolbars:
        toolbar_id = toolbar.toolbar_id.strip()
        panel_id = toolbar.panel_id.strip()
        if not toolbar_id:
            raise ValueError(f"Invalid TinyQt manifest '{app_id}': toolbar_id must not be empty")
        if not panel_id:
            raise ValueError(
                f"Invalid TinyQt manifest '{app_id}': toolbar '{toolbar_id}' has an empty panel_id"
            )
        toolbar_button_ids: set[str] = set()
        normalized_toolbar_buttons: list[TinyQtButtonManifest] = []
        for button in toolbar.buttons:
            button_id = button.button_id.strip()
            label = button.label.strip()
            role = button.role.strip().lower()
            if not button_id:
                raise ValueError(
                    f"Invalid TinyQt manifest '{app_id}': toolbar '{toolbar_id}' contains an empty button_id"
                )
            if button_id in toolbar_button_ids:
                raise ValueError(
                    f"Invalid TinyQt manifest '{app_id}': toolbar '{toolbar_id}' has duplicate button_id '{button_id}'"
                )
            toolbar_button_ids.add(button_id)
            if not label:
                raise ValueError(
                    f"Invalid TinyQt manifest '{app_id}': toolbar '{toolbar_id}' button '{button_id}' has an empty label"
                )
            if role not in _VALID_BUTTON_ROLES:
                raise ValueError(
                    f"Invalid TinyQt manifest '{app_id}': toolbar '{toolbar_id}' button '{button_id}' has unsupported role '{button.role}'"
                )
            normalized_toolbar_buttons.append(
                TinyQtButtonManifest(button_id=button_id, label=label, role=role)
            )
        normalized_toolbars.append(
            TinyQtToolbarManifest(
                toolbar_id=toolbar_id,
                panel_id=panel_id,
                compact=toolbar.compact,
                buttons=tuple(normalized_toolbar_buttons),
            )
        )

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
                subtitle=panel.subtitle.strip(),
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

    for toolbar in normalized_toolbars:
        if toolbar.panel_id not in panel_ids:
            raise ValueError(
                f"Invalid TinyQt manifest '{app_id}': toolbar '{toolbar.toolbar_id}' references unknown panel '{toolbar.panel_id}'"
            )

    return TinyQtAppManifest(
        app_id=app_id,
        title=title,
        root_qml=manifest.root_qml,
        shell=manifest.shell,
        chrome=manifest.chrome,
        window=TinyQtWindowManifest(
            window_kind=window_kind,
            presentation=presentation,
            restore_state_scope=manifest.window.restore_state_scope,
            eyebrow=eyebrow,
            subtitle=subtitle,
            default_width=manifest.window.default_width,
            default_height=manifest.window.default_height,
            min_width=manifest.window.min_width,
            min_height=manifest.window.min_height,
        ),
        menu_items=tuple(normalized_menu_items),
        buttons=tuple(normalized_buttons),
        toolbars=tuple(normalized_toolbars),
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


def manifest_menu_items(manifest: TinyQtAppManifest) -> list[dict[str, object]]:
    """Return resolved menu items for a window host to expose to QML."""
    items: list[dict[str, object]] = []
    for item in manifest.menu_items:
        visible = True
        if item.requires_feature is not None:
            visible = manifest_has_optional_feature(manifest, item.requires_feature)
        items.append(
            {
                "label": item.label,
                "action": item.action,
                "separator": item.separator,
                "visible": visible,
            }
        )
    return items


def manifest_toolbars_for_panel(
    manifest: TinyQtAppManifest,
    panel_id: str,
) -> tuple[TinyQtToolbarManifest, ...]:
    """Return toolbar declarations for one panel in manifest order."""
    return tuple(toolbar for toolbar in manifest.toolbars if toolbar.panel_id == panel_id)
