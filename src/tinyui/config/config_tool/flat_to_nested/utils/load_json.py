"""Laadt JSON bestanden (patterns, analysis)."""

import json
from pathlib import Path
from typing import Any, Dict


def load(path: Path) -> Dict[str, Any]:
    """Laadt JSON bestand."""
    if not path.exists():
        raise FileNotFoundError(f"JSON bestand niet gevonden: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save(data: Dict[str, Any], path: Path) -> None:
    """Slaat dict op als JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
