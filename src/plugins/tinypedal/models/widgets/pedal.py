# Auto-generated widget
# Widget: pedal

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import BarConfig, CellConfig, FontConfig, PositionConfig, WidgetConfig


@dataclass
class Pedal(WidgetConfig):
    name: str = "pedal"

    # groups
    bar: BarConfig = field(default_factory=lambda: BarConfig(inner_gap=2))
    font: FontConfig = field(default_factory=lambda: FontConfig(font_size=13))
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=374, position_y=401))

    # cells
    brake: CellConfig = field(default_factory=lambda: CellConfig(id='brake', column_index=3))
    brake_filtered: CellConfig = field(default_factory=lambda: CellConfig(id='brake_filtered'))
    brake_pressure: CellConfig = field(default_factory=lambda: CellConfig(id='brake_pressure'))
    clutch: CellConfig = field(default_factory=lambda: CellConfig(id='clutch', column_index=2))
    clutch_filtered: CellConfig = field(default_factory=lambda: CellConfig(id='clutch_filtered'))
    ffb: CellConfig = field(default_factory=lambda: CellConfig(id='ffb', column_index=1))
    ffb_meter: CellConfig = field(default_factory=lambda: CellConfig(id='ffb_meter'))
    readings: CellConfig = field(default_factory=lambda: CellConfig(id='readings', show=False))
    throttle: CellConfig = field(default_factory=lambda: CellConfig(id='throttle', column_index=4))
    throttle_filtered: CellConfig = field(default_factory=lambda: CellConfig(id='throttle_filtered'))

    # config
    bar_length: int = 100
    bar_width_filtered: int = 10
    bar_width_unfiltered: int = 5
    brake_color: str = '#FF2200'
    clutch_color: str = '#00C2F2'
    enable_horizontal_style: bool = False
    ffb_clipping_color: str = '#FFAA00'
    ffb_color: str = '#888888'
    max_indicator_height: int = 5
    readings_offset: float = 0.5
    throttle_color: str = '#77FF00'

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result.update(self.bar.to_flat())
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.brake.to_flat())
        result.update(self.brake_filtered.to_flat())
        result.update(self.brake_pressure.to_flat())
        result.update(self.clutch.to_flat())
        result.update(self.clutch_filtered.to_flat())
        result.update(self.ffb.to_flat())
        result.update(self.ffb_meter.to_flat())
        result.update(self.readings.to_flat())
        result.update(self.throttle.to_flat())
        result.update(self.throttle_filtered.to_flat())
        result["bar_length"] = self.bar_length
        result["bar_width_filtered"] = self.bar_width_filtered
        result["bar_width_unfiltered"] = self.bar_width_unfiltered
        result["brake_color"] = self.brake_color
        result["clutch_color"] = self.clutch_color
        result["enable_horizontal_style"] = self.enable_horizontal_style
        result["ffb_clipping_color"] = self.ffb_clipping_color
        result["ffb_color"] = self.ffb_color
        result["max_indicator_height"] = self.max_indicator_height
        result["readings_offset"] = self.readings_offset
        result["throttle_color"] = self.throttle_color
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "Pedal":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar = BarConfig.from_flat(data)
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.brake = CellConfig.from_flat(data, 'brake')
        obj.brake_filtered = CellConfig.from_flat(data, 'brake_filtered')
        obj.brake_pressure = CellConfig.from_flat(data, 'brake_pressure')
        obj.clutch = CellConfig.from_flat(data, 'clutch')
        obj.clutch_filtered = CellConfig.from_flat(data, 'clutch_filtered')
        obj.ffb = CellConfig.from_flat(data, 'ffb')
        obj.ffb_meter = CellConfig.from_flat(data, 'ffb_meter')
        obj.readings = CellConfig.from_flat(data, 'readings')
        obj.throttle = CellConfig.from_flat(data, 'throttle')
        obj.throttle_filtered = CellConfig.from_flat(data, 'throttle_filtered')
        obj.bar_length = data.get("bar_length", obj.bar_length)
        obj.bar_width_filtered = data.get("bar_width_filtered", obj.bar_width_filtered)
        obj.bar_width_unfiltered = data.get("bar_width_unfiltered", obj.bar_width_unfiltered)
        obj.brake_color = data.get("brake_color", obj.brake_color)
        obj.clutch_color = data.get("clutch_color", obj.clutch_color)
        obj.enable_horizontal_style = data.get("enable_horizontal_style", obj.enable_horizontal_style)
        obj.ffb_clipping_color = data.get("ffb_clipping_color", obj.ffb_clipping_color)
        obj.ffb_color = data.get("ffb_color", obj.ffb_color)
        obj.max_indicator_height = data.get("max_indicator_height", obj.max_indicator_height)
        obj.readings_offset = data.get("readings_offset", obj.readings_offset)
        obj.throttle_color = data.get("throttle_color", obj.throttle_color)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["bar"] = self.bar.to_dict()
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["brake"] = self.brake.to_dict()
        result["brake_filtered"] = self.brake_filtered.to_dict()
        result["brake_pressure"] = self.brake_pressure.to_dict()
        result["clutch"] = self.clutch.to_dict()
        result["clutch_filtered"] = self.clutch_filtered.to_dict()
        result["ffb"] = self.ffb.to_dict()
        result["ffb_meter"] = self.ffb_meter.to_dict()
        result["readings"] = self.readings.to_dict()
        result["throttle"] = self.throttle.to_dict()
        result["throttle_filtered"] = self.throttle_filtered.to_dict()
        result["bar_length"] = self.bar_length
        result["bar_width_filtered"] = self.bar_width_filtered
        result["bar_width_unfiltered"] = self.bar_width_unfiltered
        result["brake_color"] = self.brake_color
        result["clutch_color"] = self.clutch_color
        result["enable_horizontal_style"] = self.enable_horizontal_style
        result["ffb_clipping_color"] = self.ffb_clipping_color
        result["ffb_color"] = self.ffb_color
        result["max_indicator_height"] = self.max_indicator_height
        result["readings_offset"] = self.readings_offset
        result["throttle_color"] = self.throttle_color
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Pedal":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar = BarConfig.from_dict(data.get("bar", {}))
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.brake = CellConfig.from_dict(data.get("brake", {}), 'brake')
        obj.brake_filtered = CellConfig.from_dict(data.get("brake_filtered", {}), 'brake_filtered')
        obj.brake_pressure = CellConfig.from_dict(data.get("brake_pressure", {}), 'brake_pressure')
        obj.clutch = CellConfig.from_dict(data.get("clutch", {}), 'clutch')
        obj.clutch_filtered = CellConfig.from_dict(data.get("clutch_filtered", {}), 'clutch_filtered')
        obj.ffb = CellConfig.from_dict(data.get("ffb", {}), 'ffb')
        obj.ffb_meter = CellConfig.from_dict(data.get("ffb_meter", {}), 'ffb_meter')
        obj.readings = CellConfig.from_dict(data.get("readings", {}), 'readings')
        obj.throttle = CellConfig.from_dict(data.get("throttle", {}), 'throttle')
        obj.throttle_filtered = CellConfig.from_dict(data.get("throttle_filtered", {}), 'throttle_filtered')
        obj.bar_length = data.get("bar_length", obj.bar_length)
        obj.bar_width_filtered = data.get("bar_width_filtered", obj.bar_width_filtered)
        obj.bar_width_unfiltered = data.get("bar_width_unfiltered", obj.bar_width_unfiltered)
        obj.brake_color = data.get("brake_color", obj.brake_color)
        obj.clutch_color = data.get("clutch_color", obj.clutch_color)
        obj.enable_horizontal_style = data.get("enable_horizontal_style", obj.enable_horizontal_style)
        obj.ffb_clipping_color = data.get("ffb_clipping_color", obj.ffb_clipping_color)
        obj.ffb_color = data.get("ffb_color", obj.ffb_color)
        obj.max_indicator_height = data.get("max_indicator_height", obj.max_indicator_height)
        obj.readings_offset = data.get("readings_offset", obj.readings_offset)
        obj.throttle_color = data.get("throttle_color", obj.throttle_color)
        return obj
