"""Gedeelde utility functies."""

import keyword
import re
from typing import Any


def safe_id(name: str) -> str:
    """Maak Python-safe identifier."""
    safe = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    if safe and safe[0].isdigit():
        safe = "_" + safe
    if keyword.iskeyword(safe):
        safe += "_"
    return safe


def to_class_name(name: str) -> str:
    """Snake_case naar PascalCase."""
    return "".join(x.capitalize() for x in name.split("_"))


def infer_type(value: Any) -> str:
    """Type hint voor waarde."""
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "str"
    if isinstance(value, list):
        return "list"
    if isinstance(value, dict):
        return "dict"
    return "Any"
