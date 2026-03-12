#!/usr/bin/env python3
"""CLI voor patroon-gebaseerde scanner."""

import argparse
import json
from pathlib import Path

from .scanner import analyze_with_patterns


def main():
    parser = argparse.ArgumentParser(
        description="Analyseer templates met regex patronen"
    )
    parser.add_argument(
        "-t", "--templates", required=True, help="Pad naar templates directory"
    )
    parser.add_argument(
        "-p", "--patterns", required=True, help="Pad naar patterns JSON bestand"
    )
    parser.add_argument(
        "-o", "--output", default="component_analysis.json", help="Output JSON bestand"
    )
    parser.add_argument(
        "-f", "--first", type=int, help="Aantal willekeurige widgets om te analyseren"
    )
    args = parser.parse_args()

    templates_dir = Path(args.templates).resolve()
    patterns_path = Path(args.patterns).resolve()
    output_file = Path(args.output).resolve()

    # Laad patronen
    with open(patterns_path, "r", encoding="utf-8") as f:
        patterns = json.load(f)

    # Voer analyse uit
    report = analyze_with_patterns(templates_dir, patterns, args.first)

    # Schrijf weg
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"Analyse opgeslagen in {output_file}")


if __name__ == "__main__":
    main()
