#!/usr/bin/env python3
"""
lint_helper.py - Makkelijk linting errors doorgeven aan Kimi.

Usage:
    python lint_helper.py [file_or_folder] [options]

Examples:
    python lint_helper.py editors/heatmap/           # Alles in folder
    python lint_helper.py editors/heatmap/service.py # Specifiek file
    python lint_helper.py . --stats                  # Stats alleen
    python lint_helper.py . --fix                    # Auto-fix waar mogelijk
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_ruff(target: str, fix: bool = False) -> tuple[str, str, int]:
    """Run ruff check en return (stdout, stderr, returncode)."""
    cmd = ["ruff", "check", target, "--output-format=text"]

    if fix:
        cmd.append("--fix")

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode


def run_ruff_stats(target: str) -> str:
    """Run ruff met statistics."""
    cmd = ["ruff", "check", target, "--statistics"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout


def format_for_kimi(errors: str, max_lines: int = 100) -> str:
    """Format errors voor makkelijke copy-paste naar Kimi."""
    if not errors.strip():
        return "✅ Geen linting errors gevonden!"

    lines = errors.strip().split("\n")

    # Header
    output = [
        f"## Ruff Linting Resultaten",
        f"**Totaal errors:** {len(lines)}",
        f"**Eerste {max_lines} errors:**\n",
        "```",
    ]

    # Errors (gelimiteerd)
    for line in lines[:max_lines]:
        output.append(line)

    if len(lines) > max_lines:
        output.append(f"... en nog {len(lines) - max_lines} meer")

    output.append("```\n")

    # Samenvatting per file
    files = {}
    for line in lines:
        if ":" in line:
            filepath = line.split(":")[0]
            files[filepath] = files.get(filepath, 0) + 1

    if files:
        output.append("**Errors per file:**")
        for filepath, count in sorted(files.items(), key=lambda x: -x[1]):
            output.append(f"- `{filepath}`: {count} errors")

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="Lint helper voor TinyUi")
    parser.add_argument(
        "target", nargs="?", default=".", help="File of folder om te checken"
    )
    parser.add_argument("--fix", action="store_true", help="Auto-fix waar mogelijk")
    parser.add_argument("--stats", action="store_true", help="Alleen statistics tonen")
    parser.add_argument("--output", "-o", help="Output naar file (default: stdout)")
    parser.add_argument(
        "--max-lines", type=int, default=100, help="Max errors in output"
    )

    args = parser.parse_args()

    # Check of ruff geïnstalleerd is
    try:
        subprocess.run(["ruff", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Ruff niet gevonden. Installeer met: pip install ruff")
        sys.exit(1)

    target = args.target

    if args.stats:
        # Alleen statistics
        output = run_ruff_stats(target)
        print(output)
        return

    # Run ruff check
    stdout, stderr, code = run_ruff(target, fix=args.fix)

    # Format voor Kimi
    formatted = format_for_kimi(stdout, args.max_lines)

    # Output
    if args.output:
        Path(args.output).write_text(formatted)
        print(f"✅ Output geschreven naar: {args.output}")
    else:
        print(formatted)

    # Exit code
    sys.exit(code if code else 0)


if __name__ == "__main__":
    main()
