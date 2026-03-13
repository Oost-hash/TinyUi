"""Output directory cleaning."""

from pathlib import Path
from typing import List


def list_existing_files(output_dir: Path) -> List[Path]:
    """Lijst alle .py bestanden in de output directory."""
    if not output_dir.exists():
        return []
    return sorted(output_dir.glob("*.py"))


def clean_output(output_dir: Path) -> int:
    """Verwijder alle .py bestanden uit de output directory.

    Returns het aantal verwijderde bestanden.
    """
    files = list_existing_files(output_dir)
    for f in files:
        f.unlink()
    return len(files)
