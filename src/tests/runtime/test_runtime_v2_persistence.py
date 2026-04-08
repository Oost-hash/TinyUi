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

"""Tests for runtime V2 persistence contracts."""

from __future__ import annotations

import json

from runtimeV2.persistence.config_sets import ConfigSetCatalog
from runtimeV2.persistence.contracts import PersistencePaths
from runtimeV2.persistence.schemas.settings import SettingDecl
from runtimeV2.persistence.settings import SettingsStore
from runtimeV2.persistence.widget_config import WidgetConfigStore


def _paths(tmp_path) -> PersistencePaths:
    base_dir = tmp_path / "TinyUi"
    config_root = base_dir / "config"
    return PersistencePaths(
        base_dir=base_dir,
        config_root=config_root,
        cache_dir=base_dir / "cache",
        logs_dir=base_dir / "logs",
        bootstrap_path=base_dir / "bootstrap.toml",
        config_sets_path=config_root / "config_sets.json",
    )


def test_config_set_catalog_can_set_active_rename_and_delete(tmp_path) -> None:
    """Config set catalog should own active-set and catalog mutations."""

    paths = _paths(tmp_path)
    catalog = ConfigSetCatalog(paths)

    created = catalog.create_set("race", "Race")
    assert created.id == "race"
    assert catalog.set_active("race") is True
    assert catalog.active_set_id() == "race"
    assert 'active_set = "race"' in paths.bootstrap_path.read_text(encoding="utf-8")

    assert catalog.rename_set("race", "Race Weekend") is True
    renamed = next(item for item in catalog.list_sets() if item.id == "race")
    assert renamed.name == "Race Weekend"

    assert catalog.delete_set("race") is False
    assert catalog.set_active("default") is True
    assert catalog.delete_set("race") is True
    assert all(item.id != "race" for item in catalog.list_sets())


def test_settings_store_loads_only_registered_and_valid_values(tmp_path) -> None:
    """Settings store should ignore unknown keys and invalid persisted values."""

    paths = _paths(tmp_path)
    settings = SettingsStore(paths, "default")
    namespace_dir = paths.namespace_dir("default", "tinyui")
    namespace_dir.mkdir(parents=True, exist_ok=True)
    (namespace_dir / SettingsStore.SETTINGS_FILE).write_text(
        json.dumps(
            {
                "showClock": False,
                "refreshRate": "fast",
                "unused": 123,
            }
        ),
        encoding="utf-8",
    )

    settings.register_specs(
        {
            "tinyui": [
                SettingDecl(key="showClock", label="Show Clock", type="bool", default=True),
                SettingDecl(key="refreshRate", label="Refresh Rate", type="int", default=60),
            ]
        }
    )

    assert settings.get("tinyui", "showClock") is False
    assert settings.get("tinyui", "refreshRate") == 60
    assert settings.namespace_values("tinyui") == {
        "showClock": False,
        "refreshRate": 60,
    }


def test_widget_config_store_can_set_and_reset_widget_values(tmp_path) -> None:
    """Widget config store should own widget value persistence."""

    paths = _paths(tmp_path)
    store = WidgetConfigStore(paths, "default")

    assert store.set_widget_values("overlay.main", "speed", {"units": "kph"}) is True
    config = store.get_widget("overlay.main", "speed")
    assert config is not None
    assert config.values == {"units": "kph"}

    assert store.set_widget_values("overlay.main", "speed", {"precision": 1}) is True
    updated = store.get_widget("overlay.main", "speed")
    assert updated is not None
    assert updated.values == {"units": "kph", "precision": 1}

    assert store.reset_widget_values("overlay.main", "speed") is True
    reset = store.get_widget("overlay.main", "speed")
    assert reset is not None
    assert reset.values == {}
