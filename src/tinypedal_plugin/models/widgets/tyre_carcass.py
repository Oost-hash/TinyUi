# Auto-generated widget
# Widget: tyre_carcass

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import BarConfig, CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..colors import COMPOUND, DARK_INVERT, DEFAULT, LIGHT_BLUE, ORANGE


@dataclass
class TyreCarcass(WidgetConfig):
    name: str = "tyre_carcass"

    # groups
    bar: BarConfig = field(default_factory=BarConfig)
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=57, position_y=670))

    # cells
    carcass: CellConfig = field(default_factory=lambda: CellConfig(id='carcass', font_color=DARK_INVERT.font_color, bkg_color=DARK_INVERT.bkg_color, column_index=1))
    degree_sign: CellConfig = field(default_factory=lambda: CellConfig(id='degree_sign', show=False))
    rate_gain: CellConfig = field(default_factory=lambda: CellConfig(id='rate_gain', font_color=ORANGE.font_color, bkg_color=ORANGE.bkg_color))
    rate_loss: CellConfig = field(default_factory=lambda: CellConfig(id='rate_loss', font_color=LIGHT_BLUE.font_color, bkg_color=LIGHT_BLUE.bkg_color))
    rate_of_change: CellConfig = field(default_factory=lambda: CellConfig(id='rate_of_change', font_color=DARK_INVERT.font_color, bkg_color=DARK_INVERT.bkg_color, column_index=2))
    tyre_compound: CellConfig = field(default_factory=lambda: CellConfig(id='tyre_compound', font_color=COMPOUND.font_color, bkg_color=COMPOUND.bkg_color))

    # config
    enable_heatmap_auto_matching: bool = True
    heatmap_name: str = 'HEATMAP_DEFAULT_TYRE'
    leading_zero: int = 2
    rate_of_change_interval: int = 5
    rate_of_change_smoothing_samples: int = 20
    swap_style: bool = False

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result.update(self.bar.to_flat())
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.carcass.to_flat())
        result.update(self.degree_sign.to_flat())
        result.update(self.rate_gain.to_flat())
        result.update(self.rate_loss.to_flat())
        result.update(self.rate_of_change.to_flat())
        result.update(self.tyre_compound.to_flat())
        result["enable_heatmap_auto_matching"] = self.enable_heatmap_auto_matching
        result["heatmap_name"] = self.heatmap_name
        result["leading_zero"] = self.leading_zero
        result["rate_of_change_interval"] = self.rate_of_change_interval
        result["rate_of_change_smoothing_samples"] = self.rate_of_change_smoothing_samples
        result["swap_style"] = self.swap_style
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "TyreCarcass":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar = BarConfig.from_flat(data)
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.carcass = CellConfig.from_flat(data, 'carcass')
        obj.degree_sign = CellConfig.from_flat(data, 'degree_sign')
        obj.rate_gain = CellConfig.from_flat(data, 'rate_gain')
        obj.rate_loss = CellConfig.from_flat(data, 'rate_loss')
        obj.rate_of_change = CellConfig.from_flat(data, 'rate_of_change')
        obj.tyre_compound = CellConfig.from_flat(data, 'tyre_compound')
        obj.enable_heatmap_auto_matching = data.get("enable_heatmap_auto_matching", obj.enable_heatmap_auto_matching)
        obj.heatmap_name = data.get("heatmap_name", obj.heatmap_name)
        obj.leading_zero = data.get("leading_zero", obj.leading_zero)
        obj.rate_of_change_interval = data.get("rate_of_change_interval", obj.rate_of_change_interval)
        obj.rate_of_change_smoothing_samples = data.get("rate_of_change_smoothing_samples", obj.rate_of_change_smoothing_samples)
        obj.swap_style = data.get("swap_style", obj.swap_style)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["bar"] = self.bar.to_dict()
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["carcass"] = self.carcass.to_dict()
        result["degree_sign"] = self.degree_sign.to_dict()
        result["rate_gain"] = self.rate_gain.to_dict()
        result["rate_loss"] = self.rate_loss.to_dict()
        result["rate_of_change"] = self.rate_of_change.to_dict()
        result["tyre_compound"] = self.tyre_compound.to_dict()
        result["enable_heatmap_auto_matching"] = self.enable_heatmap_auto_matching
        result["heatmap_name"] = self.heatmap_name
        result["leading_zero"] = self.leading_zero
        result["rate_of_change_interval"] = self.rate_of_change_interval
        result["rate_of_change_smoothing_samples"] = self.rate_of_change_smoothing_samples
        result["swap_style"] = self.swap_style
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TyreCarcass":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar = BarConfig.from_dict(data.get("bar", {}))
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.carcass = CellConfig.from_dict(data.get("carcass", {}), 'carcass')
        obj.degree_sign = CellConfig.from_dict(data.get("degree_sign", {}), 'degree_sign')
        obj.rate_gain = CellConfig.from_dict(data.get("rate_gain", {}), 'rate_gain')
        obj.rate_loss = CellConfig.from_dict(data.get("rate_loss", {}), 'rate_loss')
        obj.rate_of_change = CellConfig.from_dict(data.get("rate_of_change", {}), 'rate_of_change')
        obj.tyre_compound = CellConfig.from_dict(data.get("tyre_compound", {}), 'tyre_compound')
        obj.enable_heatmap_auto_matching = data.get("enable_heatmap_auto_matching", obj.enable_heatmap_auto_matching)
        obj.heatmap_name = data.get("heatmap_name", obj.heatmap_name)
        obj.leading_zero = data.get("leading_zero", obj.leading_zero)
        obj.rate_of_change_interval = data.get("rate_of_change_interval", obj.rate_of_change_interval)
        obj.rate_of_change_smoothing_samples = data.get("rate_of_change_smoothing_samples", obj.rate_of_change_smoothing_samples)
        obj.swap_style = data.get("swap_style", obj.swap_style)
        return obj
