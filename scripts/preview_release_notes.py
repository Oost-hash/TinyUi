"""Preview release notes for one version without mutating unreleased state."""

from __future__ import annotations

import argparse
from pathlib import Path

from release_notes import build_release_body, parse_unreleased, sections_for_version

ROOT = Path(__file__).resolve().parents[1]
UNRELEASED = ROOT / "docs" / "unreleased_changelog.md"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preview release notes for one unreleased version.")
    parser.add_argument("version", help="Version tag to render, for example 0.3.1")
    parser.add_argument(
        "--output",
        help="Optional file path to write the previewed notes to. Prints to stdout when omitted.",
    )
    parser.add_argument(
        "--with-header",
        action="store_true",
        help="Include a changelog-style version header in the generated output.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    _, entries = parse_unreleased(UNRELEASED)
    body = build_release_body(sections_for_version(entries, args.version))
    if not body:
        print(f"No unreleased entries found for version {args.version}.")
        return 1

    output = body
    if args.with_header:
        output = f"## [{args.version}]\n\n{body}"

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(output + "\n", encoding="utf-8")
        print(f"Wrote release notes preview: {output_path}")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
