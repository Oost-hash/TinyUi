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

"""Widget type default definitions owned by the widgets domain."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


TEXT_WIDGET_TYPE = "textWidget"


@dataclass(frozen=True)
class WidgetTypeDefaultField:
    """One supported default value for a widget type."""

    key: str
    label: str
    value_type: str
    default: object
    group: str = ""
    minimum: float | None = None
    maximum: float | None = None
    step: float | None = None
    decimals: int = 0

    def qml_model(self) -> dict[str, object]:
        """Return this field as a QML-friendly model row."""

        row: dict[str, object] = {
            "key": self.key,
            "label": self.label,
            "valueType": self.value_type,
            "defaultValue": self.default,
            "group": self.group,
            "decimals": self.decimals,
        }
        if self.minimum is not None:
            row["min"] = self.minimum
        if self.maximum is not None:
            row["max"] = self.maximum
        if self.step is not None:
            row["step"] = self.step
        return row


@dataclass(frozen=True)
class WidgetTypeDefaultSchema:
    """Supported default fields for one widget type."""

    widget_type: str
    fields: tuple[WidgetTypeDefaultField, ...]

    def field(self, key: str) -> WidgetTypeDefaultField | None:
        """Return one field by key."""

        for item in self.fields:
            if item.key == key:
                return item
        return None


class WidgetTypeDefaultsRegistry:
    """Read and validate widget type default definitions."""

    def __init__(self, schemas: tuple[WidgetTypeDefaultSchema, ...]) -> None:
        self._schemas = {schema.widget_type: schema for schema in schemas}

    def schema(self, widget_type: str) -> WidgetTypeDefaultSchema | None:
        """Return the schema for one widget type."""

        return self._schemas.get(widget_type)

    def qml_fields(self, widget_type: str) -> list[dict[str, object]]:
        """Return supported fields as a QML model."""

        schema = self.schema(widget_type)
        if schema is None:
            return []
        return [field.qml_model() for field in schema.fields]

    def default_values(self, widget_type: str) -> dict[str, object]:
        """Return built-in fallback values for one widget type."""

        schema = self.schema(widget_type)
        if schema is None:
            return {}
        return {field.key: field.default for field in schema.fields}

    def sanitize_defaults(self, widget_type: str, values: dict[str, object]) -> dict[str, object]:
        """Keep only schema-owned keys and coerce values to their field type."""

        schema = self.schema(widget_type)
        if schema is None:
            return {}

        sanitized: dict[str, object] = {}
        for key, value in values.items():
            field = schema.field(key)
            if field is None:
                continue
            sanitized[key] = _coerce_field_value(field, value)
        return sanitized


def default_widget_type_defaults_registry() -> WidgetTypeDefaultsRegistry:
    """Return TinyUI's built-in widget type default registry."""

    return WidgetTypeDefaultsRegistry((
        WidgetTypeDefaultSchema(
            widget_type=TEXT_WIDGET_TYPE,
            fields=(
                WidgetTypeDefaultField(
                    key="width",
                    label="Width",
                    value_type="int",
                    default=220,
                    group="size",
                    minimum=80,
                    maximum=640,
                    step=10,
                ),
                WidgetTypeDefaultField(
                    key="height",
                    label="Height",
                    value_type="int",
                    default=72,
                    group="size",
                    minimum=32,
                    maximum=320,
                    step=4,
                ),
                WidgetTypeDefaultField(
                    key="fontSize",
                    label="Font size",
                    value_type="int",
                    default=18,
                    group="font",
                    minimum=8,
                    maximum=72,
                    step=1,
                ),
                WidgetTypeDefaultField(
                    key="textColor",
                    label="Text color",
                    value_type="string",
                    default="#E8EDF2",
                    group="color",
                ),
                WidgetTypeDefaultField(
                    key="backgroundColor",
                    label="Background",
                    value_type="string",
                    default="#20242b",
                    group="color",
                ),
            ),
        ),
    ))


def _coerce_field_value(field: WidgetTypeDefaultField, value: object) -> object:
    if field.value_type == "int":
        return _coerce_int(field, value)
    if field.value_type == "string":
        return str(value) if value is not None else field.default
    if field.value_type == "bool":
        return value if isinstance(value, bool) else bool(value)
    return value


def _coerce_int(field: WidgetTypeDefaultField, value: object) -> int:
    if isinstance(value, bool):
        return int(field.default) if isinstance(field.default, int) else 0
    if isinstance(value, int | float):
        number = int(value)
    elif isinstance(value, str):
        try:
            number = int(float(value))
        except ValueError:
            number = int(field.default) if isinstance(field.default, int) else 0
    else:
        number = int(field.default) if isinstance(field.default, int) else 0

    if field.minimum is not None:
        number = max(number, int(field.minimum))
    if field.maximum is not None:
        number = min(number, int(field.maximum))
    return number


TEXT_WIDGET_DEFAULTS: dict[str, Any] = default_widget_type_defaults_registry().default_values(TEXT_WIDGET_TYPE)
