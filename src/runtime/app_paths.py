"""Resolved application paths for source and frozen runtime modes."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppPaths:
    app_root:    Path
    config_dir:  Path
    plugins_dir: Path
    data_dir:    Path
    source_root: Path | None = None
    frozen_root: Path | None = None

    @classmethod
    def detect(cls) -> "AppPaths":
        if getattr(sys, "frozen", False):
            app_root = Path(sys.executable).resolve().parent
            meipass = getattr(sys, "_MEIPASS", None)
            frozen_root = Path(meipass).resolve() if isinstance(meipass, str) else app_root / "_runtime"
            return cls(
                app_root=app_root,
                config_dir=app_root / "config",
                plugins_dir=app_root / "plugins",
                data_dir=app_root / "data",
                source_root=None,
                frozen_root=frozen_root,
            )

        source_root = Path(__file__).resolve().parents[1]
        repo_root = source_root.parent
        return cls(
            app_root=source_root,
            config_dir=repo_root / "data" / "config",
            plugins_dir=source_root / "plugins",
            data_dir=repo_root / "data" / "state",
            source_root=source_root,
            frozen_root=None,
        )

    def qml_dir(self, package: str) -> Path:
        if self.frozen_root is not None:
            return self.frozen_root / package / "qml"
        if self.source_root is None:
            raise RuntimeError(f"No source root available for package '{package}'")
        return self.source_root / package / "qml"
