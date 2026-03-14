"""Scan commands: scan, colors, prefixes, suggest, rest."""

import random
from pathlib import Path

import click

from ..io import LoadError, load_configs, save_json
from ..scan.color_palettes import analyze_all_colors, analyze_widget_colors
from ..scan.columns import (
    analyze_all_cells,
    analyze_all_columns,
    analyze_widget_cells,
    analyze_widget_columns,
)
from ..model import CELL_PREFIXES, KNOWN_GROUPS
from ..scan.prefixes import (
    find_auto_prefixes,
    find_known_groups,
    find_reusable_groups,
    find_widget_groups,
)
from ..scan.suggest import format_dataclass, suggest_dataclasses
from .shared import cli, format_value


@cli.command()
@click.option("--widget", "-w", help="Specific widget to scan")
@click.option("--sample", "-s", type=int, help="Random sample of N widgets")
@click.option("--vars", "-v", "show_vars", is_flag=True, help="Show all configuration variables")
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Write scan results to JSON file")
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

    if sample:
        if sample >= len(configs):
            selected = list(configs.keys())
        else:
            selected = random.sample(list(configs.keys()), sample)
        configs = {k: configs[k] for k in selected}
        click.echo(f"\nRandom sample of {len(configs)} widgets")

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

    all_cells = analyze_all_cells(configs)
    all_columns = analyze_all_columns(configs)

    total_cells = sum(len(c) for c in all_cells.values())
    total_cols = sum(len(cols) for cols in all_columns.values())
    click.echo(f"\nFound {total_cells} cells, {total_cols} layout columns across {len(configs)} widgets")

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
@click.option("--widget", "-w", help="Specific widget to analyze")
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Write results to JSON file")
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
@click.option("--min-widgets", "-m", type=int, default=2, help="Minimum number of widgets sharing a suffix")
@click.option("--min-attrs", "-a", type=int, default=2, help="Minimum shared attributes for reusable group")
@click.option("--groups", "-g", is_flag=True, help="Show widget groups that share many suffixes")
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Write results to JSON file")
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

    candidates = find_reusable_groups(configs, min_widgets, min_attrs)

    click.echo(f"\nReusable dataclass candidates ({len(candidates)}):")

    for c in candidates:
        click.echo(f"\n  {c['suffix']} ({c['widget_count']}x)")
        click.echo(f"    widgets: {', '.join(c['widgets'])}")
        click.echo(f"    attrs:")
        for attr in c["attrs"]:
            value = c["values"].get(attr)
            click.echo(f"      {attr} = {repr(value)}")

    if output:
        save_json(candidates, output)
        click.echo(f"\nWritten to {output}")


@cli.command()
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Write results to JSON file")
@click.option("--preview", "-p", is_flag=True, help="Show Python dataclass preview")
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
        for field_item in s["fields"]:
            attrs_str = ", ".join(
                f"{a}={repr(v)}" for a, v in sorted(field_item["attrs"].items())
            )
            click.echo(f"    - {field_item['name']}: {attrs_str}")

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
@click.option("--widget", "-w", help="Specific widget to analyze")
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Write results to JSON file")
@click.pass_context
def rest(ctx, widget, output):
    """Show what remains after all known patterns are claimed."""
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
        targets = {widget: configs[widget]}
    else:
        targets = configs

    claimed_group_keys = set()
    for group_keys in KNOWN_GROUPS.values():
        claimed_group_keys.update(group_keys)

    auto = find_auto_prefixes(configs)

    for wname, config in sorted(targets.items()):
        claimed = set()
        categories = {}

        group_names = {"font": "FontConfig", "position": "PositionConfig", "bar": "BarConfig", "base": "WidgetBase"}
        for group_name, group_keys in KNOWN_GROUPS.items():
            found = {k: config[k] for k in group_keys if k in config}
            if found:
                categories[group_names[group_name]] = found
                claimed.update(found.keys())

        known_prefix_keys = {}
        for key in config:
            for prefix in CELL_PREFIXES:
                if key.startswith(prefix):
                    known_prefix_keys[key] = config[key]
                    claimed.add(key)
                    break

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

    if not widget:
        click.echo(f"\n{'=' * 50}")
        click.echo("SUMMARY")
        click.echo(f"{'=' * 50}")

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
