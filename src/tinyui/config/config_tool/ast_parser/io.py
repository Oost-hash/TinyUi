"""IO utilities: laden van configs en opslaan van resultaten."""

import ast
import json
from pathlib import Path
from typing import Any, Dict


class LoadError(Exception):
    pass


# --- Python file loading ---

def _eval_node(node: ast.AST) -> Any:
    """Evalueer AST node naar Python waarde."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.List):
        return [_eval_node(e) for e in node.elts]
    if isinstance(node, ast.Dict):
        return {
            _eval_node(k): _eval_node(v)
            for k, v in zip(node.keys, node.values)
            if k is not None
        }
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_eval_node(node.operand)
    return None


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
                    return _eval_node(node.value)

    raise LoadError(f"'{target_name}' niet gevonden in {path}")


def load_configs(templates_path: Path) -> Dict[str, Dict]:
    """Load widget configurations from templates directory."""
    heatmaps = load_assignments(
        templates_path / "setting_heatmap.py", "HEATMAP_DEFAULT"
    )
    raw_widgets = load_assignments(
        templates_path / "setting_widget.py", "WIDGET_DEFAULT"
    )

    configs = {}
    for widget_name, widget_config in raw_widgets.items():
        resolved = {}
        for key, value in widget_config.items():
            if isinstance(value, str) and value.startswith("HEATMAP["):
                heatmap_key = value[8:-1]
                resolved[key] = heatmaps.get(heatmap_key, value)
            else:
                resolved[key] = value
        configs[widget_name] = resolved

    return configs


# --- JSON ---

def load_json(path: Path) -> Dict[str, Any]:
    """Laadt JSON bestand."""
    if not path.exists():
        raise FileNotFoundError(f"JSON bestand niet gevonden: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: Any, path: Path) -> None:
    """Slaat data op als JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)

    def serialize(value):
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, (list, tuple)):
            return [serialize(v) for v in value]
        if isinstance(value, dict):
            return {str(k): serialize(v) for k, v in value.items()}
        if isinstance(value, set):
            return sorted(str(v) for v in value)
        return str(value)

    path.write_text(
        json.dumps(serialize(data), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
