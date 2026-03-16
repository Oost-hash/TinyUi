# Auto-generated widget
# Widget: battery

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..components import WarningFlashConfig


@dataclass
class Battery(WidgetConfig):
    name: str = "battery"

    # groups
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=140, position_y=293))

    # cells
    activation_timer: CellConfig = field(default_factory=lambda: CellConfig(id='activation_timer', column_index=5))
    battery_charge: CellConfig = field(default_factory=lambda: CellConfig(id='battery_charge', bkg_color='#2266CC', column_index=1))
    battery_drain: CellConfig = field(default_factory=lambda: CellConfig(id='battery_drain', column_index=2))
    battery_regen: CellConfig = field(default_factory=lambda: CellConfig(id='battery_regen', column_index=3))
    estimated_net_change: CellConfig = field(default_factory=lambda: CellConfig(id='estimated_net_change', column_index=4))

    # components
    battery_charge_warning_flash: WarningFlashConfig = field(default_factory=WarningFlashConfig)

    # config
    freeze_duration: int = 10
    high_battery_threshold: int = 95
    low_battery_threshold: int = 10
    warning_color_high_battery: str = '#AA22AA'
    warning_color_low_battery: str = '#FF2200'

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.activation_timer.to_flat())
        result.update(self.battery_charge.to_flat())
        result.update(self.battery_drain.to_flat())
        result.update(self.battery_regen.to_flat())
        result.update(self.estimated_net_change.to_flat())
        result["number_of_warning_flashes"] = self.battery_charge_warning_flash.number_of_flashes
        result["show_battery_charge_warning_flash"] = self.battery_charge_warning_flash.enabled
        result["warning_flash_highlight_duration"] = self.battery_charge_warning_flash.highlight_duration
        result["warning_flash_interval"] = self.battery_charge_warning_flash.interval
        result["freeze_duration"] = self.freeze_duration
        result["high_battery_threshold"] = self.high_battery_threshold
        result["low_battery_threshold"] = self.low_battery_threshold
        result["warning_color_high_battery"] = self.warning_color_high_battery
        result["warning_color_low_battery"] = self.warning_color_low_battery
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "Battery":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.activation_timer = CellConfig.from_flat(data, 'activation_timer')
        obj.battery_charge = CellConfig.from_flat(data, 'battery_charge')
        obj.battery_drain = CellConfig.from_flat(data, 'battery_drain')
        obj.battery_regen = CellConfig.from_flat(data, 'battery_regen')
        obj.estimated_net_change = CellConfig.from_flat(data, 'estimated_net_change')
        obj.battery_charge_warning_flash = WarningFlashConfig(
            number_of_flashes=data.get("number_of_warning_flashes", obj.battery_charge_warning_flash.number_of_flashes),
            enabled=data.get("show_battery_charge_warning_flash", obj.battery_charge_warning_flash.enabled),
            highlight_duration=data.get("warning_flash_highlight_duration", obj.battery_charge_warning_flash.highlight_duration),
            interval=data.get("warning_flash_interval", obj.battery_charge_warning_flash.interval),
        )
        obj.freeze_duration = data.get("freeze_duration", obj.freeze_duration)
        obj.high_battery_threshold = data.get("high_battery_threshold", obj.high_battery_threshold)
        obj.low_battery_threshold = data.get("low_battery_threshold", obj.low_battery_threshold)
        obj.warning_color_high_battery = data.get("warning_color_high_battery", obj.warning_color_high_battery)
        obj.warning_color_low_battery = data.get("warning_color_low_battery", obj.warning_color_low_battery)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["activation_timer"] = self.activation_timer.to_dict()
        result["battery_charge"] = self.battery_charge.to_dict()
        result["battery_drain"] = self.battery_drain.to_dict()
        result["battery_regen"] = self.battery_regen.to_dict()
        result["estimated_net_change"] = self.estimated_net_change.to_dict()
        result["battery_charge_warning_flash"] = self.battery_charge_warning_flash.to_dict()
        result["freeze_duration"] = self.freeze_duration
        result["high_battery_threshold"] = self.high_battery_threshold
        result["low_battery_threshold"] = self.low_battery_threshold
        result["warning_color_high_battery"] = self.warning_color_high_battery
        result["warning_color_low_battery"] = self.warning_color_low_battery
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Battery":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.activation_timer = CellConfig.from_dict(data.get("activation_timer", {}), 'activation_timer')
        obj.battery_charge = CellConfig.from_dict(data.get("battery_charge", {}), 'battery_charge')
        obj.battery_drain = CellConfig.from_dict(data.get("battery_drain", {}), 'battery_drain')
        obj.battery_regen = CellConfig.from_dict(data.get("battery_regen", {}), 'battery_regen')
        obj.estimated_net_change = CellConfig.from_dict(data.get("estimated_net_change", {}), 'estimated_net_change')
        obj.battery_charge_warning_flash = WarningFlashConfig.from_dict(data.get("battery_charge_warning_flash", {}))
        obj.freeze_duration = data.get("freeze_duration", obj.freeze_duration)
        obj.high_battery_threshold = data.get("high_battery_threshold", obj.high_battery_threshold)
        obj.low_battery_threshold = data.get("low_battery_threshold", obj.low_battery_threshold)
        obj.warning_color_high_battery = data.get("warning_color_high_battery", obj.warning_color_high_battery)
        obj.warning_color_low_battery = data.get("warning_color_low_battery", obj.warning_color_low_battery)
        return obj
