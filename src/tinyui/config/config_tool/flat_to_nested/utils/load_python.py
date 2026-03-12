"""Laadt Python assignments uit .py files via AST."""

import ast
from pathlib import Path
from typing import Any, Dict


class LoadError(Exception):
    pass


def _eval(node: ast.AST) -> Any:
    """Evalueer AST node naar Python waarde."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Str):  # Python < 3.8
        return node.s
    if isinstance(node, ast.Num):  # Python < 3.8
        return node.n
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.List):
        return [_eval(e) for e in node.elts]
    if isinstance(node, ast.Dict):
        return _eval_dict(node)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_eval(node.operand)
    return None


def _eval_dict(node: ast.Dict) -> Dict[str, Any]:
    """Evalueer AST Dict node."""
    result = {}
    for k, v in zip(node.keys, node.values):
        key = _eval(k)
        if key is not None:
            result[key] = _eval(v)
    return result


def load_assignments(path: Path, target_name: str) -> Dict[str, Any]:
    """Laadt dict uit Python assignment (bijv. WIDGET_DEFAULT = {...})."""
    if not path.exists():
        raise LoadError(f"Python bestand niet gevonden: {path}")

    with open(path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == target_name:
                    return _eval_dict(node.value)

    raise LoadError(f"'{target_name}' niet gevonden in {path}")
