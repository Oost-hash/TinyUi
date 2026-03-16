# Auto-generated widget
# Widget: push_to_pass

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..colors import HISTORY_PRIMARY, READING


@dataclass
class PushToPass(WidgetConfig):
    name: str = "push_to_pass"

    # base overrides
    bar_gap: int = 0
    bar_padding: float = 0.3
    layout: int = 1

    # groups
    font: FontConfig = field(default_factory=lambda: FontConfig(font_size=30))
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=556, position_y=457))

    # cells
    activation_cooldown: CellConfig = field(default_factory=lambda: CellConfig(id='activation_cooldown', font_color='#999999', bkg_color='#EEEEEE'))
    activation_timer: CellConfig = field(default_factory=lambda: CellConfig(id='activation_timer', font_color=HISTORY_PRIMARY.font_color, bkg_color=HISTORY_PRIMARY.bkg_color, column_index=2))
    battery_charge: CellConfig = field(default_factory=lambda: CellConfig(id='battery_charge', bkg_color='#0055ff', column_index=1))
    battery_cooldown: CellConfig = field(default_factory=lambda: CellConfig(id='battery_cooldown', font_color=READING.font_color, bkg_color=READING.bkg_color))
    battery_drain: CellConfig = field(default_factory=lambda: CellConfig(id='battery_drain', bkg_color='#FF6600'))
    battery_regen: CellConfig = field(default_factory=lambda: CellConfig(id='battery_regen', bkg_color='#22AA00'))

    # config
    activation_threshold_gear: int = 3
    activation_threshold_speed: int = 120
    activation_threshold_throttle: float = 0.6
    maximum_activation_time_per_lap: int = 15
    minimum_activation_time_delay: int = 5

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result["bar_gap"] = self.bar_gap
        result["bar_padding"] = self.bar_padding
        result["layout"] = self.layout
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.activation_cooldown.to_flat())
        result.update(self.activation_timer.to_flat())
        result.update(self.battery_charge.to_flat())
        result.update(self.battery_cooldown.to_flat())
        result.update(self.battery_drain.to_flat())
        result.update(self.battery_regen.to_flat())
        result["activation_threshold_gear"] = self.activation_threshold_gear
        result["activation_threshold_speed"] = self.activation_threshold_speed
        result["activation_threshold_throttle"] = self.activation_threshold_throttle
        result["maximum_activation_time_per_lap"] = self.maximum_activation_time_per_lap
        result["minimum_activation_time_delay"] = self.minimum_activation_time_delay
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "PushToPass":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar_gap = data.get("bar_gap", obj.bar_gap)
        obj.bar_padding = data.get("bar_padding", obj.bar_padding)
        obj.layout = data.get("layout", obj.layout)
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.activation_cooldown = CellConfig.from_flat(data, 'activation_cooldown')
        obj.activation_timer = CellConfig.from_flat(data, 'activation_timer')
        obj.battery_charge = CellConfig.from_flat(data, 'battery_charge')
        obj.battery_cooldown = CellConfig.from_flat(data, 'battery_cooldown')
        obj.battery_drain = CellConfig.from_flat(data, 'battery_drain')
        obj.battery_regen = CellConfig.from_flat(data, 'battery_regen')
        obj.activation_threshold_gear = data.get("activation_threshold_gear", obj.activation_threshold_gear)
        obj.activation_threshold_speed = data.get("activation_threshold_speed", obj.activation_threshold_speed)
        obj.activation_threshold_throttle = data.get("activation_threshold_throttle", obj.activation_threshold_throttle)
        obj.maximum_activation_time_per_lap = data.get("maximum_activation_time_per_lap", obj.maximum_activation_time_per_lap)
        obj.minimum_activation_time_delay = data.get("minimum_activation_time_delay", obj.minimum_activation_time_delay)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["bar_gap"] = self.bar_gap
        result["bar_padding"] = self.bar_padding
        result["layout"] = self.layout
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["activation_cooldown"] = self.activation_cooldown.to_dict()
        result["activation_timer"] = self.activation_timer.to_dict()
        result["battery_charge"] = self.battery_charge.to_dict()
        result["battery_cooldown"] = self.battery_cooldown.to_dict()
        result["battery_drain"] = self.battery_drain.to_dict()
        result["battery_regen"] = self.battery_regen.to_dict()
        result["activation_threshold_gear"] = self.activation_threshold_gear
        result["activation_threshold_speed"] = self.activation_threshold_speed
        result["activation_threshold_throttle"] = self.activation_threshold_throttle
        result["maximum_activation_time_per_lap"] = self.maximum_activation_time_per_lap
        result["minimum_activation_time_delay"] = self.minimum_activation_time_delay
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PushToPass":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar_gap = data.get("bar_gap", obj.bar_gap)
        obj.bar_padding = data.get("bar_padding", obj.bar_padding)
        obj.layout = data.get("layout", obj.layout)
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.activation_cooldown = CellConfig.from_dict(data.get("activation_cooldown", {}), 'activation_cooldown')
        obj.activation_timer = CellConfig.from_dict(data.get("activation_timer", {}), 'activation_timer')
        obj.battery_charge = CellConfig.from_dict(data.get("battery_charge", {}), 'battery_charge')
        obj.battery_cooldown = CellConfig.from_dict(data.get("battery_cooldown", {}), 'battery_cooldown')
        obj.battery_drain = CellConfig.from_dict(data.get("battery_drain", {}), 'battery_drain')
        obj.battery_regen = CellConfig.from_dict(data.get("battery_regen", {}), 'battery_regen')
        obj.activation_threshold_gear = data.get("activation_threshold_gear", obj.activation_threshold_gear)
        obj.activation_threshold_speed = data.get("activation_threshold_speed", obj.activation_threshold_speed)
        obj.activation_threshold_throttle = data.get("activation_threshold_throttle", obj.activation_threshold_throttle)
        obj.maximum_activation_time_per_lap = data.get("maximum_activation_time_per_lap", obj.maximum_activation_time_per_lap)
        obj.minimum_activation_time_delay = data.get("minimum_activation_time_delay", obj.minimum_activation_time_delay)
        return obj
