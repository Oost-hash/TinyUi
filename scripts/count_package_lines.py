"""Count tracked lines per package under src/.

By default this script counts only source-like text files:
  - .py
  - .qml
  - .toml

This keeps binary assets, submodules, fonts, and other noise out of the totals.

Examples:
  python scripts/count_package_lines.py
  python scripts/count_package_lines.py --extensions .py,.qml
  python scripts/count_package_lines.py --packages tinycore,tinyui,tinywidgets
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

DEFAULT_EXTENSIONS = (".py", ".qml", ".toml")
DEFAULT_PACKAGES = ("app", "plugins", "tinycore", "tinyui", "tinywidgets", "tinyui_schema")


def parse_csv(value: str) -> tuple[str, ...]:
    return tuple(part.strip() for part in value.split(",") if part.strip())


def git_tracked_files(repo_root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "src"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    return [repo_root / line for line in result.stdout.splitlines() if line.strip()]


def count_lines(path: Path) -> int:
    with path.open("r", encoding="utf-8") as handle:
        return sum(1 for _ in handle)


def main() -> int:
    parser = argparse.ArgumentParser(description="Count tracked source lines per src package.")
    parser.add_argument(
        "--extensions",
        default=",".join(DEFAULT_EXTENSIONS),
        help="Comma-separated extensions to include. Default: .py,.qml,.toml",
    )
    parser.add_argument(
        "--packages",
        default=",".join(DEFAULT_PACKAGES),
        help="Comma-separated package names under src/. Default: app,plugins,tinycore,tinyui,tinywidgets,tinyui_schema",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    extensions = tuple(ext if ext.startswith(".") else f".{ext}" for ext in parse_csv(args.extensions))
    wanted_packages = set(parse_csv(args.packages))

    totals: dict[str, int] = {package: 0 for package in wanted_packages}
    type_totals: dict[str, int] = {ext: 0 for ext in extensions}
    package_type_totals: dict[str, dict[str, int]] = {
        package: {ext: 0 for ext in extensions}
        for package in wanted_packages
    }

    for path in git_tracked_files(repo_root):
        rel = path.relative_to(repo_root)
        parts = rel.parts
        if len(parts) < 3:
            continue
        package = parts[1]
        if package not in wanted_packages:
            continue
        if path.suffix.lower() not in extensions:
            continue
        if not path.is_file():
            continue
        try:
            line_count = count_lines(path)
        except UnicodeDecodeError:
            # Binary or non-UTF8 file with a matching suffix; keep output stable.
            continue
        totals[package] += line_count
        type_totals[path.suffix.lower()] += line_count
        package_type_totals[package][path.suffix.lower()] += line_count

    rows = sorted(totals.items(), key=lambda item: item[1], reverse=True)
    name_width = max(len("Package"), *(len(name) for name, _ in rows))
    line_width = max(len("Lines"), *(len(str(lines)) for _, lines in rows))
    total_lines = sum(lines for _, lines in rows)

    percent_width = len("Percent")
    print(f"{'Package':<{name_width}}  {'Lines':>{line_width}}  {'Percent':>{percent_width}}")
    print(f"{'-' * name_width}  {'-' * line_width}  {'-' * percent_width}")
    for name, lines in rows:
        percent = (lines / total_lines * 100.0) if total_lines else 0.0
        print(f"{name:<{name_width}}  {lines:>{line_width}}  {percent:>{percent_width}.2f}%")
    print(f"{'-' * name_width}  {'-' * line_width}  {'-' * percent_width}")
    print(f"{'Total':<{name_width}}  {total_lines:>{line_width}}  {100.0:>{percent_width}.2f}%")

    type_rows = sorted(type_totals.items(), key=lambda item: item[1], reverse=True)
    type_width = max(len("Type"), *(len(ext) for ext, _ in type_rows))

    print()
    print(f"{'Type':<{type_width}}  {'Lines':>{line_width}}  {'Percent':>{percent_width}}")
    print(f"{'-' * type_width}  {'-' * line_width}  {'-' * percent_width}")
    for ext, lines in type_rows:
        percent = (lines / total_lines * 100.0) if total_lines else 0.0
        print(f"{ext:<{type_width}}  {lines:>{line_width}}  {percent:>{percent_width}.2f}%")

    print()
    matrix_header = f"{'Package':<{name_width}}"
    for ext in extensions:
        matrix_header += f"  {ext:>{percent_width}}"
    print(matrix_header)
    print(f"{'-' * name_width}" + "".join(f"  {'-' * percent_width}" for _ in extensions))
    for package, package_total in rows:
        line = f"{package:<{name_width}}"
        for ext in extensions:
            type_lines = package_type_totals[package][ext]
            percent = (type_lines / package_total * 100.0) if package_total else 0.0
            line += f"  {percent:>{percent_width}.2f}%"
        print(line)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
