from __future__ import annotations

import tomllib
from pathlib import Path

from tinycore.paths import AppPaths

from .manifests import (
    TinyQtAppManifest,
    TinyQtMenuItemManifest,
    TinyQtPanelManifest,
    TinyQtShellManifest,
    TinyQtWindowManifest,
    validate_manifest,
)


def _as_bool(data: dict[str, object], key: str, default: bool) -> bool:
    value = data.get(key, default)
    if not isinstance(value, bool):
        raise ValueError(f"Manifest key '{key}' must be a boolean")
    return value


def _as_str(data: dict[str, object], key: str, default: str | None = None) -> str | None:
    value = data.get(key, default)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"Manifest key '{key}' must be a string")
    return value


def _as_int(data: dict[str, object], key: str, default: int | None = None) -> int | None:
    value = data.get(key, default)
    if value is None:
        return None
    if not isinstance(value, int):
        raise ValueError(f"Manifest key '{key}' must be an integer")
    return value


def _as_str_tuple(data: dict[str, object], key: str) -> tuple[str, ...]:
    raw = data.get(key, [])
    if not isinstance(raw, list) or not all(isinstance(item, str) for item in raw):
        raise ValueError(f"Manifest key '{key}' must be a list of strings")
    return tuple(raw)


def _resolve_root_qml(paths: AppPaths, value: str | None) -> Path | None:
    if value is None:
        return None
    if paths.source_root is None:
        raise RuntimeError("TinyQt app manifest loading requires source_root in source runtime mode")
    return (paths.source_root / value).resolve()


def load_tinyqt_app_manifests(path: Path, *, paths: AppPaths) -> tuple[TinyQtAppManifest, ...]:
    """Load first-party TinyQt app manifests from one TOML file."""
    with path.open("rb") as handle:
        data = tomllib.load(handle)

    apps = data.get("app", [])
    if not isinstance(apps, list):
        raise ValueError(f"{path} must declare [[app]] tables")

    manifests: list[TinyQtAppManifest] = []
    for entry in apps:
        if not isinstance(entry, dict):
            raise ValueError(f"{path} contains an invalid [[app]] entry")

        shell_data = entry.get("shell", {})
        window_data = entry.get("window", {})
        if not isinstance(shell_data, dict):
            raise ValueError(f"{path} app '{entry.get('app_id', '<unknown>')}' has invalid [shell]")
        if not isinstance(window_data, dict):
            raise ValueError(f"{path} app '{entry.get('app_id', '<unknown>')}' has invalid [window]")

        menu_items_data = entry.get("menu_items", [])
        panels_data = entry.get("panels", [])
        if not isinstance(menu_items_data, list):
            raise ValueError(f"{path} app '{entry.get('app_id', '<unknown>')}' has invalid [[menu_items]]")
        if not isinstance(panels_data, list):
            raise ValueError(f"{path} app '{entry.get('app_id', '<unknown>')}' has invalid [[panels]]")

        menu_items = tuple(
            TinyQtMenuItemManifest(
                label=_as_str(item, "label", "") or "",
                action=_as_str(item, "action"),
                separator=_as_bool(item, "separator", False),
                requires_feature=_as_str(item, "requires_feature"),
            )
            for item in menu_items_data
            if isinstance(item, dict)
        )
        panels = tuple(
            TinyQtPanelManifest(
                panel_id=_as_str(panel, "panel_id", "") or "",
                label=_as_str(panel, "label", "") or "",
                qml_type=_as_str(panel, "qml_type", "") or "",
                package=_as_str(panel, "package", "") or "",
                load_policy=_as_str(panel, "load_policy", "lazy") or "lazy",
                required_singletons=_as_str_tuple(panel, "required_singletons"),
            )
            for panel in panels_data
            if isinstance(panel, dict)
        )

        manifests.append(
            validate_manifest(
                TinyQtAppManifest(
                    app_id=_as_str(entry, "app_id", "") or "",
                    title=_as_str(entry, "title", "") or "",
                    root_qml=_resolve_root_qml(paths, _as_str(entry, "root_qml")),
                    shell=TinyQtShellManifest(
                        use_window_menu_bar=_as_bool(shell_data, "use_window_menu_bar", True),
                        use_tab_bar=_as_bool(shell_data, "use_tab_bar", False),
                        use_status_bar=_as_bool(shell_data, "use_status_bar", False),
                        lazy_panel_loading=_as_bool(shell_data, "lazy_panel_loading", True),
                        native_chrome_platforms=_as_str_tuple(shell_data, "native_chrome_platforms")
                        or ("linux", "osx"),
                    ),
                    window=TinyQtWindowManifest(
                        window_kind=_as_str(window_data, "window_kind", "main") or "main",
                        presentation=_as_str(window_data, "presentation", "qml") or "qml",
                        restore_state_scope=_as_str(window_data, "restore_state_scope"),
                        eyebrow=_as_str(window_data, "eyebrow", "") or "",
                        subtitle=_as_str(window_data, "subtitle", "") or "",
                        default_width=_as_int(window_data, "default_width"),
                        default_height=_as_int(window_data, "default_height"),
                        min_width=_as_int(window_data, "min_width"),
                        min_height=_as_int(window_data, "min_height"),
                    ),
                    menu_items=menu_items,
                    panels=panels,
                    required_singletons=_as_str_tuple(entry, "required_singletons"),
                    optional_features=_as_str_tuple(entry, "optional_features"),
                )
            )
        )

    return tuple(manifests)
