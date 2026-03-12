"""Schrijft gegenereerde files naar disk."""

from pathlib import Path
from typing import Any, Dict, List

from jinja2 import Environment


def write_components(
    components: List[tuple], output_dir: Path, env: Environment
) -> None:
    """Schrijf _components.py."""
    template = env.get_template("component.py.j2")
    content = template.render(components=components)

    path = output_dir / "_components.py"
    path.write_text(content, encoding="utf-8")


def write_base(output_dir: Path, env: Environment) -> None:
    """Schrijf _base.py."""
    template = env.get_template("base.py.j2")
    content = template.render()

    path = output_dir / "_base.py"
    path.write_text(content, encoding="utf-8")


def write_init(widget_names: List[str], output_dir: Path, env: Environment) -> None:
    """Schrijf __init__.py."""
    template = env.get_template("__init__.py.j2")
    content = template.render(widget_names=widget_names)

    path = output_dir / "__init__.py"
    path.write_text(content, encoding="utf-8")


def write_widget(data: Dict[str, Any], output_dir: Path, env: Environment) -> None:
    """Schrijf één widget file."""
    template = env.get_template("widget.py.j2")
    content = template.render(**data)

    path = output_dir / f"{data['name']}.py"
    path.write_text(content, encoding="utf-8")


def write_all(
    components: List[tuple],
    widgets_data: List[Dict],
    output_dir: Path,
    env: Environment,
) -> None:
    """Schrijf alle output files."""
    output_dir.mkdir(parents=True, exist_ok=True)

    write_components(components, output_dir, env)
    write_base(output_dir, env)

    widget_names = []
    for widget_data in widgets_data:
        write_widget(widget_data, output_dir, env)
        widget_names.append(widget_data["name"])

    write_init(widget_names, output_dir, env)
