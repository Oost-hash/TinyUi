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

"""Widget-owned persistence schema registration."""

from __future__ import annotations

from runtimeV2.persistence.registry import PersistenceRegistry, PersistenceSchema, PersistenceScope


def register_widget_persistence_schemas(registry: PersistenceRegistry) -> None:
    """Register persistent document schemas owned by widgets."""

    registry.register_schema(
        PersistenceSchema(
            name="widget_instances",
            owner_domain="widgets",
            collection="widget_instances",
            scope=PersistenceScope.WIDGET_INSTANCE,
            version=1,
            key_fields=("widget_instance_id",),
            required_fields=("widget_instance_id", "widget_id", "schema_version"),
            default_document={"enabled": True, "position": [0, 0], "values": {}},
        ),
        registering_domain="widgets",
    )
    registry.register_schema(
        PersistenceSchema(
            name="widget_visibility",
            owner_domain="widgets",
            collection="widget_visibility",
            scope=PersistenceScope.SINGLETON,
            version=1,
            key_fields=("singleton_id",),
            required_fields=("singleton_id", "global_visible", "schema_version"),
            default_document={"global_visible": False},
        ),
        registering_domain="widgets",
    )
    registry.register_schema(
        PersistenceSchema(
            name="widget_defaults",
            owner_domain="widgets",
            collection="widget_defaults",
            scope=PersistenceScope.WIDGET_TYPE,
            version=1,
            key_fields=("widget_type",),
            required_fields=("widget_type", "defaults", "schema_version"),
            default_document={"defaults": {}},
        ),
        registering_domain="widgets",
    )
