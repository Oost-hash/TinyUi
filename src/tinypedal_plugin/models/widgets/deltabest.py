# Auto-generated widget
# Widget: deltabest

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import BarConfig, CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..colors import DARK_INVERT


@dataclass
class Deltabest(WidgetConfig):
    name: str = "deltabest"

    # groups
    bar: BarConfig = field(default_factory=lambda: BarConfig(bar_padding_horizontal=0.5, bar_padding_vertical=0.4))
    font: FontConfig = field(default_factory=lambda: FontConfig(font_size=17))
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=317, position_y=69))

    # cells
    animated_deltabest: CellConfig = field(default_factory=lambda: CellConfig(id='animated_deltabest'))
    delta_bar: CellConfig = field(default_factory=lambda: CellConfig(id='delta_bar'))
    deltabar: CellConfig = field(default_factory=lambda: CellConfig(id='deltabar'))
    deltabest: CellConfig = field(default_factory=lambda: CellConfig(id='deltabest', font_color=DARK_INVERT.font_color, bkg_color=DARK_INVERT.bkg_color))
    time_gain: CellConfig = field(default_factory=lambda: CellConfig(id='time_gain', bkg_color='#44FF00'))
    time_loss: CellConfig = field(default_factory=lambda: CellConfig(id='time_loss', bkg_color='#FF4400'))

    # config
    bar_display_range: int = 2
    bar_height: int = 16
    bar_length: int = 300
    decimal_places: int = 3
    delta_display_range: float = 99.999
    deltabest_source: str = 'Best'
    freeze_duration: int = 3
    swap_style: bool = False

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result.update(self.bar.to_flat())
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.animated_deltabest.to_flat())
        result.update(self.delta_bar.to_flat())
        result.update(self.deltabar.to_flat())
        result.update(self.deltabest.to_flat())
        result.update(self.time_gain.to_flat())
        result.update(self.time_loss.to_flat())
        result["bar_display_range"] = self.bar_display_range
        result["bar_height"] = self.bar_height
        result["bar_length"] = self.bar_length
        result["decimal_places"] = self.decimal_places
        result["delta_display_range"] = self.delta_display_range
        result["deltabest_source"] = self.deltabest_source
        result["freeze_duration"] = self.freeze_duration
        result["swap_style"] = self.swap_style
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "Deltabest":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar = BarConfig.from_flat(data)
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.animated_deltabest = CellConfig.from_flat(data, 'animated_deltabest')
        obj.delta_bar = CellConfig.from_flat(data, 'delta_bar')
        obj.deltabar = CellConfig.from_flat(data, 'deltabar')
        obj.deltabest = CellConfig.from_flat(data, 'deltabest')
        obj.time_gain = CellConfig.from_flat(data, 'time_gain')
        obj.time_loss = CellConfig.from_flat(data, 'time_loss')
        obj.bar_display_range = data.get("bar_display_range", obj.bar_display_range)
        obj.bar_height = data.get("bar_height", obj.bar_height)
        obj.bar_length = data.get("bar_length", obj.bar_length)
        obj.decimal_places = data.get("decimal_places", obj.decimal_places)
        obj.delta_display_range = data.get("delta_display_range", obj.delta_display_range)
        obj.deltabest_source = data.get("deltabest_source", obj.deltabest_source)
        obj.freeze_duration = data.get("freeze_duration", obj.freeze_duration)
        obj.swap_style = data.get("swap_style", obj.swap_style)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["bar"] = self.bar.to_dict()
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["animated_deltabest"] = self.animated_deltabest.to_dict()
        result["delta_bar"] = self.delta_bar.to_dict()
        result["deltabar"] = self.deltabar.to_dict()
        result["deltabest"] = self.deltabest.to_dict()
        result["time_gain"] = self.time_gain.to_dict()
        result["time_loss"] = self.time_loss.to_dict()
        result["bar_display_range"] = self.bar_display_range
        result["bar_height"] = self.bar_height
        result["bar_length"] = self.bar_length
        result["decimal_places"] = self.decimal_places
        result["delta_display_range"] = self.delta_display_range
        result["deltabest_source"] = self.deltabest_source
        result["freeze_duration"] = self.freeze_duration
        result["swap_style"] = self.swap_style
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Deltabest":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar = BarConfig.from_dict(data.get("bar", {}))
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.animated_deltabest = CellConfig.from_dict(data.get("animated_deltabest", {}), 'animated_deltabest')
        obj.delta_bar = CellConfig.from_dict(data.get("delta_bar", {}), 'delta_bar')
        obj.deltabar = CellConfig.from_dict(data.get("deltabar", {}), 'deltabar')
        obj.deltabest = CellConfig.from_dict(data.get("deltabest", {}), 'deltabest')
        obj.time_gain = CellConfig.from_dict(data.get("time_gain", {}), 'time_gain')
        obj.time_loss = CellConfig.from_dict(data.get("time_loss", {}), 'time_loss')
        obj.bar_display_range = data.get("bar_display_range", obj.bar_display_range)
        obj.bar_height = data.get("bar_height", obj.bar_height)
        obj.bar_length = data.get("bar_length", obj.bar_length)
        obj.decimal_places = data.get("decimal_places", obj.decimal_places)
        obj.delta_display_range = data.get("delta_display_range", obj.delta_display_range)
        obj.deltabest_source = data.get("deltabest_source", obj.deltabest_source)
        obj.freeze_duration = data.get("freeze_duration", obj.freeze_duration)
        obj.swap_style = data.get("swap_style", obj.swap_style)
        return obj
