# Auto-generated widget
# Widget: tyre_temperature

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import BarConfig, CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..colors import COMPOUND, DARK_INVERT, DEFAULT


@dataclass
class TyreTemperature(WidgetConfig):
    name: str = "tyre_temperature"

    # groups
    bar: BarConfig = field(default_factory=lambda: BarConfig(horizontal_gap=0, vertical_gap=0))
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=249, position_y=525))

    # cells
    degree_sign: CellConfig = field(default_factory=lambda: CellConfig(id='degree_sign', show=False))
    inner_center_outer: CellConfig = field(default_factory=lambda: CellConfig(id='inner_center_outer'))
    surface: CellConfig = field(default_factory=lambda: CellConfig(id='surface', font_color=DARK_INVERT.font_color, bkg_color=DARK_INVERT.bkg_color))
    tyre_compound: CellConfig = field(default_factory=lambda: CellConfig(id='tyre_compound', font_color=COMPOUND.font_color, bkg_color=COMPOUND.bkg_color))

    # config
    enable_heatmap_auto_matching: bool = True
    heatmap_name: str = 'HEATMAP_DEFAULT_TYRE'
    leading_zero: int = 2
    swap_style: bool = False

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result.update(self.bar.to_flat())
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.degree_sign.to_flat())
        result.update(self.inner_center_outer.to_flat())
        result.update(self.surface.to_flat())
        result.update(self.tyre_compound.to_flat())
        result["enable_heatmap_auto_matching"] = self.enable_heatmap_auto_matching
        result["heatmap_name"] = self.heatmap_name
        result["leading_zero"] = self.leading_zero
        result["swap_style"] = self.swap_style
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "TyreTemperature":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar = BarConfig.from_flat(data)
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.degree_sign = CellConfig.from_flat(data, 'degree_sign')
        obj.inner_center_outer = CellConfig.from_flat(data, 'inner_center_outer')
        obj.surface = CellConfig.from_flat(data, 'surface')
        obj.tyre_compound = CellConfig.from_flat(data, 'tyre_compound')
        obj.enable_heatmap_auto_matching = data.get("enable_heatmap_auto_matching", obj.enable_heatmap_auto_matching)
        obj.heatmap_name = data.get("heatmap_name", obj.heatmap_name)
        obj.leading_zero = data.get("leading_zero", obj.leading_zero)
        obj.swap_style = data.get("swap_style", obj.swap_style)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["bar"] = self.bar.to_dict()
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["degree_sign"] = self.degree_sign.to_dict()
        result["inner_center_outer"] = self.inner_center_outer.to_dict()
        result["surface"] = self.surface.to_dict()
        result["tyre_compound"] = self.tyre_compound.to_dict()
        result["enable_heatmap_auto_matching"] = self.enable_heatmap_auto_matching
        result["heatmap_name"] = self.heatmap_name
        result["leading_zero"] = self.leading_zero
        result["swap_style"] = self.swap_style
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TyreTemperature":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar = BarConfig.from_dict(data.get("bar", {}))
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.degree_sign = CellConfig.from_dict(data.get("degree_sign", {}), 'degree_sign')
        obj.inner_center_outer = CellConfig.from_dict(data.get("inner_center_outer", {}), 'inner_center_outer')
        obj.surface = CellConfig.from_dict(data.get("surface", {}), 'surface')
        obj.tyre_compound = CellConfig.from_dict(data.get("tyre_compound", {}), 'tyre_compound')
        obj.enable_heatmap_auto_matching = data.get("enable_heatmap_auto_matching", obj.enable_heatmap_auto_matching)
        obj.heatmap_name = data.get("heatmap_name", obj.heatmap_name)
        obj.leading_zero = data.get("leading_zero", obj.leading_zero)
        obj.swap_style = data.get("swap_style", obj.swap_style)
        return obj
