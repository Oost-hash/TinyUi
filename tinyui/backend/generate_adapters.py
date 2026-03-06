#!/usr/bin/env python3
"""
Generate adapter layer files from manifest.json.
Delete and recreate every run. No caching, no watchers.

Supports aliases: ["OriginalName", "AliasName"] or just "Name"
"""

import json
import os
import sys
from pathlib import Path

# This file lives in tinyui/backend/, manifest is alongside it
ADAPTER_DIR = Path(__file__).parent
MANIFEST_FILE = ADAPTER_DIR / "manifest.json"

# Files to preserve (don't delete these)
PRESERVE_FILES = {"__init__.py", "generate_adapters.py", "manifest.json"}

HEADER = '''"""
Auto-generated adapter file. Do not edit manually.
Generated from manifest.json - update there instead.
"""

'''


def load_manifest():
    """Load and validate manifest."""
    if not MANIFEST_FILE.exists():
        print(f"Error: {MANIFEST_FILE} not found")
        sys.exit(1)

    with open(MANIFEST_FILE, "r") as f:
        return json.load(f)


def delete_generated_files():
    """Remove all generated .py files, preserve essentials."""
    for f in ADAPTER_DIR.glob("*.py"):
        if f.name not in PRESERVE_FILES:
            f.unlink()
            print(f"  Deleted: {f.name}")


def parse_import_entry(entry):
    """Parse import entry, returns (original_name, alias_or_none)."""
    if isinstance(entry, str):
        return entry, None
    elif isinstance(entry, list) and len(entry) == 2:
        return entry[0], entry[1]
    else:
        raise ValueError(f"Invalid import entry: {entry}")


def generate_import_line(module, entries):
    """Generate 'from module import ...' line with optional aliases."""
    imports = []
    for entry in entries:
        orig, alias = parse_import_entry(entry)
        if alias:
            imports.append(f"{orig} as {alias}")
        else:
            imports.append(orig)

    if len(imports) == 1:
        return f"from {module} import {imports[0]}\n"

    lines = [f"from {module} import ("]
    for imp in imports:
        lines.append(f"    {imp},")
    lines.append(")\n")
    return "\n".join(lines)


def generate_file(filename, imports):
    """Generate a single adapter file."""
    filepath = ADAPTER_DIR / filename

    lines = [HEADER]

    # Group by module, generate import lines
    for module, entries in imports.items():
        lines.append(generate_import_line(module, entries))

    content = "\n".join(lines)

    with open(filepath, "w") as f:
        f.write(content)

    print(f"  Generated: {filename}")


def generate():
    """Main entry point."""
    print(f"Loading {MANIFEST_FILE.name}...")
    manifest = load_manifest()

    print(f"\nCleaning {ADAPTER_DIR.name}...")
    delete_generated_files()

    print(f"\nGenerating files...")
    for filename, imports in manifest.items():
        generate_file(filename, imports)

    print(f"\nDone. {len(manifest)} file(s) generated.")


if __name__ == "__main__":
    generate()
