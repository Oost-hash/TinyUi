"""Loaders for preset configs — brakes, classes, compounds."""

from pathlib import Path

from tinycore.config import read_json, write_json
from plugins.tinypedal.models.base import BrakePreset, ClassPreset, CompoundPreset


class BrakePresetLoader:
    """Load/save brake presets as structured JSON."""

    def load(self, path: Path) -> dict[str, BrakePreset]:
        data = read_json(path)
        return {name: BrakePreset.from_dict(name, entry) for name, entry in data.items()}

    def save(self, path: Path, config: dict[str, BrakePreset]) -> None:
        write_json(path, {name: bp.to_dict() for name, bp in config.items()})


class ClassPresetLoader:
    """Load/save class presets as structured JSON."""

    def load(self, path: Path) -> dict[str, ClassPreset]:
        data = read_json(path)
        return {name: ClassPreset.from_dict(name, entry) for name, entry in data.items()}

    def save(self, path: Path, config: dict[str, ClassPreset]) -> None:
        write_json(path, {name: cp.to_dict() for name, cp in config.items()})


class CompoundPresetLoader:
    """Load/save compound presets as structured JSON."""

    def load(self, path: Path) -> dict[str, CompoundPreset]:
        data = read_json(path)
        return {name: CompoundPreset.from_dict(name, entry) for name, entry in data.items()}

    def save(self, path: Path, config: dict[str, CompoundPreset]) -> None:
        write_json(path, {name: cp.to_dict() for name, cp in config.items()})
