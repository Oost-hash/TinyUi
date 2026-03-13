"""Command line interface for flat_to_nested.

SCAN COMMAND ARGUMENTS:
-----------------------

Position: flat_to_nested -t <templates> scan [OPTIONS]

Options:
    -w, --widget <name>     Focus on single widget by name
                            Example: -w engine

    -s, --sample <int>      Random sample of N widgets
                            Example: -s 5

    -v, --vars              Show all configuration variables
                            Use with -w to see full widget config
                            Example: -w engine --vars

    -o, --output <path>     Write JSON output to file
                            Example: -o output.json

EXAMPLES:
---------

# Scan all widgets
python -m flat_to_nested -t templates/ scan

"""

import random
from pathlib import Path

import click

from flat_to_nested.scan.columns import analyze_all_columns, analyze_widget_columns
from flat_to_nested.utils.load_python import LoadError, load_assignments
from flat_to_nested.utils.save_json import save_json


def load_configs(templates_path: Path):
    """Load widget configurations from templates directory."""
    heatmaps = load_assignments(
        templates_path / "setting_heatmap.py", "HEATMAP_DEFAULT"
    )
    raw_widgets = load_assignments(
        templates_path / "setting_widget.py", "WIDGET_DEFAULT"
    )

    configs = {}
    for widget_name, widget_config in raw_widgets.items():
        resolved = {}
        for key, value in widget_config.items():
            if isinstance(value, str) and value.startswith("HEATMAP["):
                heatmap_key = value[8:-1]
                resolved[key] = heatmaps.get(heatmap_key, value)
            else:
                resolved[key] = value
        configs[widget_name] = resolved

    return configs


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
    """Flat to nested widget converter."""
    ctx.ensure_object(dict)
    ctx.obj["templates"] = templates


def format_value(value):
    """Format value for display, truncate if too long."""
    s = repr(value)
    if len(s) > 50:
        return s[:47] + "..."
    return s


@cli.command()
@click.option(
    "--widget",
    "-w",
    help="Specific widget to scan",
)
@click.option(
    "--sample",
    "-s",
    type=int,
    help="Random sample of N widgets",
)
@click.option(
    "--vars",
    "-v",
    "show_vars",
    is_flag=True,
    help="Show all configuration variables",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Write scan results to JSON file",
)
@click.pass_context
def scan(ctx, widget, sample, show_vars, output):
    """Scan column configurations."""
    templates = ctx.obj["templates"]

    try:
        configs = load_configs(templates)
    except LoadError as e:
        click.echo(f"Error loading configurations: {e}", err=True)
        raise click.Exit(1)

    if not configs:
        click.echo("No configurations found", err=True)
        raise click.Exit(1)

    # Handle sample selection
    if sample:
        if sample >= len(configs):
            selected = list(configs.keys())
        else:
            selected = random.sample(list(configs.keys()), sample)
        configs = {k: configs[k] for k in selected}
        click.echo(f"\nRandom sample of {len(configs)} widgets")

    # Single widget focus
    if widget:
        if widget not in configs:
            click.echo(f"Widget '{widget}' not found", err=True)
            available = ", ".join(sorted(configs.keys())[:10])
            click.echo(f"Available: {available}...", err=True)
            raise click.Exit(1)

        config = configs[widget]
        columns = analyze_widget_columns(widget, config)

        click.echo(f"\n{widget}: {len(columns)} columns")

        for col in columns:
            click.echo(f"\n  Column: {col['id']}")
            click.echo(f"    show_key: {col['show_key']}")

            optional_attrs = [
                "font_color",
                "bkg_color",
                "decimal_places",
                "prefix",
                "suffix_attr",
                "state_colors",
            ]
            for attr in optional_attrs:
                if attr in col:
                    click.echo(f"    {attr}: {col[attr]}")

            show_suffix = col["show_key"][5:] if col.get("show_key") else ""
            if col["id"] != show_suffix:
                click.echo(
                    f"    WARNING: inconsistent id='{col['id']}' vs show='{col['show_key']}'"
                )

        if show_vars:
            click.echo(f"\n  All variables ({len(config)} total):")
            for key in sorted(config.keys()):
                value = format_value(config[key])
                click.echo(f"    {key}: {value}")

        if output:
            result = {
                widget: {"columns": columns, "variables": config if show_vars else None}
            }
            save_json(result, output)
            click.echo(f"\nWritten to {output}")

        return

    # All widgets (or sample)
    all_columns = analyze_all_columns(configs)

    total_cols = sum(len(cols) for cols in all_columns.values())
    click.echo(f"\nFound {total_cols} columns across {len(all_columns)} widgets")

    # Build result for JSON output
    result = {}

    for widget_name, columns in all_columns.items():
        if columns:
            click.echo(f"\n{widget_name}: {len(columns)} columns")
            for col in columns:
                click.echo(f"  - {col['id']} (via {col['show_key']})")

            if show_vars:
                config = configs[widget_name]
                click.echo(f"    Variables ({len(config)} total):")
                for key in sorted(list(config.keys())[:20]):
                    value = format_value(config[key])
                    click.echo(f"      {key}: {value}")
                if len(config) > 20:
                    click.echo(f"      ... and {len(config) - 20} more")

                result[widget_name] = {"columns": columns, "variables": config}
            else:
                result[widget_name] = columns

    if output:
        save_json(result, output)
        click.echo(f"\nWritten to {output}")


@cli.command()
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default=Path("output"),
    help="Output directory for generated widgets",
)
@click.pass_context
def build(ctx, output):
    """Build nested widgets from flat configurations."""
    templates = ctx.obj["templates"]
    click.echo(f"Building widgets from {templates}...")
    click.echo(f"Output directory: {output}")
    click.echo("Build command not yet implemented")


@cli.command()
@click.argument("generated", type=click.Path(exists=True, path_type=Path))
@click.argument("original", type=click.Path(exists=True, path_type=Path))
def compare(generated, original):
    """Compare generated widgets against original configurations."""
    click.echo(f"Comparing {generated} against {original}...")
    click.echo("Compare command not yet implemented")


def main():
    cli()


if __name__ == "__main__":
    main()
