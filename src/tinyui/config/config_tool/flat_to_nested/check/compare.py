"""Valideert gegenereerde widgets tegen originele configs."""

import importlib
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


def _import_generated_module(output_dir: Path) -> Any:
    """Importeer gegenereerde widget package."""
    sys.path.insert(0, str(output_dir.parent))
    module_name = output_dir.name

    try:
        module = importlib.import_module(module_name)
        return getattr(module, "REGISTRY")
    except (ImportError, AttributeError) as e:
        raise ImportError(f"Kan gegenereerde module niet laden: {e}")


def _flatten_widget(widget) -> Dict[str, Any]:
    """Roep to_flat() aan op widget instance."""
    return widget.to_flat()


def validate(
    original_configs: Dict[str, Dict[str, Any]], output_dir: Path
) -> List[Tuple[str, List[str]]]:
    """
    Vergelijk originele configs met gegenereerde widgets.

    Returns: lijst van (widget_name, [foutmeldingen])
    """
    try:
        registry = _import_generated_module(output_dir)
    except ImportError as e:
        return [("module", [str(e)])]

    errors = []

    for name, orig_flat in original_configs.items():
        widget_errors = []

        # Check of widget bestaat
        if name not in registry:
            errors.append((name, ["Niet gevonden in REGISTRY"]))
            continue

        # Instantieer widget
        try:
            widget = registry[name]()
        except Exception as e:
            errors.append((name, [f"Kan niet instantieren: {e}"]))
            continue

        # Genereer flat dict
        try:
            gen_flat = _flatten_widget(widget)
        except Exception as e:
            errors.append((name, [f"to_flat() fout: {e}"]))
            continue

        # Vergelijk
        for key, value in orig_flat.items():
            if key not in gen_flat:
                widget_errors.append(f"Ontbrekende key: {key}")
            elif gen_flat[key] != value:
                widget_errors.append(
                    f"Verschil bij {key}: orig={value}, gen={gen_flat[key]}"
                )

        # Check extra keys (behalve 'name')
        for key in gen_flat:
            if key not in orig_flat and key != "name":
                widget_errors.append(f"Extra key: {key}")

        if widget_errors:
            errors.append((name, widget_errors))

    return errors


def print_report(errors: List[Tuple[str, List[str]]]) -> bool:
    """Print validatie rapport. Returns True als alles OK."""
    if not errors:
        print("✅ Alle widgets correct gegenereerd")
        return True

    print(f"❌ Fouten in {len(errors)} widgets:\n")
    for name, msgs in errors:
        print(f"  {name}:")
        for msg in msgs:
            print(f"    - {msg}")

    return False
