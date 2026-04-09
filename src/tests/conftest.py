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

"""Pytest configuration for TinyUI tests."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Generator
from unittest.mock import patch

import pytest

from runtimeV2.paths.contracts import RuntimePaths
from runtimeV2.plugins.capabilities.discovery import PluginDiscoveryCapability
from runtimeV2.runtime import RuntimeV2
from runtimeV2.startup import get_runtime_v2_result, startup_runtime_v2

# Add src to Python path for all tests
src_path = str(Path(__file__).parent.parent)
if src_path not in sys.path:
    sys.path.insert(0, src_path)


def _coerce_runtime_paths(paths: object) -> RuntimePaths:
    if isinstance(paths, RuntimePaths):
        runtime_paths = paths
    else:
        runtime_paths = RuntimePaths(
            app_root=Path(getattr(paths, "app_root")),
            config_dir=Path(getattr(paths, "config_dir")),
            host_dir=Path(getattr(paths, "host_dir")),
            plugins_dir=Path(getattr(paths, "plugins_dir")),
            data_dir=Path(getattr(paths, "data_dir")),
            source_root=_optional_path(paths, "source_root"),
            frozen_root=_optional_path(paths, "frozen_root"),
        )

    runtime_paths.config_dir.mkdir(parents=True, exist_ok=True)
    runtime_paths.data_dir.mkdir(parents=True, exist_ok=True)
    return runtime_paths


def _optional_path(paths: object, name: str) -> Path | None:
    value = getattr(paths, name, None)
    return None if value is None else Path(value)


def _runtime_from_last_startup() -> RuntimeV2:
    result = get_runtime_v2_result()
    if result is None:
        raise RuntimeError("Runtime V2 startup result is not available")
    return result.runtime


def cleanup_test_runtime(runtime: RuntimeV2) -> None:
    """Shut down a test runtime and remove its import roots from sys.path."""

    try:
        runtime.begin_shutdown("test_cleanup")
    except Exception:
        pass

    try:
        discovery = runtime.capability("plugin_discovery", PluginDiscoveryCapability)
    except KeyError:
        discovery = None

    if discovery is not None:
        for import_root in discovery.import_roots():
            import_root_text = str(import_root)
            if import_root_text in sys.path:
                sys.path.remove(import_root_text)

    import runtimeV2.startup as startup_module

    startup_module._runtime_v2_result = None


@pytest.fixture
def booted_runtime() -> Generator[RuntimeV2, None, None]:
    """Create a fully booted RuntimeV2 using the default repository paths."""

    result = startup_runtime_v2()
    if not result.ok:
        pytest.skip(result.error_message or "Runtime V2 startup failed")

    runtime = _runtime_from_last_startup()
    try:
        yield runtime
    finally:
        cleanup_test_runtime(runtime)


def create_test_runtime_with_paths(paths: object) -> RuntimeV2:
    """Create a booted RuntimeV2 with test-specific runtime paths."""

    runtime_paths = _coerce_runtime_paths(paths)
    with patch("runtimeV2.paths.startup_shutdown.startup.detect_runtime_paths", return_value=runtime_paths):
        result = startup_runtime_v2()
    if not result.ok:
        raise RuntimeError(result.error_message or "Runtime V2 startup failed")
    return _runtime_from_last_startup()


def create_minimal_test_runtime(_bus: object | None = None) -> RuntimeV2:
    """Create a minimal booted RuntimeV2 using the default repository paths."""

    result = startup_runtime_v2()
    if not result.ok:
        raise RuntimeError(result.error_message or "Runtime V2 startup failed")
    return _runtime_from_last_startup()

