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

"""Tests for the persistence domain."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Generator

import pytest

from runtime.persistence import (
    ConfigResolver,
    ConfigSet,
    ConfigSetManager,
    SettingsRegistry,
    ScopedSettings,
    WidgetInstanceConfig,
    WidgetConfigStore,
    startup_persistence,
    get_persistence_result,
)
from runtime_schema import SettingsSpec


class TestConfigResolver:
    """Tests for ConfigResolver."""

    def test_base_dir_is_path(self) -> None:
        resolver = ConfigResolver()
        assert isinstance(resolver.base_dir, Path)

    def test_config_root_is_base_dir_child(self) -> None:
        resolver = ConfigResolver()
        # By default, config_root is base_dir / "config"
        assert resolver.config_root.parent == resolver.base_dir
        assert resolver.config_root.name == "config"

    def test_cache_dir_is_base_dir_child(self) -> None:
        resolver = ConfigResolver()
        assert resolver.cache_dir.parent == resolver.base_dir
        assert resolver.cache_dir.name == "cache"

    def test_logs_dir_is_base_dir_child(self) -> None:
        resolver = ConfigResolver()
        assert resolver.logs_dir.parent == resolver.base_dir
        assert resolver.logs_dir.name == "logs"

    def test_config_set_dir(self) -> None:
        resolver = ConfigResolver()
        set_dir = resolver.config_set_dir("race")
        assert set_dir.parent == resolver.config_root
        assert set_dir.name == "race"

    def test_namespace_dir(self) -> None:
        resolver = ConfigResolver()
        ns_dir = resolver.namespace_dir("default", "tinyui")
        assert ns_dir.parent == resolver.config_set_dir("default")
        assert ns_dir.name == "tinyui"


class TestConfigSetManager:
    """Tests for ConfigSetManager."""

    @pytest.fixture
    def temp_resolver(self) -> Generator[ConfigResolver, None, None]:
        with tempfile.TemporaryDirectory() as tmp:
            # Create a mock resolver that uses temp dir
            resolver = ConfigResolver()
            # Monkey-patch to use temp dir
            resolver._base_dir = Path(tmp)
            resolver._bootstrap = {}
            yield resolver

    def test_default_set_exists(self, temp_resolver: ConfigResolver) -> None:
        manager = ConfigSetManager(temp_resolver)
        assert "default" in [s.id for s in manager.list_sets()]

    def test_active_is_default_initially(self, temp_resolver: ConfigResolver) -> None:
        manager = ConfigSetManager(temp_resolver)
        assert manager.get_active_id() == "default"
        assert manager.get_active().id == "default"

    def test_create_set(self, temp_resolver: ConfigResolver) -> None:
        manager = ConfigSetManager(temp_resolver)
        new_set = manager.create_set("race", "Race Mode", "For racing")
        assert new_set is not None
        assert new_set.id == "race"
        assert new_set.name == "Race Mode"
        assert "race" in [s.id for s in manager.list_sets()]

    def test_cannot_create_duplicate_set(self, temp_resolver: ConfigResolver) -> None:
        manager = ConfigSetManager(temp_resolver)
        result = manager.create_set("default", "Duplicate")
        assert result is None

    def test_set_active(self, temp_resolver: ConfigResolver) -> None:
        manager = ConfigSetManager(temp_resolver)
        manager.create_set("race", "Race Mode")
        assert manager.set_active("race") is True
        assert manager.get_active_id() == "race"

    def test_set_active_nonexistent(self, temp_resolver: ConfigResolver) -> None:
        manager = ConfigSetManager(temp_resolver)
        assert manager.set_active("nonexistent") is False

    def test_cannot_delete_default(self, temp_resolver: ConfigResolver) -> None:
        manager = ConfigSetManager(temp_resolver)
        assert manager.delete_set("default") is False

    def test_cannot_delete_active(self, temp_resolver: ConfigResolver) -> None:
        manager = ConfigSetManager(temp_resolver)
        manager.create_set("race", "Race Mode")
        manager.set_active("race")
        assert manager.delete_set("race") is False

    def test_delete_set(self, temp_resolver: ConfigResolver) -> None:
        manager = ConfigSetManager(temp_resolver)
        manager.create_set("temp", "Temporary")
        assert manager.delete_set("temp") is True
        assert "temp" not in [s.id for s in manager.list_sets()]

    def test_rename_set(self, temp_resolver: ConfigResolver) -> None:
        manager = ConfigSetManager(temp_resolver)
        assert manager.rename_set("default", "New Default") is True
        assert manager.get_active().name == "New Default"


class TestSettingsRegistry:
    """Tests for SettingsRegistry."""

    @pytest.fixture
    def temp_registry(self) -> Generator[SettingsRegistry, None, None]:
        with tempfile.TemporaryDirectory() as tmp:
            resolver = ConfigResolver()
            resolver._base_dir = Path(tmp)
            resolver._bootstrap = {}
            registry = SettingsRegistry(resolver, "default")
            yield registry

    def test_register_and_get(self, temp_registry: SettingsRegistry) -> None:
        spec = SettingsSpec(
            key="test_setting",
            label="Test Setting",
            default="default_value",
            type="str",
        )
        temp_registry.register("test_ns", spec)
        assert temp_registry.get("test_ns", "test_setting") == "default_value"

    def test_set_and_get(self, temp_registry: SettingsRegistry) -> None:
        spec = SettingsSpec(
            key="test_setting",
            label="Test Setting",
            default="default_value",
            type="str",
        )
        temp_registry.register("test_ns", spec)
        temp_registry.set("test_ns", "test_setting", "new_value")
        assert temp_registry.get("test_ns", "test_setting") == "new_value"

    def test_scoped(self, temp_registry: SettingsRegistry) -> None:
        spec = SettingsSpec(
            key="test_setting",
            label="Test Setting",
            default="default_value",
            type="str",
        )
        temp_registry.register("test_ns", spec)
        scoped = temp_registry.scoped("test_ns")
        assert isinstance(scoped, ScopedSettings)
        assert scoped.get("test_setting") == "default_value"

    def test_save_and_load(self, temp_registry: SettingsRegistry) -> None:
        spec = SettingsSpec(
            key="test_setting",
            label="Test Setting",
            default="default_value",
            type="str",
        )
        temp_registry.register("test_ns", spec)
        temp_registry.set("test_ns", "test_setting", "saved_value")
        temp_registry.save("test_ns")

        # Load into new registry
        new_registry = SettingsRegistry(
            temp_registry._resolver, temp_registry._set_id
        )
        new_registry.register("test_ns", spec)
        new_registry.load_persisted()
        assert new_registry.get("test_ns", "test_setting") == "saved_value"


class TestWidgetConfigStore:
    """Tests for WidgetConfigStore."""

    @pytest.fixture
    def temp_store(self) -> Generator[WidgetConfigStore, None, None]:
        with tempfile.TemporaryDirectory() as tmp:
            resolver = ConfigResolver()
            resolver._base_dir = Path(tmp)
            resolver._bootstrap = {}
            store = WidgetConfigStore(resolver, "default")
            yield store

    def test_load_empty(self, temp_store: WidgetConfigStore) -> None:
        configs = temp_store.load_for_overlay("test_overlay")
        assert configs == []

    def test_save_and_load(self, temp_store: WidgetConfigStore) -> None:
        configs = [
            WidgetInstanceConfig(
                widget_id="fuel",
                enabled=True,
                position=(100, 200),
                values={"color": "#ff0000"},
            ),
            WidgetInstanceConfig(
                widget_id="speed",
                enabled=False,
                position=(300, 400),
                values={"label": "Speed"},
            ),
        ]
        temp_store.save_for_overlay("test_overlay", configs)

        loaded = temp_store.load_for_overlay("test_overlay")
        assert len(loaded) == 2
        assert loaded[0].widget_id == "fuel"
        assert loaded[0].enabled is True
        assert loaded[0].position == (100, 200)
        assert loaded[0].values["color"] == "#ff0000"

    def test_update_widget(self, temp_store: WidgetConfigStore) -> None:
        configs = [
            WidgetInstanceConfig(widget_id="fuel", values={"color": "#ff0000"}),
        ]
        temp_store.save_for_overlay("test_overlay", configs)

        result = temp_store.update_widget("test_overlay", "fuel", {"threshold": 10})
        assert result is True

        loaded = temp_store.load_for_overlay("test_overlay")
        assert loaded[0].values["color"] == "#ff0000"
        assert loaded[0].values["threshold"] == 10

    def test_update_widget_not_found(self, temp_store: WidgetConfigStore) -> None:
        result = temp_store.update_widget("test_overlay", "nonexistent", {"a": 1})
        assert result is False

    def test_set_widget_enabled(self, temp_store: WidgetConfigStore) -> None:
        configs = [WidgetInstanceConfig(widget_id="fuel", enabled=True)]
        temp_store.save_for_overlay("test_overlay", configs)

        result = temp_store.set_widget_enabled("test_overlay", "fuel", False)
        assert result is True

        loaded = temp_store.load_for_overlay("test_overlay")
        assert loaded[0].enabled is False

    def test_set_widget_position(self, temp_store: WidgetConfigStore) -> None:
        configs = [WidgetInstanceConfig(widget_id="fuel", position=(0, 0))]
        temp_store.save_for_overlay("test_overlay", configs)

        result = temp_store.set_widget_position("test_overlay", "fuel", 500, 600)
        assert result is True

        loaded = temp_store.load_for_overlay("test_overlay")
        assert loaded[0].position == (500, 600)


class TestStartup:
    """Tests for startup_persistence."""

    def test_startup_ok(self) -> None:
        result = startup_persistence()
        assert result.ok is True
        assert result.error_message == ""

    def test_get_persistence_result_after_startup(self) -> None:
        startup_persistence()
        persistence = get_persistence_result()
        assert persistence is not None
        assert persistence.settings is not None
        assert persistence.widget_store is not None
        assert persistence.config_manager is not None
