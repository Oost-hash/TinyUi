"""Jinja environment setup met filters."""

import keyword
import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


def _to_safe_id(name: str) -> str:
    """Maak Python-safe identifier."""
    safe = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    if safe and safe[0].isdigit():
        safe = "_" + safe
    if keyword.iskeyword(safe):
        safe += "_"
    return safe


def _to_class_name(name: str) -> str:
    """Converteer snake_case naar PascalCase."""
    return "".join(x.capitalize() for x in name.split("_"))


def _to_type_hint(value) -> str:
    """Bepaal type annotation voor waarde."""
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "str"
    return "Any"


def _to_dict_repr(d: dict) -> str:
    """Formatteer dict als Python dict literal."""
    items = []
    for idx, kwargs in sorted(d.items()):
        class_name = kwargs.pop("_class_name", "Unknown")
        kw_str = ", ".join(f"{k}={repr(v)}" for k, v in kwargs.items())
        items.append(f"{idx}: {class_name}({kw_str})")
    return "{" + ", ".join(items) + "}"


def _to_dict_kwargs(d: dict) -> str:
    """Formatteer dict als keyword arguments string."""
    return ", ".join(f"{k}={repr(v)}" for k, v in d.items())


def create(template_dir: Path) -> Environment:
    """Maak Jinja environment met custom filters."""
    env = Environment(loader=FileSystemLoader(template_dir))

    env.filters["safe_id"] = _to_safe_id
    env.filters["class_name"] = _to_class_name
    env.filters["type_hint"] = _to_type_hint
    env.filters["to_dict_repr"] = _to_dict_repr
    env.filters["dict_kwargs"] = _to_dict_kwargs
    env.filters["repr"] = repr

    return env
