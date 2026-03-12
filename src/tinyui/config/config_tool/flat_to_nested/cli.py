"""Command line interface voor flat_to_nested."""

import argparse
import sys
from pathlib import Path

from flat_to_nested.build import create, prepare_components, prepare_widget, write_all
from flat_to_nested.check import print_report, validate
from flat_to_nested.scan import Matcher, aggregate, collect_by_component, is_column
from flat_to_nested.scan.columns import (
    analyze_all_columns,
    analyze_widget_columns,
    find_column_inconsistencies,
)
from flat_to_nested.utils import load_assignments, load_json, resolve


def do_scan(args, configs):
    """Voer scan uit op basis van args."""

    if args.scan == "columns":
        if args.widget:
            # Scan specifieke widget
            if args.widget not in configs:
                print(f"Widget '{args.widget}' niet gevonden")
                return 1

            print(f"\nKolommen in '{args.widget}':")
            columns = analyze_widget_columns(args.widget, configs[args.widget])

            for col in columns:
                print(f"\n  Kolom: {col['id']}")
                print(f"    show_key: {col['show_key']}")
                for attr, key in col.items():
                    if attr not in ("id", "show_key"):
                        print(f"    {attr}: {key}")

                # Check inconsistentie
                show_suffix = col["show_key"][5:] if col.get("show_key") else ""
                if col["id"] != show_suffix:
                    print(
                        f"    ⚠️  Inconsistent: id='{col['id']}' vs show='{col['show_key']}'"
                    )

        else:
            # Scan alle widgets
            print(f"\nKolommen in {len(configs)} widgets:")
            all_columns = analyze_all_columns(configs)

            for widget_name, columns in all_columns.items():
                if columns:
                    print(f"\n{widget_name}: {len(columns)} kolommen")
                    for col in columns:
                        print(f"  - {col['id']} (via {col['show_key']})")

            # Toon inconsistenties
            inconsistencies = find_column_inconsistencies(all_columns)
            if inconsistencies:
                print(f"\n⚠️  {len(inconsistencies)} inconsistenties:")
                for inc in inconsistencies[:10]:
                    print(f"  {inc['widget']}: {inc['column_id']} vs {inc['show_key']}")

    elif args.scan == "components":
        key_values = {}
        for cfg in configs.values():
            for key, value in cfg.items():
                if not is_column(key, []):
                    key_values.setdefault(key, []).append(value)

        matcher = Matcher(load_json(args.patterns))
        prefix_comps, numbered_comps = collect_by_component(
            key_values, matcher, configs
        )

        print(f"\nPrefix componenten: {len(prefix_comps)}")
        for name, data in prefix_comps.items():
            print(
                f"  {name}: {len(data['suffixes'])} attrs, {len(data['widgets'])} widgets"
            )

        print(f"\nNumbered componenten: {len(numbered_comps)}")
        for name, data in numbered_comps.items():
            print(
                f"  {name}: {len(data['indices'])} indices, {len(data['attributes'])} attrs"
            )

    elif args.scan == "keys":
        if args.widget:
            if args.widget not in configs:
                print(f"Widget '{args.widget}' niet gevonden")
                return 1

            print(f"\nKeys in '{args.widget}':")
            for key in sorted(configs[args.widget].keys()):
                print(f"  {key}")
        else:
            all_keys = set()
            for cfg in configs.values():
                all_keys.update(cfg.keys())

            print(f"\n{len(all_keys)} unieke keys in {len(configs)} widgets:")
            for key in sorted(all_keys)[:50]:
                print(f"  {key}")
            if len(all_keys) > 50:
                print(f"  ... en {len(all_keys) - 50} meer")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Genereer gestructureerde widgets uit platte configs"
    )
    parser.add_argument(
        "-t", "--templates", required=True, help="Pad naar templates directory"
    )
    parser.add_argument(
        "-p", "--patterns", default="patterns.json", help="Pad naar patterns JSON"
    )
    parser.add_argument("-o", "--output", default="output", help="Output directory")
    parser.add_argument(
        "-s",
        "--scan",
        choices=["columns", "components", "keys"],
        help="Scan mode: columns, components, of keys",
    )
    parser.add_argument("-w", "--widget", help="Specifieke widget (bij --scan)")
    parser.add_argument(
        "-a",
        "--analyse",
        action="store_true",
        help="Analyse JSON wegschrijven (vervangt --analysis-only)",
    )
    parser.add_argument(
        "--validate", action="store_true", help="Valideer gegenereerde code"
    )
    parser.add_argument("--sample", type=int, help="Sample N willekeurige widgets")

    args = parser.parse_args()

    paths = {
        "templates": Path(args.templates).resolve(),
        "patterns": Path(args.patterns).resolve(),
        "output": Path(args.output).resolve(),
    }

    # Laad data
    try:
        patterns = load_json(paths["patterns"])
    except FileNotFoundError as e:
        print(f"Fout: {e}")
        return 1

    try:
        heatmaps = load_assignments(
            paths["templates"] / "setting_heatmap.py", "HEATMAP_DEFAULT"
        )
        raw_widgets = load_assignments(
            paths["templates"] / "setting_widget.py", "WIDGET_DEFAULT"
        )
    except Exception as e:
        print(f"Fout bij laden templates: {e}")
        return 1

    configs = resolve(raw_widgets, heatmaps)

    # Sample
    if args.sample and args.sample < len(configs):
        import random

        selected = random.sample(list(configs.keys()), args.sample)
        configs = {k: configs[k] for k in selected}
        print(f"Sample: {len(configs)} widgets")

    # Scan mode
    if args.scan:
        return do_scan(args, configs)

    # Analyse mode (JSON output)
    if args.analyse:
        key_values = {}
        for cfg in configs.values():
            for key, value in cfg.items():
                if not is_column(key, []):
                    key_values.setdefault(key, []).append(value)

        matcher = Matcher(patterns)
        prefix_comps, numbered_comps = collect_by_component(
            key_values, matcher, configs
        )

        from flat_to_nested.utils.load_json import save

        save(
            {
                "prefix_components": prefix_comps,
                "numbered_components": numbered_comps,
            },
            paths["output"].with_suffix(".json"),
        )

        print(f"Analyse: {paths['output']}.json")
        return 0

    # Generate mode
    print(f"Genereren {len(configs)} widgets...")

    template_dir = Path(__file__).parent / "templates"
    env = create(template_dir)

    key_values = {}
    for cfg in configs.values():
        for key, value in cfg.items():
            if not is_column(key, []):
                key_values.setdefault(key, []).append(value)

    matcher = Matcher(patterns)
    prefix_comps, numbered_comps = collect_by_component(key_values, matcher, configs)

    components = prepare_components(prefix_comps, numbered_comps)

    widgets_data = []
    for name, cfg in configs.items():
        data = prepare_widget(name, cfg, prefix_comps, numbered_comps)
        widgets_data.append(data)
        print(f"  {name}.py")

    write_all(components, widgets_data, paths["output"], env)
    print(f"\n✅ {len(widgets_data)} widgets → {paths['output']}")

    if args.validate:
        print("\nValideren...")
        errors = validate(configs, paths["output"])
        if not print_report(errors):
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
