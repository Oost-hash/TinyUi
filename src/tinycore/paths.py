"""Shared application path ownership for source and packaged runtime modes."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppPaths:
    """Resolved application roots for the current runtime mode."""

    app_root: Path
    config_dir: Path
    plugins_dir: Path
    source_root: Path | None = None
    frozen_root: Path | None = None

    @classmethod
    def detect(cls) -> "AppPaths":
        """Resolve shared app roots for source mode or frozen mode."""
        if getattr(sys, "frozen", False):
            app_root = Path(sys.executable).resolve().parent
            meipass = getattr(sys, "_MEIPASS", None)
            frozen_root = Path(meipass).resolve() if isinstance(meipass, str) else app_root / "_runtime"
            return cls(
                app_root=app_root,
                config_dir=app_root / "config",
                plugins_dir=app_root / "plugins",
                source_root=None,
                frozen_root=frozen_root,
            )

        source_root = Path(__file__).resolve().parents[1]
        repo_root = source_root.parent
        return cls(
            app_root=source_root,
            config_dir=repo_root / "data" / "plugin-config",
            plugins_dir=source_root / "plugins",
            source_root=source_root,
            frozen_root=None,
        )

    def qml_dir(self, package: str) -> Path:
        """Return the QML directory for one package in the current runtime mode."""
        if self.frozen_root is not None:
            return self.frozen_root / package / "qml"
        if self.source_root is None:
            raise RuntimeError(f"No source root available for package '{package}'")
        return self.source_root / package / "qml"
