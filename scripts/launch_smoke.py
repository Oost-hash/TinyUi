#  TinyUI
#  Copyright (C) 2026 Oost-hash
#
#  This file is part of TinyUI.
#
#  TinyUI is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  TinyUI is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  TinyUI builds on TinyPedal by s-victor (https://github.com/s-victor/TinyPedal),
#  licensed under GPLv3.
"""Launch TinyUI, wait for a startup marker, then close it again."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from collections import deque
from pathlib import Path
from typing import IO

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"
LAUNCH_MARKER = "launch_ready_for_exec"


def _build_command() -> list[str]:
    python = PYTHON if PYTHON.exists() else Path(sys.executable)
    return [str(python), str(SRC / "tinyui_boot.py")]


def _read_until_launch(
    stream: IO[str],
    *,
    timeout_seconds: float,
    tail: deque[str],
) -> bool:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        line = stream.readline()
        if line:
            text = line.rstrip()
            tail.append(text)
            print(text)
            if LAUNCH_MARKER in text:
                return True
            continue
        time.sleep(0.05)
    return False


def _terminate_process(process: subprocess.Popen[str], timeout_seconds: float) -> int:
    process.terminate()
    try:
        return process.wait(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        process.kill()
        return process.wait(timeout=timeout_seconds)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Launch TinyUI, print when it launches, and close it again."
    )
    parser.add_argument(
        "--launch-timeout",
        type=float,
        default=20.0,
        help="Seconds to wait for the launch marker before failing.",
    )
    parser.add_argument(
        "--linger",
        type=float,
        default=1.5,
        help="Seconds to keep the app running after launch was detected.",
    )
    parser.add_argument(
        "--shutdown-timeout",
        type=float,
        default=5.0,
        help="Seconds to wait for the process to exit after termination.",
    )
    parser.add_argument(
        "--tail-lines",
        type=int,
        default=25,
        help="Number of recent output lines to keep for failure reporting.",
    )
    args = parser.parse_args()

    command = _build_command()
    print(f"Launching: {' '.join(command)}")
    process = subprocess.Popen(
        command,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )

    assert process.stdout is not None
    tail: deque[str] = deque(maxlen=max(args.tail_lines, 1))

    try:
        launched = _read_until_launch(
            process.stdout,
            timeout_seconds=args.launch_timeout,
            tail=tail,
        )
        if not launched:
            if process.poll() is None:
                _terminate_process(process, args.shutdown_timeout)
            print("Launch failed: did not observe launch marker")
            if tail:
                print("--- recent output ---")
                for line in tail:
                    print(line)
            return 1

        print("Launched successfully")
        time.sleep(max(args.linger, 0.0))
        exit_code = _terminate_process(process, args.shutdown_timeout)
        print(f"Closed application (exit code {exit_code})")
        return 0
    finally:
        if process.poll() is None:
            _terminate_process(process, args.shutdown_timeout)


if __name__ == "__main__":
    raise SystemExit(main())
