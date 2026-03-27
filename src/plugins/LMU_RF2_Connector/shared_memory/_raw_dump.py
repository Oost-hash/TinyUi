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

"""Helpers for walking shared-memory structures and buffers into readable snapshots."""

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


def _render_ascii(data: bytes) -> str:
    return "".join(chr(byte) if 32 <= byte <= 126 else "." for byte in data)


def iter_memory_rows(
    prefix: str,
    data: bytes,
    *,
    width: int = 16,
) -> list[tuple[str, str]]:
    """Render a byte buffer into offset-addressed hex/ascii rows."""

    rows: list[tuple[str, str]] = [
        (f"{prefix}.size", str(len(data))),
        (f"{prefix}.width", str(width)),
    ]

    if not data:
        rows.append((f"{prefix}.status", "empty"))
        return rows

    for offset in range(0, len(data), width):
        chunk = data[offset : offset + width]
        hex_part = " ".join(f"{byte:02X}" for byte in chunk)
        ascii_part = _render_ascii(chunk)
        rows.append((f"{prefix}.{offset:08X}", f"{hex_part:<{width * 3 - 1}} |{ascii_part}|"))

    return rows
