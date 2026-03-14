"""CLI voor de ast_parser config tool."""

from .shared import cli

# Registreer alle command modules
from . import scan_cmds  # noqa: F401
from . import leftover_cmd  # noqa: F401
from . import flat_cmd  # noqa: F401
from . import build_cmd  # noqa: F401

__all__ = ["cli"]
