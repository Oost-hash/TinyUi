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

"""Persistence domain startup."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from runtime.persistence.paths import ConfigResolver
from runtime.persistence.config_set import ConfigSetManager
from runtime.persistence.registry import SettingsRegistry
from runtime.persistence.widget_config import WidgetConfigStore

if TYPE_CHECKING:
    from runtime_schema import EventBus
    from runtime_schema.startup import StartupResult


# Module-level storage for persistence result after startup
_persistence_result: PersistenceStartupResult | None = None


def _is_frozen() -> bool:
    """Check if running in frozen mode."""
    return getattr(sys, "frozen", False)


def _find_repo_root() -> Path | None:
    """Find repository root for dev mode migration."""
    try:
        # Try to find repo root from current file location
        current_file = Path(__file__).resolve()
        # runtime/persistence/startup.py -> src/runtime/persistence/startup.py
        # Go up 4 levels to reach repo root
        repo_root = current_file.parents[3]
        data_config = repo_root / "data" / "config"
        if data_config.exists():
            return data_config
    except Exception:
        pass
    return None


def _migrate_legacy_settings(old_dir: Path, resolver: ConfigResolver) -> None:
    """Migrate old settings to new structure (default set)."""
    if not old_dir.exists():
        return

    for namespace_dir in old_dir.iterdir():
        if not namespace_dir.is_dir():
            continue

        old_settings = namespace_dir / "settings.json"
        if old_settings.exists():
            new_dir = resolver.namespace_dir("default", namespace_dir.name)
            new_dir.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(old_settings, new_dir / "settings.json")
            except Exception:
                pass  # Continue even if one namespace fails


def _migrate_if_needed(resolver: ConfigResolver) -> None:
    """Check for legacy settings and migrate if present."""
    if resolver.config_root.exists():
        return  # Already migrated or fresh install

    # Check legacy locations
    if _is_frozen():
        # Frozen mode: config was next to executable
        exe_dir = Path(sys.executable).parent
        old_config = exe_dir / "config"
        if old_config.exists():
            _migrate_legacy_settings(old_config, resolver)
    else:
        # Dev mode: config was in repo/data/config
        old_config = _find_repo_root()
        if old_config and old_config.exists():
            _migrate_legacy_settings(old_config, resolver)


class PersistenceStartupResult:
    """Result of persistence startup."""

    def __init__(
        self,
        resolver: ConfigResolver,
        config_manager: ConfigSetManager,
        settings: SettingsRegistry,
        widget_store: WidgetConfigStore,
        active_set_id: str,
    ) -> None:
        self.resolver = resolver
        self.config_manager = config_manager
        self.settings = settings
        self.widget_store = widget_store
        self.active_set_id = active_set_id


def startup_persistence(
    event_bus: EventBus | None = None,
) -> StartupResult:
    """Startup function for persistence domain.
    
    Following Test 28 pattern: domain starts itself, reports ok/error.
    
    This function:
    1. Determines all persistence paths
    2. Creates base directories
    3. Migrates legacy settings if present
    4. Loads config sets
    5. Creates settings registry for active set
    6. Creates widget config store
    
    After successful startup, use get_persistence_result() to access
    the created persistence objects.
    
    Returns:
        StartupResult with ok=True on success, ok=False + error_message on failure.
    """
    from runtime_schema.startup import startup_ok, startup_error
    global _persistence_result

    try:
        # 1. Determine all persistence paths
        resolver = ConfigResolver()

        # 2. Ensure base directories exist
        resolver.cache_dir.mkdir(parents=True, exist_ok=True)
        resolver.logs_dir.mkdir(parents=True, exist_ok=True)
        resolver.config_root.mkdir(parents=True, exist_ok=True)

        # 3. Migrate legacy settings if present
        _migrate_if_needed(resolver)

        # 4. Load config sets
        config_manager = ConfigSetManager(resolver)
        active_set = config_manager.get_active()

        # 5. Create settings registry for active set
        settings = SettingsRegistry(resolver, active_set.id)

        # 6. Create widget config store
        widget_store = WidgetConfigStore(resolver, active_set.id)

        # 7. Store result for later access
        _persistence_result = PersistenceStartupResult(
            resolver=resolver,
            config_manager=config_manager,
            settings=settings,
            widget_store=widget_store,
            active_set_id=active_set.id,
        )

        return startup_ok()

    except Exception as e:
        _persistence_result = None
        return startup_error(f"Persistence startup failed: {e}")


def get_persistence_result() -> PersistenceStartupResult | None:
    """Get the result of the last successful persistence startup.
    
    Returns None if startup was not called or failed.
    """
    return _persistence_result
