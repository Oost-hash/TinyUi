from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from tinycore.paths import AppPaths

from tinyqt.manifests import TinyQtAppManifest

from .devtools import build_tinyqt_devtools_manifest
from .settings import build_tinyqt_settings_manifest
from .tinyui import build_tinyui_manifest


@dataclass(frozen=True)
class FirstPartyFeatureSpec:
    feature_id: str
    app_id: str
    build_manifest: Callable[[AppPaths], TinyQtAppManifest]


FIRST_PARTY_FEATURES: tuple[FirstPartyFeatureSpec, ...] = (
    FirstPartyFeatureSpec(
        feature_id="main",
        app_id="tinyui.main",
        build_manifest=build_tinyui_manifest,
    ),
    FirstPartyFeatureSpec(
        feature_id="settings",
        app_id="tinyqt_settings.window",
        build_manifest=build_tinyqt_settings_manifest,
    ),
    FirstPartyFeatureSpec(
        feature_id="devtools",
        app_id="tinyqt_devtools.window",
        build_manifest=build_tinyqt_devtools_manifest,
    ),
)


def build_first_party_manifests(paths: AppPaths) -> dict[str, TinyQtAppManifest]:
    """Return the static manifest map for first-party hosted surfaces."""
    return {
        spec.app_id: spec.build_manifest(paths)
        for spec in FIRST_PARTY_FEATURES
    }


def get_first_party_manifest(paths: AppPaths, app_id: str) -> TinyQtAppManifest:
    """Resolve a first-party hosted surface manifest by id."""
    manifests = build_first_party_manifests(paths)
    try:
        return manifests[app_id]
    except KeyError as exc:
        raise KeyError(f"Unknown TinyQt first-party manifest '{app_id}'") from exc
