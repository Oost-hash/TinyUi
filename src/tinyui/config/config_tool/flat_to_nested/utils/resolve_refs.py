"""Resolves string references to heatmap values."""

from typing import Any, Dict


def resolve(
    configs: Dict[str, Dict[str, Any]], heatmaps: Dict[str, Any]
) -> Dict[str, Dict[str, Any]]:
    """Vervangt string waarden die verwijzen naar heatmaps."""
    result = {}
    for name, config in configs.items():
        resolved = {}
        for key, value in config.items():
            if isinstance(value, str) and value in heatmaps:
                resolved[key] = heatmaps[value]
            else:
                resolved[key] = value
        result[name] = resolved
    return result
