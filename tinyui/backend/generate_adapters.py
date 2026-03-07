#!/usr/bin/env python3
"""
Generate adapter layer files from manifest.json.
Only touches files defined in the manifest — hand-written files are never deleted.
Skips writing when content is unchanged.

Supports aliases: ["OriginalName", "AliasName"] or just "Name"
"""

import json
import sys
from pathlib import Path

ADAPTER_DIR = Path(__file__).parent
MANIFEST_FILE = ADAPTER_DIR / "manifest.json"

HEADER = '"""\nAuto-generated adapter file. Do not edit manually.\nGenerated from manifest.json - update there instead.\n"""\n\n'


def load_manifest():
    """Load manifest, exit on failure."""
    if not MANIFEST_FILE.exists():
        print(f"Error: {MANIFEST_FILE} not found")
        sys.exit(1)
    with open(MANIFEST_FILE, "r") as f:
        return json.load(f)


def parse_import_entry(entry):
    """Parse import entry, returns (original_name, alias_or_none)."""
    if isinstance(entry, str):
        return entry, None
    if isinstance(entry, list) and len(entry) == 2:
        return entry[0], entry[1]
    raise ValueError(f"Invalid import entry: {entry}")


def generate_import_line(module, entries):
    """Generate 'from module import ...' line with optional aliases."""
    imports = []
    for entry in entries:
        orig, alias = parse_import_entry(entry)
        imports.append(f"{orig} as {alias}" if alias else orig)

    if len(imports) == 1:
        return f"from {module} import {imports[0]}\n"

    items = "".join(f"    {imp},\n" for imp in imports)
    return f"from {module} import (\n{items})\n"


def build_content(imports):
    """Build full file content from import definitions."""
    parts = [HEADER]
    for module, entries in imports.items():
        parts.append(generate_import_line(module, entries))
    return "\n".join(parts)


def write_if_changed(filepath, content):
    """Write file only when content differs. Returns True if written."""
    if filepath.exists():
        if filepath.read_text() == content:
            return False
    filepath.write_text(content)
    return True


def generate():
    """Main entry point."""
    print(f"Loading {MANIFEST_FILE.name}...")
    manifest = load_manifest()

    written = 0
    skipped = 0
    for filename, imports in manifest.items():
        filepath = ADAPTER_DIR / filename
        content = build_content(imports)
        if write_if_changed(filepath, content):
            print(f"  Generated: {filename}")
            written += 1
        else:
            skipped += 1

    print(f"\nDone. {written} written, {skipped} unchanged.")


if __name__ == "__main__":
    generate()
