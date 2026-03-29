from __future__ import annotations

from tinycore.paths import AppPaths

from tinyqt.app_manifest_loader import load_tinyqt_app_manifests
from tinyqt.manifests import TinyQtAppManifest


def build_tinyqt_settings_manifest(paths: AppPaths) -> TinyQtAppManifest:
    """Build the native settings manifest from tinyqt_settings/manifest.toml."""
    manifest_path = paths.source_root / "tinyqt_settings" / "manifest.toml" if paths.source_root else None
    if manifest_path is None:
        raise RuntimeError("TinyQt settings manifest requires a source_root in source runtime mode")
    manifests = load_tinyqt_app_manifests(manifest_path, paths=paths)
    for manifest in manifests:
        if manifest.app_id == "tinyqt_settings.window":
            return manifest
    raise RuntimeError(f"Missing TinyQt settings manifest 'tinyqt_settings.window' in {manifest_path}")
