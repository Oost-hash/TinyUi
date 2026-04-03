"""Minimal source-layout smoke for TinyUi."""

from __future__ import annotations

import argparse
import os
import platform
import subprocess
import sys
import time
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a minimal source-layout smoke for TinyUi.")
    parser.add_argument("--timeout", type=float, default=8.0, help="Seconds to allow the app to stay up before terminating it.")
    return parser.parse_args()


def _smoke_env() -> dict[str, str]:
    env = os.environ.copy()
    python_path_entries = [str(ROOT / "src")]
    existing_pythonpath = env.get("PYTHONPATH")
    if existing_pythonpath:
        python_path_entries.append(existing_pythonpath)
    env["PYTHONPATH"] = os.pathsep.join(python_path_entries)
    if platform.system() == "Linux":
        env.setdefault("QT_QPA_PLATFORM", "offscreen")
        env.setdefault("QT_QUICK_BACKEND", "software")
        env.setdefault("QSG_RHI_BACKEND", "software")
        env.setdefault("LIBGL_ALWAYS_SOFTWARE", "1")
        env.setdefault("XDG_RUNTIME_DIR", tempfile.gettempdir())
    return env


def main() -> int:
    args = _parse_args()
    proc = subprocess.Popen(
        [sys.executable, "-m", "boot"],
        cwd=str(ROOT),
        env=_smoke_env(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        time.sleep(args.timeout)
        if proc.poll() not in (None, 0):
            stdout, stderr = proc.communicate(timeout=5)
            output = "\n".join(part.strip() for part in (stdout, stderr) if part.strip())
            if output:
                print(output)
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
