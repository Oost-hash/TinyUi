"""Shared CLI infrastructure."""

from pathlib import Path

import click

from ..io import LoadError, load_configs


def format_value(value):
    """Format value for display, truncate if too long."""
    s = repr(value)
    if len(s) > 50:
        return s[:47] + "..."
    return s


@click.group()
@click.option(
    "--templates",
    "-t",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to templates directory",
)
@click.pass_context
def cli(ctx, templates):
    """AST-based config compiler."""
    ctx.ensure_object(dict)
    ctx.obj["templates"] = templates
