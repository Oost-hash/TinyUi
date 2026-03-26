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

"""Helpers for walking shared-memory structures into readable raw snapshots."""

from __future__ import annotations

import ctypes
from collections.abc import Iterable


def _decode_char_array(value: ctypes.Array) -> str:
    raw = bytes(value)
    return raw.rstrip(b"\x00").decode("utf-8", errors="replace")


def _is_primitive(value: object) -> bool:
    return isinstance(value, bool | int | float | str | bytes)


def _render_primitive(value: object) -> str:
    if isinstance(value, bytes):
        return value.rstrip(b"\x00").decode("utf-8", errors="replace")
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def iter_raw_fields(root: object, prefix: str) -> list[tuple[str, str]]:
    """Flatten a ctypes-heavy object graph into key/value string pairs."""

    rows: list[tuple[str, str]] = []

    def walk(path: str, value: object) -> None:
        if _is_primitive(value):
            rows.append((path, _render_primitive(value)))
            return

        if isinstance(value, ctypes.Array):
            if getattr(value, "_type_", None) is ctypes.c_char:
                rows.append((path, _decode_char_array(value)))
                return

            items = [item for item in value]
            if items and all(_is_primitive(item) for item in items) and len(items) <= 8:
                rows.append((path, ", ".join(_render_primitive(item) for item in items)))
                return

            for index, item in enumerate(items):
                walk(f"{path}[{index}]", item)
            return

        fields = getattr(type(value), "_fields_", None)
        if fields:
            for field_name, *_rest in fields:
                walk(f"{path}.{field_name}", getattr(value, field_name))
            return

        if isinstance(value, Iterable) and not isinstance(value, str | bytes):
            for index, item in enumerate(value):
                walk(f"{path}[{index}]", item)
            return

        rows.append((path, str(value)))

    walk(prefix, root)
    return rows


def annotate_rows(
    rows: list[tuple[str, str]],
    mapping_hints: dict[str, str],
) -> list[tuple[str, str]]:
    """Attach known normalized mapping hints to raw rows when available."""

    return [
        (key, f"{value} -> {mapping_hints[key]}" if key in mapping_hints else value)
        for key, value in rows
    ]
