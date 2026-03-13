"""JSON output util."""

import json
from pathlib import Path
from typing import Any, Dict


def serialize_value(value: Any) -> Any:
    """Convert value to JSON-serializable format."""
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (list, tuple)):
        return [serialize_value(v) for v in value]
    if isinstance(value, dict):
        return {str(k): serialize_value(v) for k, v in value.items()}
    return str(value)


def save_json(data: Dict, path: Path) -> None:
    """Save data to JSON."""
    serialized = serialize_value(data)
    path.write_text(json.dumps(serialized, indent=2), encoding="utf-8")
