"""Leftover command: inspect wat overblijft na parse + normalize."""

import random

import click

from ..io import LoadError, load_configs
from ..compiler import normalize, parse
from .shared import cli


@cli.command()
@click.option("--widget", "-w", help="Specific widget to check")
@click.option("--sample", "-s", type=int, default=5, help="Random sample of N widgets (default 5)")
@click.pass_context
def leftover(ctx, widget, sample):
    """Show leftover keys after parse + normalize."""
    templates = ctx.obj["templates"]

    try:
        configs = load_configs(templates)
    except LoadError as e:
        click.echo(f"Error loading configurations: {e}", err=True)
        raise click.Exit(1)

    if widget:
        if widget not in configs:
            click.echo(f"Widget '{widget}' not found", err=True)
            raise click.Exit(1)
        targets = [widget]
    else:
        all_names = sorted(configs.keys())
        targets = random.sample(all_names, min(sample, len(all_names)))

    total_leftover = 0
    for name in sorted(targets):
        ast = parse(name, configs[name])
        ast = normalize(ast)
        total_leftover += len(ast.leftover)

        if ast.leftover:
            click.echo(f"\n{name}: {len(ast.leftover)} leftover")
            for f in ast.leftover:
                click.echo(f"  {f.name}: {f.type} = {f.default!r}")
        else:
            click.echo(f"\n{name}: clean!")

    click.echo(f"\n--- {total_leftover} leftover across {len(targets)} widgets ---")


@cli.command(name="leftover-total")
@click.pass_context
def leftover_total(ctx):
    """Show total leftover count across all widgets."""
    templates = ctx.obj["templates"]

    try:
        configs = load_configs(templates)
    except LoadError as e:
        click.echo(f"Error loading configurations: {e}", err=True)
        raise click.Exit(1)

    total = 0
    for name, config in configs.items():
        ast = parse(name, config)
        ast = normalize(ast)
        total += len(ast.leftover)

    click.echo(f"Total leftover: {total}")
