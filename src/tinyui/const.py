"""TinyUI constants — single source via pyproject.toml metadata."""

from importlib.metadata import metadata

_meta = metadata("tinyui")

APP_NAME: str = _meta["Name"]
VERSION: str = _meta["Version"]
