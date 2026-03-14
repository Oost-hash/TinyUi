"""Flat command: toon de ruwe flat config van een widget."""

import json
from pathlib import Path

import click

from ..io import LoadError, load_configs
from .shared import cli


@cli.command()
@click.argument("widget")
@click.option("--output", "-o", type=click.Path(path_type=Path), default=None, help="Output naar JSON bestand")
@click.option("--sort/--no-sort", default=True, help="Sorteer keys alfabetisch")
@click.pass_context
def flat(ctx, widget, output, sort):
    """Toon de ruwe flat config van een widget (zonder bewerking)."""
    templates = ctx.obj["templates"]

    try:
        configs = load_configs(templates)
    except LoadError as e:
        click.echo(f"Error loading configurations: {e}", err=True)
        raise click.Exit(1)

    if widget not in configs:
        click.echo(f"Widget '{widget}' not found", err=True)
        click.echo(f"Available: {', '.join(sorted(configs.keys()))}")
        raise click.Exit(1)

    data = configs[widget]
    if sort:
        data = dict(sorted(data.items()))

    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        click.echo(f"Written {len(data)} keys to {output}")
    else:
        for key, value in data.items():
            click.echo(f"{key}: {value!r}")
        click.echo(f"\n--- {len(data)} keys ---")
