# Auto-generated widget
# Widget: rpm_led

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import BarConfig, CellConfig, PositionConfig, WidgetConfig


@dataclass
class RpmLed(WidgetConfig):
    name: str = "rpm_led"

    # base overrides
    bkg_color: str = '#88000000'

    # groups
    bar: BarConfig = field(default_factory=lambda: BarConfig(inner_gap=3))
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=766, position_y=804))

    # cells
    background: CellConfig = field(default_factory=lambda: CellConfig(id='background', show=False))
    rpm_flickering_above_critical: CellConfig = field(default_factory=lambda: CellConfig(id='rpm_flickering_above_critical'))
    speed_limiter_flash: CellConfig = field(default_factory=lambda: CellConfig(id='speed_limiter_flash'))

    # config
    display_margin: int = 4
    enable_double_side_led: bool = False
    led_height: int = 20
    led_outline_color: str = '#88888888'
    led_outline_width: int = 2
    led_radius: int = 2
    led_width: int = 40
    number_of_led: int = 10
    rpm_color_critical: str = '#00FFFF'
    rpm_color_low: str = '#00FF00'
    rpm_color_off: str = '#111111'
    rpm_color_over_rev: str = '#FF00FF'
    rpm_color_redline: str = '#FF0000'
    rpm_color_safe: str = '#FFFF00'
    rpm_multiplier_critical: float = 0.96
    rpm_multiplier_low: float = 0.84
    rpm_multiplier_over_rev: float = 0.9999
    rpm_multiplier_redline: float = 0.92
    rpm_multiplier_safe: float = 0.88
    speed_limiter_flash_color: str = '#00FF00'
    speed_limiter_flash_interval: float = 0.25

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result["bkg_color"] = self.bkg_color
        result.update(self.bar.to_flat())
        result.update(self.position.to_flat())
        result.update(self.background.to_flat())
        result.update(self.rpm_flickering_above_critical.to_flat())
        result.update(self.speed_limiter_flash.to_flat())
        result["display_margin"] = self.display_margin
        result["enable_double_side_led"] = self.enable_double_side_led
        result["led_height"] = self.led_height
        result["led_outline_color"] = self.led_outline_color
        result["led_outline_width"] = self.led_outline_width
        result["led_radius"] = self.led_radius
        result["led_width"] = self.led_width
        result["number_of_led"] = self.number_of_led
        result["rpm_color_critical"] = self.rpm_color_critical
        result["rpm_color_low"] = self.rpm_color_low
        result["rpm_color_off"] = self.rpm_color_off
        result["rpm_color_over_rev"] = self.rpm_color_over_rev
        result["rpm_color_redline"] = self.rpm_color_redline
        result["rpm_color_safe"] = self.rpm_color_safe
        result["rpm_multiplier_critical"] = self.rpm_multiplier_critical
        result["rpm_multiplier_low"] = self.rpm_multiplier_low
        result["rpm_multiplier_over_rev"] = self.rpm_multiplier_over_rev
        result["rpm_multiplier_redline"] = self.rpm_multiplier_redline
        result["rpm_multiplier_safe"] = self.rpm_multiplier_safe
        result["speed_limiter_flash_color"] = self.speed_limiter_flash_color
        result["speed_limiter_flash_interval"] = self.speed_limiter_flash_interval
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "RpmLed":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bkg_color = data.get("bkg_color", obj.bkg_color)
        obj.bar = BarConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.background = CellConfig.from_flat(data, 'background')
        obj.rpm_flickering_above_critical = CellConfig.from_flat(data, 'rpm_flickering_above_critical')
        obj.speed_limiter_flash = CellConfig.from_flat(data, 'speed_limiter_flash')
        obj.display_margin = data.get("display_margin", obj.display_margin)
        obj.enable_double_side_led = data.get("enable_double_side_led", obj.enable_double_side_led)
        obj.led_height = data.get("led_height", obj.led_height)
        obj.led_outline_color = data.get("led_outline_color", obj.led_outline_color)
        obj.led_outline_width = data.get("led_outline_width", obj.led_outline_width)
        obj.led_radius = data.get("led_radius", obj.led_radius)
        obj.led_width = data.get("led_width", obj.led_width)
        obj.number_of_led = data.get("number_of_led", obj.number_of_led)
        obj.rpm_color_critical = data.get("rpm_color_critical", obj.rpm_color_critical)
        obj.rpm_color_low = data.get("rpm_color_low", obj.rpm_color_low)
        obj.rpm_color_off = data.get("rpm_color_off", obj.rpm_color_off)
        obj.rpm_color_over_rev = data.get("rpm_color_over_rev", obj.rpm_color_over_rev)
        obj.rpm_color_redline = data.get("rpm_color_redline", obj.rpm_color_redline)
        obj.rpm_color_safe = data.get("rpm_color_safe", obj.rpm_color_safe)
        obj.rpm_multiplier_critical = data.get("rpm_multiplier_critical", obj.rpm_multiplier_critical)
        obj.rpm_multiplier_low = data.get("rpm_multiplier_low", obj.rpm_multiplier_low)
        obj.rpm_multiplier_over_rev = data.get("rpm_multiplier_over_rev", obj.rpm_multiplier_over_rev)
        obj.rpm_multiplier_redline = data.get("rpm_multiplier_redline", obj.rpm_multiplier_redline)
        obj.rpm_multiplier_safe = data.get("rpm_multiplier_safe", obj.rpm_multiplier_safe)
        obj.speed_limiter_flash_color = data.get("speed_limiter_flash_color", obj.speed_limiter_flash_color)
        obj.speed_limiter_flash_interval = data.get("speed_limiter_flash_interval", obj.speed_limiter_flash_interval)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["bkg_color"] = self.bkg_color
        result["bar"] = self.bar.to_dict()
        result["position"] = self.position.to_dict()
        result["background"] = self.background.to_dict()
        result["rpm_flickering_above_critical"] = self.rpm_flickering_above_critical.to_dict()
        result["speed_limiter_flash"] = self.speed_limiter_flash.to_dict()
        result["display_margin"] = self.display_margin
        result["enable_double_side_led"] = self.enable_double_side_led
        result["led_height"] = self.led_height
        result["led_outline_color"] = self.led_outline_color
        result["led_outline_width"] = self.led_outline_width
        result["led_radius"] = self.led_radius
        result["led_width"] = self.led_width
        result["number_of_led"] = self.number_of_led
        result["rpm_color_critical"] = self.rpm_color_critical
        result["rpm_color_low"] = self.rpm_color_low
        result["rpm_color_off"] = self.rpm_color_off
        result["rpm_color_over_rev"] = self.rpm_color_over_rev
        result["rpm_color_redline"] = self.rpm_color_redline
        result["rpm_color_safe"] = self.rpm_color_safe
        result["rpm_multiplier_critical"] = self.rpm_multiplier_critical
        result["rpm_multiplier_low"] = self.rpm_multiplier_low
        result["rpm_multiplier_over_rev"] = self.rpm_multiplier_over_rev
        result["rpm_multiplier_redline"] = self.rpm_multiplier_redline
        result["rpm_multiplier_safe"] = self.rpm_multiplier_safe
        result["speed_limiter_flash_color"] = self.speed_limiter_flash_color
        result["speed_limiter_flash_interval"] = self.speed_limiter_flash_interval
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RpmLed":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bkg_color = data.get("bkg_color", obj.bkg_color)
        obj.bar = BarConfig.from_dict(data.get("bar", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.background = CellConfig.from_dict(data.get("background", {}), 'background')
        obj.rpm_flickering_above_critical = CellConfig.from_dict(data.get("rpm_flickering_above_critical", {}), 'rpm_flickering_above_critical')
        obj.speed_limiter_flash = CellConfig.from_dict(data.get("speed_limiter_flash", {}), 'speed_limiter_flash')
        obj.display_margin = data.get("display_margin", obj.display_margin)
        obj.enable_double_side_led = data.get("enable_double_side_led", obj.enable_double_side_led)
        obj.led_height = data.get("led_height", obj.led_height)
        obj.led_outline_color = data.get("led_outline_color", obj.led_outline_color)
        obj.led_outline_width = data.get("led_outline_width", obj.led_outline_width)
        obj.led_radius = data.get("led_radius", obj.led_radius)
        obj.led_width = data.get("led_width", obj.led_width)
        obj.number_of_led = data.get("number_of_led", obj.number_of_led)
        obj.rpm_color_critical = data.get("rpm_color_critical", obj.rpm_color_critical)
        obj.rpm_color_low = data.get("rpm_color_low", obj.rpm_color_low)
        obj.rpm_color_off = data.get("rpm_color_off", obj.rpm_color_off)
        obj.rpm_color_over_rev = data.get("rpm_color_over_rev", obj.rpm_color_over_rev)
        obj.rpm_color_redline = data.get("rpm_color_redline", obj.rpm_color_redline)
        obj.rpm_color_safe = data.get("rpm_color_safe", obj.rpm_color_safe)
        obj.rpm_multiplier_critical = data.get("rpm_multiplier_critical", obj.rpm_multiplier_critical)
        obj.rpm_multiplier_low = data.get("rpm_multiplier_low", obj.rpm_multiplier_low)
        obj.rpm_multiplier_over_rev = data.get("rpm_multiplier_over_rev", obj.rpm_multiplier_over_rev)
        obj.rpm_multiplier_redline = data.get("rpm_multiplier_redline", obj.rpm_multiplier_redline)
        obj.rpm_multiplier_safe = data.get("rpm_multiplier_safe", obj.rpm_multiplier_safe)
        obj.speed_limiter_flash_color = data.get("speed_limiter_flash_color", obj.speed_limiter_flash_color)
        obj.speed_limiter_flash_interval = data.get("speed_limiter_flash_interval", obj.speed_limiter_flash_interval)
        return obj
