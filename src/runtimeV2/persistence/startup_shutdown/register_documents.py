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

"""Persistence-owned document schema registration."""

from runtimeV2.persistence.registry import PersistenceRegistry, PersistenceSchema, PersistenceScope


def register_persistence_documents(registry: PersistenceRegistry) -> None:
    """Register persistence-owned document schemas."""

    registry.register_schema(
        PersistenceSchema(
            name="settings_values",
            owner_domain="persistence",
            collection="settings_values",
            scope=PersistenceScope.NAMESPACE,
            version=1,
            key_fields=("namespace",),
            required_fields=("namespace", "values", "schema_version"),
            default_document={"values": {}},
        ),
        registering_domain="persistence",
    )
    registry.register_schema(
        PersistenceSchema(
            name="persistence_migrations",
            owner_domain="persistence",
            collection="persistence_migrations",
            scope=PersistenceScope.APP,
            version=1,
            key_fields=("schema_name", "from_version", "to_version"),
            required_fields=("schema_name", "from_version", "to_version", "schema_version"),
            default_document={},
        ),
        registering_domain="persistence",
    )
    registry.register_schema(
        PersistenceSchema(
            name="overlay_index",
            owner_domain="persistence",
            collection="overlay_index",
            scope=PersistenceScope.APP,
            version=1,
            key_fields=("overlay_uuid",),
            required_fields=("overlay_uuid", "plugin_id", "overlay_id", "enabled", "schema_version"),
            default_document={"enabled": True},
        ),
        registering_domain="persistence",
    )
    registry.register_schema(
        PersistenceSchema(
            name="overlay_theme",
            owner_domain="persistence",
            collection="overlay_theme",
            scope=PersistenceScope.SINGLETON,
            version=1,
            key_fields=("singleton_id",),
            required_fields=("singleton_id", "theme", "schema_version"),
            default_document={"theme": {}},
        ),
        registering_domain="persistence",
    )
    registry.register_schema(
        PersistenceSchema(
            name="overlay_layout",
            owner_domain="persistence",
            collection="overlay_layout",
            scope=PersistenceScope.SINGLETON,
            version=1,
            key_fields=("singleton_id",),
            required_fields=("singleton_id", "layout", "schema_version"),
            default_document={"layout": {}},
        ),
        registering_domain="persistence",
    )
    registry.register_schema(
        PersistenceSchema(
            name="host_plugin_style",
            owner_domain="persistence",
            collection="host_plugin_style",
            scope=PersistenceScope.PLUGIN,
            version=1,
            key_fields=("plugin_id",),
            required_fields=("plugin_id", "style", "schema_version"),
            default_document={"style": {}},
        ),
        registering_domain="persistence",
    )
