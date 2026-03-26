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

"""Synchronize packaged plugin user-facing files into their install targets."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from tinycore.log import get_logger

from .manifest import PluginManifest

_log = get_logger(__name__)


@dataclass(frozen=True)
class UserFileSyncResult:
    """Summary of a packaged user-file synchronization pass."""

    installed: int = 0
    preserved: int = 0
    missing_sources: int = 0
    left_unset: int = 0

    def merge(self, other: "UserFileSyncResult") -> "UserFileSyncResult":
        return UserFileSyncResult(
            installed=self.installed + other.installed,
            preserved=self.preserved + other.preserved,
            missing_sources=self.missing_sources + other.missing_sources,
            left_unset=self.left_unset + other.left_unset,
        )


def _safe_target(app_root: Path, relative_target: str) -> Path:
    target = (app_root / relative_target).resolve()
    app_root_resolved = app_root.resolve()
    target.relative_to(app_root_resolved)
    return target


def sync_user_files(app_root: Path, manifests: list[PluginManifest]) -> UserFileSyncResult:
    """Copy packaged user files into their install targets without overwriting user edits."""
    total = UserFileSyncResult()
    for manifest in manifests:
        if not manifest.user_files.preserve_user_files:
            continue

        plugin_result = UserFileSyncResult()
        for entry in manifest.user_files.files:
            source = (manifest.plugin_dir / entry.source).resolve()
            target = _safe_target(app_root, entry.target)

            if not source.exists():
                _log.warning(
                    "plugin user file source missing  plugin=%s  source=%s",
                    manifest.name,
                    source,
                )
                plugin_result = plugin_result.merge(UserFileSyncResult(missing_sources=1))
                continue

            if source == target:
                continue

            if target.exists():
                plugin_result = plugin_result.merge(UserFileSyncResult(preserved=1))
                continue

            if not entry.copy_if_missing and manifest.user_files.preserve_user_files:
                plugin_result = plugin_result.merge(UserFileSyncResult(left_unset=1))
                continue

            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            plugin_result = plugin_result.merge(UserFileSyncResult(installed=1))

        if plugin_result != UserFileSyncResult():
            _log.info(
                "plugin user files synced  plugin=%s  installed=%d  preserved=%d  left_unset=%d  missing=%d",
                manifest.name,
                plugin_result.installed,
                plugin_result.preserved,
                plugin_result.left_unset,
                plugin_result.missing_sources,
            )
        total = total.merge(plugin_result)

    return total
