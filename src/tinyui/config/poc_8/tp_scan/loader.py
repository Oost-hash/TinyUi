"""Laadt templates uit Python files en retourneer ruwe configuraties."""

import ast
from pathlib import Path
from typing import Any, Dict


class LoadError(Exception):
    pass


def _eval(node: ast.AST) -> Any:
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Str):
        return node.s
    if isinstance(node, ast.Num):
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
    result = {}
    for k, v in zip(node.keys, node.values):
        key = _eval(k)
        if key is not None:
            result[key] = _eval(v)
    return result


def _resolve_refs(config: Dict[str, Any], heatmaps: Dict[str, Any]) -> Dict[str, Any]:
    result = {}
    for key, value in config.items():
        if isinstance(value, str) and value in heatmaps:
            result[key] = heatmaps[value]
        else:
            result[key] = value
    return result


def load_heatmaps(templates_dir: Path) -> Dict[str, Any]:
    path = templates_dir / "setting_heatmap.py"
    if not path.exists():
        raise LoadError(f"heatmap file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())

    heatmaps = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    if target.id == "HEATMAP_DEFAULT":
                        heatmaps = _eval_dict(node.value)
                    elif target.id.startswith("HEATMAP_DEFAULT_"):
                        heatmaps[target.id] = _eval(node.value)
    return heatmaps


def load_widget_configs(
    templates_dir: Path, heatmaps: Dict[str, Any]
) -> Dict[str, Dict[str, Any]]:
    path = templates_dir / "setting_widget.py"
    if not path.exists():
        raise LoadError(f"widget file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())

    raw_widgets = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "WIDGET_DEFAULT":
                    raw_widgets = _eval_dict(node.value)

    result = {}
    for name, config in raw_widgets.items():
        if not isinstance(config, dict):
            continue
        result[name] = _resolve_refs(config, heatmaps)
    return result
