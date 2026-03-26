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

"""Helpers for loading plugin runtime code from either source or packaged artifacts."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
import zipfile


def _runtime_cache_dir(artifact: Path) -> Path:
    stamp = artifact.stat().st_mtime_ns
    return artifact.parent.parent / "_internal" / "_runtime_cache" / f"{artifact.stem}-{stamp}"


def _materialize_runtime_artifact(artifact: Path) -> Path:
    if artifact.is_dir():
        return artifact

    cache_dir = _runtime_cache_dir(artifact)
    if cache_dir.exists():
        return cache_dir

    cache_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(artifact) as zf:
        zf.extractall(cache_dir)
    return cache_dir


def ensure_runtime_import_path(artifact_path: str | None) -> str | None:
    """Put a packaged runtime artifact at the front of ``sys.path`` when present."""
    if not artifact_path:
        return None

    artifact = Path(artifact_path).resolve()
    import_root = _materialize_runtime_artifact(artifact)
    resolved = str(import_root.resolve())
    if resolved in sys.path:
        sys.path.remove(resolved)
    sys.path.insert(0, resolved)
    importlib.invalidate_caches()
    return resolved


def load_runtime_class(module_path: str, class_name: str, artifact_path: str | None = None):
    """Import and return a plugin runtime class from source or packaged runtime."""
    ensure_runtime_import_path(artifact_path)
    mod = importlib.import_module(module_path)
    return getattr(mod, class_name)
