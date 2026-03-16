# Auto-generated base classes

"""Base configuration classes with their default values."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any, Dict


@dataclass
class FlatMixin:
    """Mixin that adds serialization to any dataclass."""

    def to_flat(self) -> Dict[str, Any]:
        return {f.name: getattr(self, f.name) for f in fields(self)}

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "FlatMixin":
        """Create instance from flat dict. Keys match field names."""
        kwargs = {}
        for f in fields(cls):
            if f.name in data:
                kwargs[f.name] = data[f.name]
        return cls(**kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """Structured serialization. Same as to_flat for simple configs."""
        return {f.name: getattr(self, f.name) for f in fields(self)}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FlatMixin":
        """Create instance from structured dict."""
        kwargs = {}
        for f in fields(cls):
            if f.name in data:
                kwargs[f.name] = data[f.name]
        return cls(**kwargs)


@dataclass
class WidgetConfig:
    """Base class for all widgets."""

    name: str = ""
    enable: bool = True
    update_interval: int = 20
    opacity: float = 0.9
    bar_gap: int = 2
    bar_padding: float = 0.2
    layout: int = 0
    bkg_color: str = "#222222"

    def to_flat(self) -> Dict[str, Any]:
        return {f.name: getattr(self, f.name) for f in fields(self)}

    def to_dict(self) -> Dict[str, Any]:
        """Structured serialization — excludes name, nests sub-objects."""
        result = {}
        for f in fields(self):
            if f.name == "name":
                continue
            val = getattr(self, f.name)
            if hasattr(val, "to_dict"):
                result[f.name] = val.to_dict()
            else:
                result[f.name] = val
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WidgetConfig":
        """Create from structured dict. Subclasses override for nested fields."""
        kwargs = {}
        for f in fields(cls):
            if f.name in data:
                kwargs[f.name] = data[f.name]
        return cls(**kwargs)


@dataclass
class FontConfig(FlatMixin):
    """Font configuration."""

    font_name: str = "Consolas"
    font_size: int = 15
    font_weight: str = "Bold"
    font_offset_vertical: int = 0
    font_scale_caption: float = 0.8
    enable_auto_font_offset: bool = True


@dataclass
class PositionConfig(FlatMixin):
    """Position configuration."""

    position_x: int = 0
    position_y: int = 0


@dataclass
class BarConfig(FlatMixin):
    """Bar configuration."""

    bar_padding_horizontal: float = 0.4
    bar_padding_vertical: float = 0.3
    bar_width: int = 50
    horizontal_gap: int = 2
    vertical_gap: int = 2
    inner_gap: int = 0


@dataclass
class CellConfig(FlatMixin):
    """Cell configuration."""

    id: str = ""
    font_color: str = "#FFFFFF"
    bkg_color: str = "#222222"
    show: bool = True
    column_index: int = 0
    decimal_places: int = 0
    prefix: str = ""
    suffix: str = ""
    caption_text: str = ""

    def to_flat(self) -> Dict[str, Any]:
        result = {}
        for f in fields(self):
            if f.name == "id":
                continue
            result[f"{f.name}_{self.id}"] = getattr(self, f.name)
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any], cell_id: str) -> "CellConfig":
        """Create CellConfig from flat dict using cell_id suffix pattern."""
        kwargs = {"id": cell_id}
        for f in fields(cls):
            if f.name == "id":
                continue
            flat_key = f"{f.name}_{cell_id}"
            if flat_key in data:
                kwargs[f.name] = data[flat_key]
        return cls(**kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """Structured serialization — excludes id (used as key)."""
        return {f.name: getattr(self, f.name) for f in fields(self) if f.name != "id"}

    @classmethod
    def from_dict(cls, data: Dict[str, Any], cell_id: str) -> "CellConfig":
        """Create from structured dict with explicit cell_id."""
        return cls(id=cell_id, **{k: v for k, v in data.items() if k != "id"})


@dataclass
class HeatmapEntry:
    """Single temperature -> color mapping."""

    temperature: float
    color: str


@dataclass
class HeatmapConfig:
    """Named temperature-to-color gradient."""

    name: str
    entries: tuple = ()  # tuple[HeatmapEntry, ...], sorted by temperature

    def to_flat(self) -> Dict[str, str]:
        """Convert back to tinypedal format: {"-273": "#44F", ...}"""
        return {str(int(e.temperature)): e.color for e in self.entries}

    @classmethod
    def from_flat(cls, name: str, data: Dict[str, str]) -> "HeatmapConfig":
        """Create from tinypedal dict."""
        entries = tuple(sorted(
            (HeatmapEntry(float(temp), color) for temp, color in data.items()),
            key=lambda e: e.temperature,
        ))
        return cls(name=name, entries=entries)

    def to_dict(self) -> Dict[str, Any]:
        """Structured serialization."""
        return {"entries": [{"temperature": e.temperature, "color": e.color} for e in self.entries]}

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> "HeatmapConfig":
        """Create from structured dict."""
        entries = tuple(
            HeatmapEntry(**e) for e in data.get("entries", [])
        )
        return cls(name=name, entries=entries)


# --- Preset dataclasses ---


@dataclass
class BrakePreset:
    """Single brake preset entry."""

    name: str
    failure_thickness: float = 0.0
    heatmap: str = "HEATMAP_DEFAULT_BRAKE"

    def to_flat(self) -> Dict[str, Any]:
        return {f.name: getattr(self, f.name) for f in fields(self) if f.name != "name"}

    @classmethod
    def from_flat(cls, name: str, data: Dict[str, Any]) -> "BrakePreset":
        return cls(name=name, **{k: v for k, v in data.items() if k != "name"})

    def to_dict(self) -> Dict[str, Any]:
        return {f.name: getattr(self, f.name) for f in fields(self) if f.name != "name"}

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> "BrakePreset":
        return cls(name=name, **data)


@dataclass
class ClassPreset:
    """Single vehicle class preset entry."""

    name: str
    alias: str = "???"
    color: str = "#0044AA"
    preset: str = ""

    def to_flat(self) -> Dict[str, Any]:
        return {f.name: getattr(self, f.name) for f in fields(self) if f.name != "name"}

    @classmethod
    def from_flat(cls, name: str, data: Dict[str, Any]) -> "ClassPreset":
        return cls(name=name, **{k: v for k, v in data.items() if k != "name"})

    def to_dict(self) -> Dict[str, Any]:
        return {f.name: getattr(self, f.name) for f in fields(self) if f.name != "name"}

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> "ClassPreset":
        return cls(name=name, **data)


@dataclass
class CompoundPreset:
    """Single tyre compound preset entry."""

    name: str
    symbol: str = "?"
    heatmap: str = "HEATMAP_DEFAULT_TYRE"

    def to_flat(self) -> Dict[str, Any]:
        return {f.name: getattr(self, f.name) for f in fields(self) if f.name != "name"}

    @classmethod
    def from_flat(cls, name: str, data: Dict[str, Any]) -> "CompoundPreset":
        return cls(name=name, **{k: v for k, v in data.items() if k != "name"})

    def to_dict(self) -> Dict[str, Any]:
        return {f.name: getattr(self, f.name) for f in fields(self) if f.name != "name"}

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> "CompoundPreset":
        return cls(name=name, **data)
