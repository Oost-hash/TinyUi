"""Minimal packaged smoke for a built TinyUi distribution."""

from __future__ import annotations

import argparse
import os
import platform
import subprocess
import time
from pathlib import Path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a minimal packaged smoke for TinyUi.")
    parser.add_argument("--dist", default="dist/TinyUi", help="Path to the built TinyUi distribution directory.")
    parser.add_argument("--timeout", type=float, default=8.0, help="Seconds to allow the app to stay up before terminating it.")
    return parser.parse_args()


def _exe_path(dist_dir: Path) -> Path:
    exe_name = "TinyUi.exe" if platform.system() == "Windows" else "TinyUi"
    return dist_dir / exe_name


def _require_path(path: Path, label: str) -> None:
    if not path.exists():
        raise SystemExit(f"Missing {label}: {path}")


def _validate_layout(dist_dir: Path) -> Path:
    _require_path(dist_dir, "distribution directory")
    exe_path = _exe_path(dist_dir)
    _require_path(exe_path, "executable")
    _require_path(dist_dir / "libs", "libs directory")
    _require_path(dist_dir / "tinyui" / "manifest.toml", "promoted host manifest")
    _require_path(dist_dir / "plugins", "external plugins directory")
    _require_path(dist_dir / "themes", "themes directory")
    _require_path(dist_dir / "config", "config directory")
    _require_path(dist_dir / "data", "data directory")
    return exe_path


def _smoke_env() -> dict[str, str]:
    env = os.environ.copy()
    if platform.system() == "Linux":
        env.setdefault("QT_QPA_PLATFORM", "offscreen")
    return env


def main() -> int:
    args = _parse_args()
    dist_dir = Path(args.dist).resolve()
    exe_path = _validate_layout(dist_dir)

    proc = subprocess.Popen(
        [str(exe_path)],
        cwd=str(dist_dir),
        env=_smoke_env(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        time.sleep(args.timeout)
        if proc.poll() not in (None, 0):
            return proc.returncode or 1
        proc.terminate()
        proc.wait(timeout=10)
        return 0
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=10)


if __name__ == "__main__":
    raise SystemExit(main())
