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
DEFAULT_PACKAGES = ("runtime", "runtime_schema", "app_schema", "ui_api", "widget_api", "capabilities", "plugins")


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


# Banner fingerprints to detect
_BANNER_FINGERPRINTS = [
    "TinyUI",
    "Copyright (C) 2026 Oost-hash",
    "This file is part of TinyUI",
    "GNU General Public License",
    "licensed under GPLv3",
]


def count_lines(path: Path) -> tuple[int, int]:
    """Return (total_lines, banner_lines) for a file."""
    with path.open("r", encoding="utf-8") as handle:
        lines = list(handle)
    
    total = len(lines)
    banner_count = 0
    in_banner = False
    comment_char = "#" if path.suffix == ".py" else "//" if path.suffix == ".qml" else None
    
    for line in lines[:30]:  # Only check first 30 lines for banner
        stripped = line.strip()
        if comment_char and stripped.startswith(comment_char):
            if any(fp in stripped for fp in _BANNER_FINGERPRINTS):
                in_banner = True
        if in_banner and (not stripped or (comment_char and stripped.startswith(comment_char))):
            banner_count += 1
        elif in_banner:
            break
    
    return total, banner_count


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
        help="Comma-separated package names under src/. Default: runtime,runtime_schema,app_schema,ui_api,widget_api,capabilities,plugins",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    extensions = tuple(ext if ext.startswith(".") else f".{ext}" for ext in parse_csv(args.extensions))
    wanted_packages = set(parse_csv(args.packages))

    totals: dict[str, int] = {package: 0 for package in wanted_packages}
    banner_totals: dict[str, int] = {package: 0 for package in wanted_packages}
    type_totals: dict[str, int] = {ext: 0 for ext in extensions}
    type_banner_totals: dict[str, int] = {ext: 0 for ext in extensions}
    package_type_totals: dict[str, dict[str, int]] = {
        package: {ext: 0 for ext in extensions}
        for package in wanted_packages
    }
    package_type_banner_totals: dict[str, dict[str, int]] = {
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
            line_count, banner_count = count_lines(path)
        except UnicodeDecodeError:
            # Binary or non-UTF8 file with a matching suffix; keep output stable.
            continue
        totals[package] += line_count
        banner_totals[package] += banner_count
        type_totals[path.suffix.lower()] += line_count
        type_banner_totals[path.suffix.lower()] += banner_count
        package_type_totals[package][path.suffix.lower()] += line_count
        package_type_banner_totals[package][path.suffix.lower()] += banner_count

    rows = sorted(totals.items(), key=lambda item: item[1], reverse=True)
    name_width = max(len("Package"), *(len(name) for name, _ in rows))
    line_width = max(len("Total"), *(len(str(lines)) for _, lines in rows))
    code_width = max(len("Code"), *(len(str(lines - banner_totals[name])) for name, lines in rows))
    total_lines = sum(lines for _, lines in rows)
    total_banner = sum(banner_totals[name] for name, _ in rows)
    total_code = total_lines - total_banner

    percent_width = len("Percent")
    banner_width = len("Banner")
    
    print(f"{'Package':<{name_width}}  {'Total':>{line_width}}  {'Code':>{code_width}}  {'Banner':>{banner_width}}  {'Overhead':>{percent_width}}")
    print(f"{'-' * name_width}  {'-' * line_width}  {'-' * code_width}  {'-' * banner_width}  {'-' * percent_width}")
    for name, lines in rows:
        banner = banner_totals[name]
        code = lines - banner
        percent = (banner / lines * 100.0) if lines else 0.0
        print(f"{name:<{name_width}}  {lines:>{line_width}}  {code:>{code_width}}  {banner:>{banner_width}}  {percent:>{percent_width}.1f}%")
    print(f"{'-' * name_width}  {'-' * line_width}  {'-' * code_width}  {'-' * banner_width}  {'-' * percent_width}")
    total_percent = (total_banner / total_lines * 100.0) if total_lines else 0.0
    print(f"{'Total':<{name_width}}  {total_lines:>{line_width}}  {total_code:>{code_width}}  {total_banner:>{banner_width}}  {total_percent:>{percent_width}.1f}%")

    type_rows = sorted(type_totals.items(), key=lambda item: item[1], reverse=True)
    type_width = max(len("Type"), *(len(ext) for ext, _ in type_rows))

    print()
    print(f"{'Type':<{type_width}}  {'Total':>{line_width}}  {'Code':>{code_width}}  {'Banner':>{banner_width}}  {'Overhead':>{percent_width}}")
    print(f"{'-' * type_width}  {'-' * line_width}  {'-' * code_width}  {'-' * banner_width}  {'-' * percent_width}")
    for ext, lines in type_rows:
        banner = type_banner_totals[ext]
        code = lines - banner
        percent = (banner / lines * 100.0) if lines else 0.0
        print(f"{ext:<{type_width}}  {lines:>{line_width}}  {code:>{code_width}}  {banner:>{banner_width}}  {percent:>{percent_width}.1f}%")

    print()
    print("Type distribution per package (percentage of package lines):")
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
            line += f"  {percent:>{percent_width}.0f}%"
        print(line)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

