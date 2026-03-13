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

from .scan.color_palettes import analyze_all_colors, analyze_widget_colors
from .scan.columns import analyze_all_cells, analyze_all_columns, analyze_widget_cells, analyze_widget_columns
from .scan.prefixes import find_reusable_groups, find_widget_groups
from .scan.prefixes import KNOWN_GROUPS, KNOWN_PREFIXES, find_auto_prefixes, find_known_groups
from .scan.suggest import format_dataclass, suggest_dataclasses
from .utils.load_python import LoadError, load_assignments
from .utils.save_json import save_json


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
        cells = analyze_widget_cells(widget, config)
        columns = analyze_widget_columns(widget, config)

        click.echo(f"\n{widget}: {len(cells)} cells, {len(columns)} layout columns")

        if cells:
            click.echo(f"\n  Cells:")
            for cell in cells:
                attrs_str = ", ".join(cell["attrs"])
                click.echo(f"    {cell['id']} [{cell['variant']}]: {attrs_str}")

        if columns:
            click.echo(f"\n  Layout columns:")
            for col in columns:
                click.echo(f"    {col['id']} (show_key: {col['show_key']})")

        if show_vars:
            click.echo(f"\n  All variables ({len(config)} total):")
            for key in sorted(config.keys()):
                value = format_value(config[key])
                click.echo(f"    {key}: {value}")

        if output:
            result = {
                widget: {
                    "cells": cells,
                    "columns": columns,
                    "variables": config if show_vars else None,
                }
            }
            save_json(result, output)
            click.echo(f"\nWritten to {output}")

        return

    # All widgets (or sample)
    all_cells = analyze_all_cells(configs)
    all_columns = analyze_all_columns(configs)

    total_cells = sum(len(c) for c in all_cells.values())
    total_cols = sum(len(cols) for cols in all_columns.values())
    click.echo(f"\nFound {total_cells} cells, {total_cols} layout columns across {len(configs)} widgets")

    # Build result for JSON output
    result = {}

    for widget_name in sorted(configs.keys()):
        cells = all_cells.get(widget_name, [])
        columns = all_columns.get(widget_name, [])

        if cells or columns:
            parts = []
            if cells:
                parts.append(f"{len(cells)} cells")
            if columns:
                parts.append(f"{len(columns)} columns")
            click.echo(f"\n{widget_name}: {', '.join(parts)}")

            for cell in cells:
                click.echo(f"  cell: {cell['id']} [{cell['variant']}]")
            for col in columns:
                click.echo(f"  col:  {col['id']} (via {col['show_key']})")

            result[widget_name] = {"cells": cells, "columns": columns}

    if output:
        save_json(result, output)
        click.echo(f"\nWritten to {output}")


@cli.command()
@click.option(
    "--widget",
    "-w",
    help="Specific widget to analyze",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Write results to JSON file",
)
@click.pass_context
def colors(ctx, widget, output):
    """Scan color palettes across widgets."""
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

        result = analyze_widget_colors(widget, configs[widget])

        click.echo(f"\n{widget}: {result['color_count']} unique colors")

        click.echo(f"\n  Palettes (font + bkg pairs): {len(result['pairs'])}")
        for pair in result["pairs"]:
            click.echo(
                f"    {pair['suffix']}: "
                f"font={pair['font_color']}  bkg={pair['bkg_color']}"
            )

        if result["unpaired"]:
            click.echo(f"\n  Unpaired ({len(result['unpaired'])}):")
            for p in result["unpaired"]:
                color = p.get("font_color") or p.get("bkg_color")
                kind = "font" if "font_color" in p else "bkg"
                click.echo(f"    {p['suffix']}: {kind}={color}")

        if output:
            save_json(result, output)
            click.echo(f"\nWritten to {output}")
        return

    # All widgets
    result = analyze_all_colors(configs)

    click.echo(f"\nTotal unique palettes: {result['total_unique_palettes']}")
    click.echo(f"Total unique colors: {result['total_unique_colors']}")
    click.echo(f"Matched unpaired to palette: {result['total_matched']}")
    click.echo(f"Still unpaired: {result['total_still_unpaired']}")

    click.echo(f"\n  Most used palettes (font + bkg):")
    for entry in result["global_palettes"][:20]:
        click.echo(
            f"    font={entry['font_color']}  bkg={entry['bkg_color']}"
            f"  ({entry['count']}x)"
        )
    if len(result["global_palettes"]) > 20:
        click.echo(f"    ... and {len(result['global_palettes']) - 20} more")

    # Toon still unpaired per widget
    has_unpaired = {
        name: data["unpaired"]
        for name, data in result["per_widget"].items()
        if data["unpaired"]
    }
    if has_unpaired:
        click.echo(f"\n  Still unpaired ({result['total_still_unpaired']}):")
        for name, unpaired in sorted(has_unpaired.items()):
            for p in unpaired:
                color = p.get("font_color") or p.get("bkg_color")
                kind = "font" if "font_color" in p else "bkg"
                click.echo(f"    {name}.{p['suffix']}: {kind}={color}")

    if output:
        save_json(result, output)
        click.echo(f"\nWritten to {output}")


@cli.command()
@click.option(
    "--min-widgets",
    "-m",
    type=int,
    default=2,
    help="Minimum number of widgets sharing a suffix",
)
@click.option(
    "--min-attrs",
    "-a",
    type=int,
    default=2,
    help="Minimum shared attributes for reusable group",
)
@click.option(
    "--groups",
    "-g",
    is_flag=True,
    help="Show widget groups that share many suffixes",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Write results to JSON file",
)
@click.pass_context
def prefixes(ctx, min_widgets, min_attrs, groups, output):
    """Scan shared prefixes/suffixes for reusable dataclasses."""
    templates = ctx.obj["templates"]

    try:
        configs = load_configs(templates)
    except LoadError as e:
        click.echo(f"Error loading configurations: {e}", err=True)
        raise click.Exit(1)

    if groups:
        widget_groups = find_widget_groups(configs, min_shared=min_attrs)

        click.echo(f"\nWidget groups sharing {min_attrs}+ identical suffixes:")
        for group in widget_groups[:20]:
            w1, w2 = group["widgets"]
            click.echo(
                f"\n  {w1} <-> {w2}: "
                f"{group['identical_count']} identical, "
                f"{group['shared_count']} shared"
            )
            for suffix in group["identical_suffixes"][:10]:
                click.echo(f"    - {suffix}")
            if len(group["identical_suffixes"]) > 10:
                click.echo(
                    f"    ... and {len(group['identical_suffixes']) - 10} more"
                )

        if output:
            save_json(widget_groups, output)
            click.echo(f"\nWritten to {output}")
        return

    # Reusable dataclass candidates
    candidates = find_reusable_groups(configs, min_widgets, min_attrs)

    click.echo(f"\nReusable dataclass candidates ({len(candidates)}):")

    for c in candidates:
        click.echo(
            f"\n  {c['suffix']} ({c['widget_count']}x)"
        )
        click.echo(f"    widgets: {', '.join(c['widgets'])}")
        click.echo(f"    attrs:")
        for attr in c["attrs"]:
            value = c["values"].get(attr)
            click.echo(f"      {attr} = {repr(value)}")

    if output:
        save_json(candidates, output)
        click.echo(f"\nWritten to {output}")


@cli.command()
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Write results to JSON file",
)
@click.option(
    "--preview",
    "-p",
    is_flag=True,
    help="Show Python dataclass preview",
)
@click.pass_context
def suggest(ctx, output, preview):
    """Suggest dataclasses based on shared patterns."""
    templates = ctx.obj["templates"]

    try:
        configs = load_configs(templates)
    except LoadError as e:
        click.echo(f"Error loading configurations: {e}", err=True)
        raise click.Exit(1)

    suggestions = suggest_dataclasses(configs)

    click.echo(f"\nSuggested dataclasses: {len(suggestions)}")

    for s in suggestions:
        click.echo(
            f"\n  {s['class_name']} "
            f"({s['field_count']} fields, "
            f"used by {s['widget_count']} widgets)"
        )
        click.echo(f"    widgets: {', '.join(s['widgets'])}")
        for field in s["fields"]:
            attrs_str = ", ".join(
                f"{a}={repr(v)}" for a, v in sorted(field["attrs"].items())
            )
            click.echo(f"    - {field['name']}: {attrs_str}")

    if preview:
        click.echo("\n" + "=" * 60)
        click.echo("DATACLASS PREVIEW")
        click.echo("=" * 60)
        for s in suggestions:
            click.echo("")
            click.echo(format_dataclass(s))

    if output:
        save_json(suggestions, output)
        click.echo(f"\nWritten to {output}")


@cli.command()
@click.option(
    "--widget",
    "-w",
    help="Specific widget to analyze",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Write results to JSON file",
)
@click.pass_context
def rest(ctx, widget, output):
    """Show what remains after all known patterns are claimed."""
    templates = ctx.obj["templates"]

    try:
        configs = load_configs(templates)
    except LoadError as e:
        click.echo(f"Error loading configurations: {e}", err=True)
        raise click.Exit(1)

    # Welke widgets analyseren
    if widget:
        if widget not in configs:
            click.echo(f"Widget '{widget}' not found", err=True)
            raise click.Exit(1)
        targets = {widget: configs[widget]}
    else:
        targets = configs

    # Bekende groepen
    known_keys = set()
    for group in KNOWN_GROUPS.values():
        known_keys.update(group["keys"])

    # Auto-detected prefixes
    auto = find_auto_prefixes(configs)

    for wname, config in sorted(targets.items()):
        claimed = set()
        categories = {}

        # 1. Base/Font/Position (known groups)
        for group_name, group_info in KNOWN_GROUPS.items():
            found = {k: config[k] for k in group_info["keys"] if k in config}
            if found:
                categories[group_info["class_name"]] = found
                claimed.update(found.keys())

        # 2. Known prefix keys (font_color_*, bkg_color_*, etc)
        known_prefix_keys = {}
        for key in config:
            for prefix in KNOWN_PREFIXES:
                if key.startswith(prefix):
                    known_prefix_keys[key] = config[key]
                    claimed.add(key)
                    break

        # 3. Auto-detected prefix groups
        auto_claimed = {}
        for prefix, info in auto.items():
            if wname not in info["widgets"]:
                continue
            prefix_keys = {
                k: config[k] for k in config
                if k.startswith(prefix + "_") and k not in claimed
            }
            if prefix_keys:
                auto_claimed[prefix] = prefix_keys
                claimed.update(prefix_keys.keys())

        # 4. Wat blijft over
        remaining = {k: config[k] for k in config if k not in claimed}

        click.echo(f"\n{'=' * 50}")
        click.echo(f"{wname}: {len(config)} total keys")
        click.echo(f"{'=' * 50}")

        for cat_name, cat_keys in categories.items():
            click.echo(f"\n  {cat_name} ({len(cat_keys)}):")
            for k, v in sorted(cat_keys.items()):
                click.echo(f"    {k} = {repr(v)}")

        click.echo(f"\n  Known prefixes ({len(known_prefix_keys)}):")
        click.echo(f"    (font_color_*, bkg_color_*, show_*, column_index_*, etc)")

        if auto_claimed:
            click.echo(f"\n  Auto-detected groups ({len(auto_claimed)}):")
            for prefix, keys in sorted(auto_claimed.items()):
                click.echo(f"    [{prefix}] ({len(keys)} fields)")
                for k, v in sorted(keys.items()):
                    click.echo(f"      {k} = {repr(v)}")

        click.echo(f"\n  Remaining ({len(remaining)}):")
        for k, v in sorted(remaining.items()):
            click.echo(f"    {k} = {repr(v)}")

    # Samenvatting over alle widgets
    if not widget:
        click.echo(f"\n{'=' * 50}")
        click.echo("SUMMARY")
        click.echo(f"{'=' * 50}")

        # Bekende groepen coverage
        known = find_known_groups(configs)
        for group_name, info in known.items():
            click.echo(f"\n  {info['class_name']} ({info['widget_count']} widgets)")
            if info["identical"]:
                click.echo(f"    identical: {list(info['identical'].keys())}")
            if info["varying"]:
                click.echo(f"    varying: {list(info['varying'].keys())}")

        click.echo(f"\n  Auto-detected prefixes: {len(auto)}")
        for prefix, info in sorted(auto.items(), key=lambda x: -x[1]["widget_count"]):
            click.echo(
                f"    {prefix}: {info['field_count']} fields, "
                f"{info['widget_count']} widgets"
            )

    if output:
        save_json({"auto_prefixes": auto}, output)
        click.echo(f"\nWritten to {output}")


@cli.command()
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default=Path("output"),
    help="Output directory for generated widgets",
)
@click.option(
    "--widget",
    "-w",
    help="Build only a specific widget",
)
@click.pass_context
def build(ctx, output, widget):
    """Build nested widgets from flat configurations."""
    from .build.colors import prepare as prepare_colors
    from .build.components import prepare as prepare_components
    from .build.setup_jinja import create as create_env
    from .build.widgets import prepare as prepare_widget
    from .build.writer import write_all
    from .utils.clean import clean_output, list_existing_files

    templates = ctx.obj["templates"]

    try:
        configs = load_configs(templates)
    except LoadError as e:
        click.echo(f"Error loading configurations: {e}", err=True)
        raise click.Exit(1)

    # Check bestaande bestanden
    existing = list_existing_files(output)
    if existing:
        click.echo(f"\nFound {len(existing)} existing files in {output}")
        if click.confirm("Remove old files?", default=True):
            removed = clean_output(output)
            click.echo(f"  Removed {removed} files")
        else:
            click.echo("  Keeping old files (may cause conflicts)")

    click.echo(f"\nBuilding widgets from {templates}...")
    click.echo(f"Output directory: {output}")

    # 1. Scan colors
    color_result = analyze_all_colors(configs)
    palettes = prepare_colors(color_result["global_palettes"])
    click.echo(f"  Colors: {len(palettes)} palettes")

    # 2. Auto-detect prefixes
    auto_prefixes = find_auto_prefixes(configs)
    click.echo(f"  Auto prefixes: {len(auto_prefixes)}")

    # 3. Components (placeholder - nog geen prefix/numbered detectie)
    prefix_components = {}
    numbered_components = {}
    components = prepare_components(prefix_components, numbered_components)

    # 4. Prepare widgets
    if widget:
        if widget not in configs:
            click.echo(f"Widget '{widget}' not found", err=True)
            raise click.Exit(1)
        target_configs = {widget: configs[widget]}
    else:
        target_configs = configs

    widgets_data = []
    for name, config in sorted(target_configs.items()):
        data = prepare_widget(
            name, config, prefix_components, numbered_components, auto_prefixes
        )
        widgets_data.append(data)

    click.echo(f"  Widgets: {len(widgets_data)}")

    # 5. Setup Jinja en schrijf
    template_dir = Path(__file__).parent / "templates"
    env = create_env(template_dir)
    write_all(palettes, components, widgets_data, output, env)

    click.echo(f"\nDone! Generated {len(widgets_data)} widgets in {output}")


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
