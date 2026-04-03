from __future__ import annotations

import zipfile
from pathlib import Path

from scripts.build_plugin import build_plugin


def test_build_plugin_uses_manifest_toml_and_freezes_runtime(tmp_path: Path) -> None:
    plugin_dir = tmp_path / "example_plugin"
    plugin_dir.mkdir(parents=True)
    (plugin_dir / "__init__.py").write_text("", encoding="utf-8")
    (plugin_dir / "manifest.toml").write_text(
        "\n".join(
            [
                "[plugin]",
                'id = "example_plugin"',
                'type = "plugin"',
                'version = "1.2.3"',
                'author = "Test"',
                'description = "Example"',
                "",
                "[[window]]",
                'id = "example.dialog"',
                'title = "Example"',
                'surface = "qml/surface.qml"',
            ]
        ),
        encoding="utf-8",
    )
    (plugin_dir / "plugin.py").write_text("def activate(ctx):\n    return None\n", encoding="utf-8")
    (plugin_dir / "qml").mkdir()
    (plugin_dir / "qml" / "surface.qml").write_text("import QtQuick\nItem {}", encoding="utf-8")
    (plugin_dir / "config" / "defaults").mkdir(parents=True)
    (plugin_dir / "config" / "defaults" / "example.json").write_text("{}", encoding="utf-8")

    output_dir = tmp_path / "dist"
    package_dir = build_plugin(plugin_dir, output_dir, clean=True, create_zip=True)

    assert package_dir == output_dir / "example_plugin"
    assert (package_dir / "_internal" / "manifest.toml").exists()
    assert (package_dir / "manifest.lock").exists()
    assert (package_dir / "runtime" / "example_plugin.pkg").exists()
    assert (package_dir / "config" / "defaults" / "example.json").exists()

    manifest_text = (package_dir / "_internal" / "manifest.toml").read_text(encoding="utf-8")
    assert '[plugin]' in manifest_text
    assert 'id = "example_plugin"' in manifest_text

    with zipfile.ZipFile(package_dir / "runtime" / "example_plugin.pkg") as archive:
        names = set(archive.namelist())
    assert "plugins/example_plugin/plugin.pyc" in names
    assert "plugins/example_plugin/qml/surface.qml" in names
    assert "plugins/example_plugin/manifest.toml" not in names

    zip_path = output_dir / "example_plugin-1.2.3.zip"
    assert zip_path.exists()
