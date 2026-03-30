"""Application identity — name and version."""

from __future__ import annotations

from importlib.metadata import metadata

_meta = metadata("tinyui")

APP_NAME: str = _meta["Name"]
VERSION: str  = _meta["Version"]
