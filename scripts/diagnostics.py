"""Compact diagnostics summary and inspection for basedpyright and qmllint."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Diagnostic:
    tool: str
    file: str
    line: int
    column: int
    severity: str
    code: str
    message: str


def _venv_python() -> Path:
    scripts_dir = ROOT / ".venv" / ("Scripts" if sys.platform == "win32" else "bin")
    return scripts_dir / ("python.exe" if sys.platform == "win32" else "python")


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def _basedpyright_cmd() -> list[str]:
    return [str(_venv_python()), "-m", "basedpyright", "--outputjson", "-p", str(ROOT)]


def load_basedpyright() -> tuple[list[Diagnostic], int]:
    result = _run(_basedpyright_cmd())
    try:
        payload = json.loads(result.stdout or "{}")
    except json.JSONDecodeError:
        message = (result.stderr or result.stdout or "basedpyright produced invalid JSON").strip()
        return [
            Diagnostic(
                tool="py",
                file="<basedpyright>",
                line=1,
                column=1,
                severity="error",
                code="tool-launch",
                message=message,
            )
        ], result.returncode or 1
    diagnostics = [
        Diagnostic(
            tool="py",
            file=item["file"],
            line=item["range"]["start"]["line"] + 1,
            column=item["range"]["start"]["character"] + 1,
            severity=item["severity"],
            code=item.get("rule", ""),
            message=item["message"],
        )
        for item in payload.get("generalDiagnostics", [])
    ]
    return diagnostics, result.returncode


QML_PATTERN = re.compile(
    r"^(Warning|Info|Error): (?P<file>.*?):(?P<line>\d+):(?P<column>\d+): (?P<message>.*?)(?: \[(?P<code>[^\]]+)\])?$"
)


def _qmllint_cmd() -> list[str]:
    return [str(_venv_python()), str(ROOT / "scripts" / "qmllint.py")]


def load_qmllint() -> tuple[list[Diagnostic], int]:
    result = _run(_qmllint_cmd())
    diagnostics: list[Diagnostic] = []
    for line in (result.stdout + "\n" + result.stderr).splitlines():
        match = QML_PATTERN.match(line.strip())
        if not match:
            continue
        severity = match.group(1).lower()
        diagnostics.append(
            Diagnostic(
                tool="qml",
                file=match.group("file"),
                line=int(match.group("line")),
                column=int(match.group("column")),
                severity=severity,
                code=match.group("code") or "",
                message=match.group("message"),
            )
        )
    if not diagnostics and result.returncode not in {0, 1}:
        message = (result.stderr or result.stdout or "qmllint failed to start").strip()
        diagnostics.append(
            Diagnostic(
                tool="qml",
                file="<qmllint>",
                line=1,
                column=1,
                severity="error",
                code="tool-launch",
                message=message,
            )
        )
    return diagnostics, result.returncode


def load_tools(which: str) -> tuple[list[Diagnostic], dict[str, int]]:
    diagnostics: list[Diagnostic] = []
    exit_codes: dict[str, int] = {}
    if which in {"all", "py"}:
        py_diags, py_code = load_basedpyright()
        diagnostics.extend(py_diags)
        exit_codes["py"] = py_code
    if which in {"all", "qml"}:
        qml_diags, qml_code = load_qmllint()
        diagnostics.extend(qml_diags)
        exit_codes["qml"] = qml_code
    return diagnostics, exit_codes


def print_summary(
    diagnostics: list[Diagnostic],
    exit_codes: dict[str, int],
    *,
    oneline: bool,
) -> int:
    if not diagnostics:
        tools = ", ".join(sorted(exit_codes)) or "selected tools"
        print(f"clean: no diagnostics from {tools}")
        return 0

    by_tool = Counter(d.tool for d in diagnostics)
    by_severity = Counter(d.severity for d in diagnostics)
    by_code = Counter(d.code or "(none)" for d in diagnostics)

    tool_bits = " ".join(f"{tool}={count}" for tool, count in sorted(by_tool.items()))
    sev_bits = " ".join(f"{sev}={count}" for sev, count in sorted(by_severity.items()))
    code_bits = ", ".join(f"{code}={count}" for code, count in by_code.most_common(5))

    if oneline:
        print(f"diagnostics: {len(diagnostics)} | {tool_bits} | {sev_bits} | {code_bits}")
        return 1

    print(f"diagnostics: {len(diagnostics)}  {tool_bits}  {sev_bits}")
    print("top codes:")
    for code, count in by_code.most_common(8):
        print(f"  {count:>3}  {code}")

    print("first hits:")
    for diag in diagnostics[:12]:
        print(f"  [{diag.tool}] {diag.code or diag.severity}  {diag.file}:{diag.line}:{diag.column}  {diag.message}")

    return 1


def print_inspect(diagnostics: list[Diagnostic], needle: str, *, limit: int | None) -> int:
    needle_lower = needle.lower()
    matches = [
        diag
        for diag in diagnostics
        if needle_lower in diag.code.lower() or needle_lower in diag.message.lower()
    ]
    if not matches:
        print(f"no diagnostics matched '{needle}'")
        return 0

    print(f"matches for '{needle}': {len(matches)}")
    shown = matches if limit is None else matches[:limit]
    for diag in shown:
        print(f"[{diag.tool}] {diag.severity} {diag.code or '(no-code)'}")
        print(f"  {diag.file}:{diag.line}:{diag.column}")
        print(f"  {diag.message}")
    if limit is not None and len(matches) > limit:
        print(f"... {len(matches) - limit} more not shown; rerun with --all to show everything")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    summary = sub.add_parser("summary")
    summary.add_argument("--tool", choices=["all", "py", "qml"], default="all")
    summary.add_argument("--oneline", action="store_true")

    inspect = sub.add_parser("inspect")
    inspect.add_argument("needle")
    inspect.add_argument("--tool", choices=["all", "py", "qml"], default="all")
    inspect.add_argument("--limit", type=int, default=20)
    inspect.add_argument("--all", action="store_true")

    raw = sub.add_parser("raw")
    raw.add_argument("--tool", choices=["py", "qml"], required=True)

    args = parser.parse_args()

    if args.cmd == "raw":
        cmd = _basedpyright_cmd() if args.tool == "py" else _qmllint_cmd()
        result = subprocess.run(cmd, cwd=ROOT)
        return result.returncode

    diagnostics, exit_codes = load_tools(args.tool)
    if args.cmd == "summary":
        return print_summary(diagnostics, exit_codes, oneline=args.oneline)
    if args.cmd == "inspect":
        limit = None if args.all else args.limit
        return print_inspect(diagnostics, args.needle, limit=limit)
    return 1


if __name__ == "__main__":
    sys.exit(main())
