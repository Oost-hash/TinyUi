from __future__ import annotations

from runtime.app.paths import AppPaths


def test_app_paths_detect_uses_src_as_source_root() -> None:
    paths = AppPaths.detect()

    assert paths.source_root is not None
    assert paths.source_root.name == "src"
    assert paths.app_root == paths.source_root
    assert paths.host_dir == paths.source_root / "plugins" / "tinyui"
    assert paths.plugins_dir == paths.source_root / "plugins"
