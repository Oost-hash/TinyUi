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

from runtimeV2.persistence.backends import SQLiteDocumentBackend, create_persistence_backend
from runtimeV2.persistence.bootstrap import load_bootstrap, save_bootstrap
from runtimeV2.persistence.capabilities.settings_read import SettingsRead
from runtimeV2.persistence.capabilities.settings_write import SettingsWrite
from runtimeV2.persistence.capabilities.widget_config_read import WidgetConfigRead
from runtimeV2.persistence.capabilities.widget_config_write import WidgetConfigWrite
from runtimeV2.persistence.contracts import BootstrapConfig, PersistencePaths
from runtimeV2.persistence.services.reset_service import PersistenceResetService
from runtimeV2.persistence.services.store_provider import PersistenceStoreProvider
from runtimeV2.persistence.registry import PersistenceRegistry, PersistenceSchema, PersistenceScope
from runtimeV2.persistence.repository import PersistenceRepository
from runtimeV2.persistence.manifest.settings import SettingDecl
from runtimeV2.persistence.startup_shutdown.register_documents import register_persistence_documents
from runtimeV2.persistence.stores.overlay_index import OverlayIndexStore, overlay_store_uuid
from runtimeV2.persistence.stores.overlay_stores import HostPluginStyleStore, OverlayLayoutStore, OverlayThemeStore
from runtimeV2.persistence.stores.settings import SettingsStore
from runtimeV2.persistence.stores.widget_config import WidgetConfigStore
from runtimeV2.widgets.startup_shutdown.register_persistence import register_widget_persistence_schemas


def _paths(tmp_path) -> PersistencePaths:
    base_dir = tmp_path / "TinyUi"
    return PersistencePaths(
        base_dir=base_dir,
        cache_dir=base_dir / "cache",
        logs_dir=base_dir / "logs",
        bootstrap_path=base_dir / "bootstrap.toml",
        app_database_path=base_dir / "app.db",
        overlays_dir=base_dir / "overlays",
    )


def _repository(tmp_path) -> PersistenceRepository:
    registry = PersistenceRegistry()
    register_persistence_documents(registry)
    register_widget_persistence_schemas(registry)
    return PersistenceRepository(registry, SQLiteDocumentBackend(tmp_path / "test.db"))


def _registry() -> PersistenceRegistry:
    registry = PersistenceRegistry()
    register_persistence_documents(registry)
    register_widget_persistence_schemas(registry)
    return registry


def test_persistence_registry_registers_persistence_owned_schemas() -> None:
    """Persistence startup should expose central schemas for owned documents."""

    registry = PersistenceRegistry()
    register_persistence_documents(registry)

    assert registry.schema("settings_values").key_fields == ("namespace",)
    assert registry.schema("persistence_migrations").scope == PersistenceScope.APP
    assert registry.schema("overlay_index").key_fields == ("overlay_uuid",)
    assert registry.schema("overlay_theme").key_fields == ("singleton_id",)
    assert registry.schema("overlay_layout").key_fields == ("singleton_id",)
    assert registry.schema("host_plugin_style").key_fields == ("plugin_id",)


def test_widgets_register_their_own_persistence_schemas() -> None:
    """Widgets should register widget-owned persistent document schemas."""

    registry = PersistenceRegistry()
    register_widget_persistence_schemas(registry)

    assert registry.schema("widget_instances").key_fields == ("widget_instance_id",)
    assert registry.schema("widget_visibility").key_fields == ("singleton_id",)
    assert registry.schema("widget_defaults").key_fields == ("widget_type",)


def test_persistence_registry_rejects_wrong_owner_registration() -> None:
    """Schema ownership should match the registering domain."""

    registry = PersistenceRegistry()
    schema = PersistenceSchema(
        name="widget_instances",
        owner_domain="widgets",
        collection="widget_instances",
        scope=PersistenceScope.WIDGET_INSTANCE,
        version=1,
        key_fields=("widget_instance_id",),
    )

    try:
        registry.register_schema(schema, registering_domain="persistence")
    except ValueError as exc:
        assert "does not match registering domain" in str(exc)
    else:
        raise AssertionError("Registry accepted a schema registered by the wrong domain")


def test_bootstrap_defaults_to_sqlite_backend(tmp_path) -> None:
    """Bootstrap should prefer SQLite for new persistence installs."""

    config = load_bootstrap(tmp_path / "bootstrap.toml")

    assert config.backend == "sqlite"


def test_bootstrap_persists_sqlite_backend_config(tmp_path) -> None:
    """Bootstrap should keep the selected backend."""

    path = tmp_path / "bootstrap.toml"
    save_bootstrap(path, BootstrapConfig(backend="sqlite"))

    config = load_bootstrap(path)

    assert config.backend == "sqlite"


def test_sqlite_document_backend_is_runtime_default(tmp_path) -> None:
    """SQLite backend should be the embedded runtime persistence backend."""

    paths = _paths(tmp_path)
    backend = create_persistence_backend(BootstrapConfig(), sqlite_path=paths.app_database_path)

    assert isinstance(backend, SQLiteDocumentBackend)
    assert paths.app_database_path.exists()


def test_json_backend_is_not_supported() -> None:
    """JSON backend should not exist as a runtime or test backend."""

    try:
        create_persistence_backend(BootstrapConfig(backend="json"))
    except ValueError as exc:
        assert "Unsupported persistence backend" in str(exc)
    else:
        raise AssertionError("JSON backend is still supported")


def test_repository_rejects_unknown_schema(tmp_path) -> None:
    """Repository should fail hard when a store asks for an unregistered schema."""

    repository = PersistenceRepository(PersistenceRegistry(), SQLiteDocumentBackend(tmp_path / "test.db"))

    try:
        repository.read_one("missing_schema", {})
    except KeyError as exc:
        assert "Unknown persistence schema" in str(exc)
    else:
        raise AssertionError("Repository accepted an unknown schema")


def test_repository_validates_schema_keys(tmp_path) -> None:
    """Repository should enforce schema key fields before storage access."""

    repository = _repository(tmp_path)

    try:
        repository.write_one("settings_values", {"unexpected_key": "default"}, {"values": {}})
    except ValueError as exc:
        assert "namespace" in str(exc)
    else:
        raise AssertionError("Repository accepted an incomplete schema key")


def test_settings_store_loads_only_registered_and_valid_values(tmp_path) -> None:
    """Settings store should ignore unknown keys and invalid persisted values."""

    repository = _repository(tmp_path)
    repository.write_one(
        "settings_values",
        {"namespace": "tinyui"},
        {"values": {"showClock": False, "refreshRate": "fast", "unused": 123}},
    )
    settings = SettingsStore(repository)

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

    store = WidgetConfigStore(_repository(tmp_path))

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


def test_widget_config_store_can_set_and_reset_widget_type_defaults(tmp_path) -> None:
    """Widget config store should persist defaults per widget type."""

    store = WidgetConfigStore(_repository(tmp_path))

    assert store.set_widget_type_defaults("overlay.main", "textWidget", {"width": 220, "height": 80}) is True
    assert store.widget_type_defaults("overlay.main", "textWidget") == {"width": 220, "height": 80}

    assert store.reset_widget_type_defaults("overlay.main", "textWidget") is True
    assert store.widget_type_defaults("overlay.main", "textWidget") == {}
    assert store.reset_widget_type_defaults("overlay.main", "textWidget") is False


def test_widget_config_store_can_route_overlay_data_to_overlay_database(tmp_path) -> None:
    """Widget config should be able to persist overlay-owned documents in overlay stores."""

    paths = _paths(tmp_path)
    provider = PersistenceStoreProvider(
        config=BootstrapConfig(),
        paths=paths,
        registry=_registry(),
    )
    overlay_index = OverlayIndexStore(provider.app_repository())
    overlay_record = overlay_index.register_overlay(
        plugin_id="tinyui",
        overlay_id="tinyui.statusbar",
    )
    store = WidgetConfigStore(
        provider.app_repository(),
        overlay_repository=provider.overlay_repository,
        overlay_index=overlay_index,
    )

    assert store.set_widget_values("tinyui.statusbar", "speed", {"units": "kph"}) is True
    assert store.set_widget_type_defaults("tinyui.statusbar", "textWidget", {"width": 220}) is True

    assert paths.app_database_path.exists()
    assert paths.overlay_database_path(overlay_record.overlay_uuid).exists()
    assert provider.app_repository().list_documents("widget_instances") == []
    assert provider.app_repository().list_documents("widget_defaults") == []
    assert provider.overlay_repository(overlay_record.overlay_uuid).list_documents("widget_instances")[0]["widget_id"] == "speed"
    assert provider.overlay_repository(overlay_record.overlay_uuid).list_documents("widget_defaults")[0]["defaults"] == {
        "width": 220,
    }

    provider.close()


def test_widget_config_store_fails_for_unknown_overlay_with_overlay_routing(tmp_path) -> None:
    """Overlay-routed widget config should fail hard for unknown overlays."""

    paths = _paths(tmp_path)
    provider = PersistenceStoreProvider(
        config=BootstrapConfig(),
        paths=paths,
        registry=_registry(),
    )
    store = WidgetConfigStore(
        provider.app_repository(),
        overlay_repository=provider.overlay_repository,
        overlay_index=OverlayIndexStore(provider.app_repository()),
    )

    try:
        store.set_widget_values("missing.overlay", "speed", {"units": "kph"})
    except KeyError as exc:
        assert "missing.overlay" in str(exc)
    else:
        raise AssertionError("Widget config accepted an unknown overlay")
    finally:
        provider.close()


def test_overlay_stores_write_to_overlay_database(tmp_path) -> None:
    """Overlay-owned theme, layout and style documents should live in overlay stores."""

    paths = _paths(tmp_path)
    provider = PersistenceStoreProvider(
        config=BootstrapConfig(),
        paths=paths,
        registry=_registry(),
    )
    overlay_index = OverlayIndexStore(provider.app_repository())
    overlay_record = overlay_index.register_overlay(
        plugin_id="tinyui",
        overlay_id="tinyui.statusbar",
    )
    theme_store = OverlayThemeStore(
        overlay_index=overlay_index,
        overlay_repository=provider.overlay_repository,
    )
    layout_store = OverlayLayoutStore(
        overlay_index=overlay_index,
        overlay_repository=provider.overlay_repository,
    )
    style_store = HostPluginStyleStore(
        overlay_index=overlay_index,
        overlay_repository=provider.overlay_repository,
    )

    theme_store.set_theme("tinyui.statusbar", {"font": "Inter"})
    layout_store.set_layout("tinyui.statusbar", {"grid": "3x3"})
    style_store.set_style("tinyui.statusbar", "tinyui", {"background": "#111111"})

    assert theme_store.get_theme("tinyui.statusbar") == {"font": "Inter"}
    assert layout_store.get_layout("tinyui.statusbar") == {"grid": "3x3"}
    assert style_store.get_style("tinyui.statusbar", "tinyui") == {"background": "#111111"}
    assert provider.app_repository().list_documents("overlay_theme") == []
    assert provider.app_repository().list_documents("overlay_layout") == []
    assert provider.app_repository().list_documents("host_plugin_style") == []
    overlay_repository = provider.overlay_repository(overlay_record.overlay_uuid)
    assert overlay_repository.list_documents("overlay_theme")[0]["theme"] == {"font": "Inter"}
    assert overlay_repository.list_documents("overlay_layout")[0]["layout"] == {"grid": "3x3"}
    assert overlay_repository.list_documents("host_plugin_style")[0]["style"] == {"background": "#111111"}

    provider.close()


def test_overlay_store_uuid_is_stable() -> None:
    """Overlay store UUID should be stable for the plugin and overlay identity."""

    assert overlay_store_uuid(plugin_id="tinyui", overlay_id="tinyui.statusbar") == overlay_store_uuid(
        plugin_id="tinyui",
        overlay_id="tinyui.statusbar",
    )
    assert overlay_store_uuid(plugin_id="tinyui", overlay_id="tinyui.statusbar") != overlay_store_uuid(
        plugin_id="tinyui",
        overlay_id="tinyui.dashboard",
    )


def test_overlay_index_keeps_app_owned_relationship_metadata(tmp_path) -> None:
    """Overlay index should map app-known overlays without owning overlay content."""

    store = OverlayIndexStore(_repository(tmp_path))

    record = store.register_overlay(
        plugin_id="tinyui",
        overlay_id="tinyui.statusbar",
    )

    assert record.overlay_uuid == overlay_store_uuid(plugin_id="tinyui", overlay_id="tinyui.statusbar")
    assert store.overlay(record.overlay_uuid) == record
    assert store.overlay_by_id("tinyui.statusbar") == record
    assert store.overlays() == [record]

    store.remove_overlay(record.overlay_uuid)

    assert store.overlay(record.overlay_uuid) is None


def test_reset_overlay_deletes_overlay_database_but_keeps_index(tmp_path) -> None:
    """Overlay reset should delete the overlay store and keep the app-owned index."""

    paths = _paths(tmp_path)
    provider = PersistenceStoreProvider(
        config=BootstrapConfig(),
        paths=paths,
        registry=_registry(),
    )
    overlay_index = OverlayIndexStore(provider.app_repository())
    overlay_record = overlay_index.register_overlay(plugin_id="tinyui", overlay_id="tinyui.statusbar")
    widget_config = WidgetConfigStore(
        provider.app_repository(),
        overlay_repository=provider.overlay_repository,
        overlay_index=overlay_index,
    )
    reset_service = PersistenceResetService(
        overlay_index=overlay_index,
        store_provider=provider,
        widget_config=widget_config,
    )
    widget_config.set_widget_values("tinyui.statusbar", "speed", {"units": "kph"})
    overlay_path = paths.overlay_database_path(overlay_record.overlay_uuid)
    assert overlay_path.exists()

    reset_service.reset_overlay("tinyui.statusbar")

    assert not overlay_path.exists()
    assert overlay_index.overlay_by_id("tinyui.statusbar") == overlay_record
    assert widget_config.get_widget("tinyui.statusbar", "speed") is None

    provider.close()


def test_delete_overlay_deletes_overlay_database_and_index(tmp_path) -> None:
    """Overlay delete should remove both the overlay store and the app-owned index."""

    paths = _paths(tmp_path)
    provider = PersistenceStoreProvider(
        config=BootstrapConfig(),
        paths=paths,
        registry=_registry(),
    )
    overlay_index = OverlayIndexStore(provider.app_repository())
    overlay_record = overlay_index.register_overlay(plugin_id="tinyui", overlay_id="tinyui.statusbar")
    widget_config = WidgetConfigStore(
        provider.app_repository(),
        overlay_repository=provider.overlay_repository,
        overlay_index=overlay_index,
    )
    reset_service = PersistenceResetService(
        overlay_index=overlay_index,
        store_provider=provider,
        widget_config=widget_config,
    )
    widget_config.set_widget_values("tinyui.statusbar", "speed", {"units": "kph"})
    overlay_path = paths.overlay_database_path(overlay_record.overlay_uuid)
    assert overlay_path.exists()

    reset_service.delete_overlay("tinyui.statusbar")

    assert not overlay_path.exists()
    assert overlay_index.overlay_by_id("tinyui.statusbar") is None

    provider.close()


def test_factory_reset_deletes_app_and_overlay_databases(tmp_path) -> None:
    """Factory reset should delete app and overlay database files."""

    paths = _paths(tmp_path)
    provider = PersistenceStoreProvider(
        config=BootstrapConfig(),
        paths=paths,
        registry=_registry(),
    )
    overlay_index = OverlayIndexStore(provider.app_repository())
    overlay_record = overlay_index.register_overlay(plugin_id="tinyui", overlay_id="tinyui.statusbar")
    widget_config = WidgetConfigStore(
        provider.app_repository(),
        overlay_repository=provider.overlay_repository,
        overlay_index=overlay_index,
    )
    reset_service = PersistenceResetService(
        overlay_index=overlay_index,
        store_provider=provider,
        widget_config=widget_config,
    )
    widget_config.set_widget_values("tinyui.statusbar", "speed", {"units": "kph"})
    overlay_path = paths.overlay_database_path(overlay_record.overlay_uuid)
    assert paths.app_database_path.exists()
    assert overlay_path.exists()

    reset_service.factory_reset()

    assert not paths.app_database_path.exists()
    assert not overlay_path.exists()


def test_settings_capabilities_read_and_write_values(tmp_path) -> None:
    """Settings capabilities should expose specs and persist values through the store."""

    store = SettingsStore(_repository(tmp_path))
    store.register_specs(
        {
            "tinyui": [
                SettingDecl(key="showClock", label="Show Clock", type="bool", default=True),
            ]
        }
    )
    read = SettingsRead(store)
    write = SettingsWrite(store)

    assert read.by_namespace()["tinyui"][0].key == "showClock"
    assert read.get("tinyui", "showClock") is True

    write.set("tinyui", "showClock", False)
    write.save("tinyui")
    write.save_all()

    assert read.get("tinyui", "showClock") is False
    assert read.namespace_values("tinyui") == {"showClock": False}


def test_widget_config_capabilities_keep_persistence_as_owner(tmp_path) -> None:
    """Widget config read/write should keep persistence as the storage owner."""

    store = WidgetConfigStore(_repository(tmp_path))
    read = WidgetConfigRead(store)
    write = WidgetConfigWrite(store)

    assert write.set_widget_enabled("overlay.main", "speed", False) is True
    assert write.set_widget_position("overlay.main", "speed", 10, 20) is True
    assert write.set_widget_values("overlay.main", "speed", {"units": "kph"}) is True
    assert write.set_widget_type_defaults("overlay.main", "gauge", {"width": 180}) is True

    config = read.get_widget("overlay.main", "speed")
    assert config is not None
    assert config.enabled is False
    assert config.position == (10, 20)
    assert read.widget_values("overlay.main", "speed") == {"units": "kph"}
    assert read.widget_type_defaults("overlay.main", "gauge") == {"width": 180}
    assert write.reset_widget_type_defaults("overlay.main", "gauge") is True
    assert read.widget_type_defaults("overlay.main", "gauge") == {}
    assert read.global_widgets_visible() is False
