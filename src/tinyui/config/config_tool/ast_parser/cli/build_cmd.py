"""Build command: compileer flat configs naar Python dataclasses."""

from pathlib import Path

import click

from ..compiler import emit_components_file, emit_widget, mark_shared_components, normalize, parse
from ..io import LoadError, load_configs, load_json
from .shared import cli


@cli.command()
@click.option("--output", "-o", type=click.Path(path_type=Path), required=True, help="Output directory")
@click.option("--groupings", "-g", type=click.Path(exists=True, path_type=Path), help="Groupings JSON file")
@click.option("--widget", "-w", help="Build single widget only")
@click.pass_context
def build(ctx, output, groupings, widget):
    """Build Python dataclass files from flat widget configs."""
    templates = ctx.obj["templates"]

    try:
        configs = load_configs(templates)
    except LoadError as e:
        click.echo(f"Error loading configurations: {e}", err=True)
        raise click.Exit(1)

    # Load optional groupings
    grouping_data = {}
    if groupings:
        grouping_data = load_json(groupings)

    # Filter single widget
    if widget:
        if widget not in configs:
            click.echo(f"Widget '{widget}' not found", err=True)
            raise click.Exit(1)
        configs = {widget: configs[widget]}

    # Parse all widgets
    widgets = []
    for name, config in configs.items():
        widget_groupings = grouping_data.get(name)
        ast = parse(name, config, groupings=widget_groupings)
        ast = normalize(ast)
        widgets.append(ast)

    # Global analysis
    shared_components = mark_shared_components(widgets)

    # Emit
    output.mkdir(parents=True, exist_ok=True)

    if shared_components:
        components_code = emit_components_file(shared_components)
        (output / "_components.py").write_text(components_code, encoding="utf-8")
        click.echo(f"  _components.py ({len(shared_components)} components)")

    for ast in widgets:
        widget_code = emit_widget(ast)
        (output / f"{ast.name}.py").write_text(widget_code, encoding="utf-8")

    click.echo(f"\nBuilt {len(widgets)} widgets to {output}")
