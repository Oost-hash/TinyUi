"""Resolved application paths for source and frozen runtime modes."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path


def _os_config_dir(app_name: str) -> Path:
    """Return the OS-level user config directory for the given app name."""
    if sys.platform == "win32":
        base = os.getenv("APPDATA", str(Path.home()))
        return Path(base) / app_name
    # Linux / macOS — XDG_CONFIG_HOME or ~/.config
    xdg = os.getenv("XDG_CONFIG_HOME", str(Path.home() / ".config"))
    return Path(xdg) / app_name


@dataclass(frozen=True)
class AppPaths:
    app_root:    Path
    config_dir:  Path
    host_dir:    Path
    plugins_dir: Path
    data_dir:    Path
    source_root: Path | None = None
    frozen_root: Path | None = None

    @classmethod
    def detect(cls) -> "AppPaths":
        if getattr(sys, "frozen", False):
            app_root = Path(sys.executable).resolve().parent
            meipass = getattr(sys, "_MEIPASS", None)
            frozen_root = Path(meipass).resolve() if isinstance(meipass, str) else app_root / "libs"
            paths = cls(
                app_root=app_root,
                config_dir=app_root / "config",
                host_dir=app_root / "tinyui",
                plugins_dir=app_root / "plugins",
                data_dir=app_root / "data",
                source_root=None,
                frozen_root=frozen_root,
            )
        else:
            source_root = Path(__file__).resolve().parents[2]
            repo_root = source_root.parent
            paths = cls(
                app_root=source_root,
                config_dir=repo_root / "data" / "config",
                host_dir=source_root / "plugins" / "tinyui",
                plugins_dir=source_root / "plugins",
                data_dir=repo_root / "data" / "state",
                source_root=source_root,
                frozen_root=None,
            )

        paths.config_dir.mkdir(parents=True, exist_ok=True)
        paths.data_dir.mkdir(parents=True, exist_ok=True)
        return paths

    def qml_dir(self, package: str) -> Path:
        if self.frozen_root is not None:
            return self.frozen_root / package / "qml"
        if self.source_root is None:
            raise RuntimeError(f"No source root available for package '{package}'")
        return self.source_root / package / "qml"
