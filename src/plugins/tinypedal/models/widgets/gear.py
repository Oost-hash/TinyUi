# Auto-generated widget
# Widget: gear

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import BarConfig, CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..colors import DISABLED


@dataclass
class Gear(WidgetConfig):
    name: str = "gear"

    # base overrides
    bar_gap: int = 0

    # groups
    bar: BarConfig = field(default_factory=lambda: BarConfig(bar_padding_horizontal=0.5, bar_padding_vertical=0.2))
    font: FontConfig = field(default_factory=lambda: FontConfig(font_size=44))
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=306, position_y=293))

    # cells
    battery: CellConfig = field(default_factory=lambda: CellConfig(id='battery', column_index=2))
    battery_bar: CellConfig = field(default_factory=lambda: CellConfig(id='battery_bar'))
    battery_reading: CellConfig = field(default_factory=lambda: CellConfig(id='battery_reading', show=False))
    gauge: CellConfig = field(default_factory=lambda: CellConfig(id='gauge', column_index=1))
    inverted_battery: CellConfig = field(default_factory=lambda: CellConfig(id='inverted_battery', show=False))
    inverted_rpm: CellConfig = field(default_factory=lambda: CellConfig(id='inverted_rpm', show=False))
    rpm: CellConfig = field(default_factory=lambda: CellConfig(id='rpm', font_color=DISABLED.font_color, bkg_color=DISABLED.bkg_color, column_index=3))
    rpm_bar: CellConfig = field(default_factory=lambda: CellConfig(id='rpm_bar'))
    rpm_flickering_above_critical: CellConfig = field(default_factory=lambda: CellConfig(id='rpm_flickering_above_critical'))
    rpm_reading: CellConfig = field(default_factory=lambda: CellConfig(id='rpm_reading', show=False))
    speed: CellConfig = field(default_factory=lambda: CellConfig(id='speed'))
    speed_below_gear: CellConfig = field(default_factory=lambda: CellConfig(id='speed_below_gear', show=False))
    speed_limiter: CellConfig = field(default_factory=lambda: CellConfig(id='speed_limiter', font_color='#111111', bkg_color='#FF2200'))

    # config
    battery_bar_bkg_color: str = '#88222222'
    battery_bar_color: str = '#00CCFF'
    battery_bar_color_regen: str = '#44FF00'
    battery_bar_height: int = 4
    battery_decimal_places: int = 1
    battery_reading_offset_x: float = 0.5
    battery_reading_text_alignment: str = 'Center'
    font_color: str = '#FFFFFF'
    font_scale_speed: float = 0.5
    font_size_battery: int = 16
    font_size_rpm: int = 20
    font_weight_battery: str = 'Bold'
    font_weight_gear: str = 'Bold'
    font_weight_rpm: str = 'Bold'
    font_weight_speed: str = 'Normal'
    high_battery_threshold: int = 95
    low_battery_threshold: int = 10
    neutral_warning_speed_threshold: int = 28
    neutral_warning_time_threshold: float = 0.3
    rpm_bar_bkg_color: str = '#00222222'
    rpm_bar_color: str = '#FFFFFF'
    rpm_bar_height: int = 14
    rpm_color_over_rev: str = '#FF00FF'
    rpm_color_redline: str = '#00FFFF'
    rpm_color_safe: str = '#FF2200'
    rpm_decimal_places: int = 0
    rpm_multiplier_critical: float = 0.97
    rpm_multiplier_redline: float = 0.95
    rpm_multiplier_safe: float = 0.91
    rpm_reading_offset_x: float = 0.5
    rpm_reading_text_alignment: str = 'Center'
    speed_limiter_padding_horizontal: float = 0.3
    speed_limiter_text: str = 'LIMIT'
    warning_color_high_battery: str = '#FF44FF'
    warning_color_low_battery: str = '#FF2200'

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result["bar_gap"] = self.bar_gap
        result.update(self.bar.to_flat())
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.battery.to_flat())
        result.update(self.battery_bar.to_flat())
        result.update(self.battery_reading.to_flat())
        result.update(self.gauge.to_flat())
        result.update(self.inverted_battery.to_flat())
        result.update(self.inverted_rpm.to_flat())
        result.update(self.rpm.to_flat())
        result.update(self.rpm_bar.to_flat())
        result.update(self.rpm_flickering_above_critical.to_flat())
        result.update(self.rpm_reading.to_flat())
        result.update(self.speed.to_flat())
        result.update(self.speed_below_gear.to_flat())
        result.update(self.speed_limiter.to_flat())
        result["battery_bar_bkg_color"] = self.battery_bar_bkg_color
        result["battery_bar_color"] = self.battery_bar_color
        result["battery_bar_color_regen"] = self.battery_bar_color_regen
        result["battery_bar_height"] = self.battery_bar_height
        result["battery_decimal_places"] = self.battery_decimal_places
        result["battery_reading_offset_x"] = self.battery_reading_offset_x
        result["battery_reading_text_alignment"] = self.battery_reading_text_alignment
        result["font_color"] = self.font_color
        result["font_scale_speed"] = self.font_scale_speed
        result["font_size_battery"] = self.font_size_battery
        result["font_size_rpm"] = self.font_size_rpm
        result["font_weight_battery"] = self.font_weight_battery
        result["font_weight_gear"] = self.font_weight_gear
        result["font_weight_rpm"] = self.font_weight_rpm
        result["font_weight_speed"] = self.font_weight_speed
        result["high_battery_threshold"] = self.high_battery_threshold
        result["low_battery_threshold"] = self.low_battery_threshold
        result["neutral_warning_speed_threshold"] = self.neutral_warning_speed_threshold
        result["neutral_warning_time_threshold"] = self.neutral_warning_time_threshold
        result["rpm_bar_bkg_color"] = self.rpm_bar_bkg_color
        result["rpm_bar_color"] = self.rpm_bar_color
        result["rpm_bar_height"] = self.rpm_bar_height
        result["rpm_color_over_rev"] = self.rpm_color_over_rev
        result["rpm_color_redline"] = self.rpm_color_redline
        result["rpm_color_safe"] = self.rpm_color_safe
        result["rpm_decimal_places"] = self.rpm_decimal_places
        result["rpm_multiplier_critical"] = self.rpm_multiplier_critical
        result["rpm_multiplier_redline"] = self.rpm_multiplier_redline
        result["rpm_multiplier_safe"] = self.rpm_multiplier_safe
        result["rpm_reading_offset_x"] = self.rpm_reading_offset_x
        result["rpm_reading_text_alignment"] = self.rpm_reading_text_alignment
        result["speed_limiter_padding_horizontal"] = self.speed_limiter_padding_horizontal
        result["speed_limiter_text"] = self.speed_limiter_text
        result["warning_color_high_battery"] = self.warning_color_high_battery
        result["warning_color_low_battery"] = self.warning_color_low_battery
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "Gear":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar_gap = data.get("bar_gap", obj.bar_gap)
        obj.bar = BarConfig.from_flat(data)
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.battery = CellConfig.from_flat(data, 'battery')
        obj.battery_bar = CellConfig.from_flat(data, 'battery_bar')
        obj.battery_reading = CellConfig.from_flat(data, 'battery_reading')
        obj.gauge = CellConfig.from_flat(data, 'gauge')
        obj.inverted_battery = CellConfig.from_flat(data, 'inverted_battery')
        obj.inverted_rpm = CellConfig.from_flat(data, 'inverted_rpm')
        obj.rpm = CellConfig.from_flat(data, 'rpm')
        obj.rpm_bar = CellConfig.from_flat(data, 'rpm_bar')
        obj.rpm_flickering_above_critical = CellConfig.from_flat(data, 'rpm_flickering_above_critical')
        obj.rpm_reading = CellConfig.from_flat(data, 'rpm_reading')
        obj.speed = CellConfig.from_flat(data, 'speed')
        obj.speed_below_gear = CellConfig.from_flat(data, 'speed_below_gear')
        obj.speed_limiter = CellConfig.from_flat(data, 'speed_limiter')
        obj.battery_bar_bkg_color = data.get("battery_bar_bkg_color", obj.battery_bar_bkg_color)
        obj.battery_bar_color = data.get("battery_bar_color", obj.battery_bar_color)
        obj.battery_bar_color_regen = data.get("battery_bar_color_regen", obj.battery_bar_color_regen)
        obj.battery_bar_height = data.get("battery_bar_height", obj.battery_bar_height)
        obj.battery_decimal_places = data.get("battery_decimal_places", obj.battery_decimal_places)
        obj.battery_reading_offset_x = data.get("battery_reading_offset_x", obj.battery_reading_offset_x)
        obj.battery_reading_text_alignment = data.get("battery_reading_text_alignment", obj.battery_reading_text_alignment)
        obj.font_color = data.get("font_color", obj.font_color)
        obj.font_scale_speed = data.get("font_scale_speed", obj.font_scale_speed)
        obj.font_size_battery = data.get("font_size_battery", obj.font_size_battery)
        obj.font_size_rpm = data.get("font_size_rpm", obj.font_size_rpm)
        obj.font_weight_battery = data.get("font_weight_battery", obj.font_weight_battery)
        obj.font_weight_gear = data.get("font_weight_gear", obj.font_weight_gear)
        obj.font_weight_rpm = data.get("font_weight_rpm", obj.font_weight_rpm)
        obj.font_weight_speed = data.get("font_weight_speed", obj.font_weight_speed)
        obj.high_battery_threshold = data.get("high_battery_threshold", obj.high_battery_threshold)
        obj.low_battery_threshold = data.get("low_battery_threshold", obj.low_battery_threshold)
        obj.neutral_warning_speed_threshold = data.get("neutral_warning_speed_threshold", obj.neutral_warning_speed_threshold)
        obj.neutral_warning_time_threshold = data.get("neutral_warning_time_threshold", obj.neutral_warning_time_threshold)
        obj.rpm_bar_bkg_color = data.get("rpm_bar_bkg_color", obj.rpm_bar_bkg_color)
        obj.rpm_bar_color = data.get("rpm_bar_color", obj.rpm_bar_color)
        obj.rpm_bar_height = data.get("rpm_bar_height", obj.rpm_bar_height)
        obj.rpm_color_over_rev = data.get("rpm_color_over_rev", obj.rpm_color_over_rev)
        obj.rpm_color_redline = data.get("rpm_color_redline", obj.rpm_color_redline)
        obj.rpm_color_safe = data.get("rpm_color_safe", obj.rpm_color_safe)
        obj.rpm_decimal_places = data.get("rpm_decimal_places", obj.rpm_decimal_places)
        obj.rpm_multiplier_critical = data.get("rpm_multiplier_critical", obj.rpm_multiplier_critical)
        obj.rpm_multiplier_redline = data.get("rpm_multiplier_redline", obj.rpm_multiplier_redline)
        obj.rpm_multiplier_safe = data.get("rpm_multiplier_safe", obj.rpm_multiplier_safe)
        obj.rpm_reading_offset_x = data.get("rpm_reading_offset_x", obj.rpm_reading_offset_x)
        obj.rpm_reading_text_alignment = data.get("rpm_reading_text_alignment", obj.rpm_reading_text_alignment)
        obj.speed_limiter_padding_horizontal = data.get("speed_limiter_padding_horizontal", obj.speed_limiter_padding_horizontal)
        obj.speed_limiter_text = data.get("speed_limiter_text", obj.speed_limiter_text)
        obj.warning_color_high_battery = data.get("warning_color_high_battery", obj.warning_color_high_battery)
        obj.warning_color_low_battery = data.get("warning_color_low_battery", obj.warning_color_low_battery)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["bar_gap"] = self.bar_gap
        result["bar"] = self.bar.to_dict()
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["battery"] = self.battery.to_dict()
        result["battery_bar"] = self.battery_bar.to_dict()
        result["battery_reading"] = self.battery_reading.to_dict()
        result["gauge"] = self.gauge.to_dict()
        result["inverted_battery"] = self.inverted_battery.to_dict()
        result["inverted_rpm"] = self.inverted_rpm.to_dict()
        result["rpm"] = self.rpm.to_dict()
        result["rpm_bar"] = self.rpm_bar.to_dict()
        result["rpm_flickering_above_critical"] = self.rpm_flickering_above_critical.to_dict()
        result["rpm_reading"] = self.rpm_reading.to_dict()
        result["speed"] = self.speed.to_dict()
        result["speed_below_gear"] = self.speed_below_gear.to_dict()
        result["speed_limiter"] = self.speed_limiter.to_dict()
        result["battery_bar_bkg_color"] = self.battery_bar_bkg_color
        result["battery_bar_color"] = self.battery_bar_color
        result["battery_bar_color_regen"] = self.battery_bar_color_regen
        result["battery_bar_height"] = self.battery_bar_height
        result["battery_decimal_places"] = self.battery_decimal_places
        result["battery_reading_offset_x"] = self.battery_reading_offset_x
        result["battery_reading_text_alignment"] = self.battery_reading_text_alignment
        result["font_color"] = self.font_color
        result["font_scale_speed"] = self.font_scale_speed
        result["font_size_battery"] = self.font_size_battery
        result["font_size_rpm"] = self.font_size_rpm
        result["font_weight_battery"] = self.font_weight_battery
        result["font_weight_gear"] = self.font_weight_gear
        result["font_weight_rpm"] = self.font_weight_rpm
        result["font_weight_speed"] = self.font_weight_speed
        result["high_battery_threshold"] = self.high_battery_threshold
        result["low_battery_threshold"] = self.low_battery_threshold
        result["neutral_warning_speed_threshold"] = self.neutral_warning_speed_threshold
        result["neutral_warning_time_threshold"] = self.neutral_warning_time_threshold
        result["rpm_bar_bkg_color"] = self.rpm_bar_bkg_color
        result["rpm_bar_color"] = self.rpm_bar_color
        result["rpm_bar_height"] = self.rpm_bar_height
        result["rpm_color_over_rev"] = self.rpm_color_over_rev
        result["rpm_color_redline"] = self.rpm_color_redline
        result["rpm_color_safe"] = self.rpm_color_safe
        result["rpm_decimal_places"] = self.rpm_decimal_places
        result["rpm_multiplier_critical"] = self.rpm_multiplier_critical
        result["rpm_multiplier_redline"] = self.rpm_multiplier_redline
        result["rpm_multiplier_safe"] = self.rpm_multiplier_safe
        result["rpm_reading_offset_x"] = self.rpm_reading_offset_x
        result["rpm_reading_text_alignment"] = self.rpm_reading_text_alignment
        result["speed_limiter_padding_horizontal"] = self.speed_limiter_padding_horizontal
        result["speed_limiter_text"] = self.speed_limiter_text
        result["warning_color_high_battery"] = self.warning_color_high_battery
        result["warning_color_low_battery"] = self.warning_color_low_battery
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Gear":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar_gap = data.get("bar_gap", obj.bar_gap)
        obj.bar = BarConfig.from_dict(data.get("bar", {}))
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.battery = CellConfig.from_dict(data.get("battery", {}), 'battery')
        obj.battery_bar = CellConfig.from_dict(data.get("battery_bar", {}), 'battery_bar')
        obj.battery_reading = CellConfig.from_dict(data.get("battery_reading", {}), 'battery_reading')
        obj.gauge = CellConfig.from_dict(data.get("gauge", {}), 'gauge')
        obj.inverted_battery = CellConfig.from_dict(data.get("inverted_battery", {}), 'inverted_battery')
        obj.inverted_rpm = CellConfig.from_dict(data.get("inverted_rpm", {}), 'inverted_rpm')
        obj.rpm = CellConfig.from_dict(data.get("rpm", {}), 'rpm')
        obj.rpm_bar = CellConfig.from_dict(data.get("rpm_bar", {}), 'rpm_bar')
        obj.rpm_flickering_above_critical = CellConfig.from_dict(data.get("rpm_flickering_above_critical", {}), 'rpm_flickering_above_critical')
        obj.rpm_reading = CellConfig.from_dict(data.get("rpm_reading", {}), 'rpm_reading')
        obj.speed = CellConfig.from_dict(data.get("speed", {}), 'speed')
        obj.speed_below_gear = CellConfig.from_dict(data.get("speed_below_gear", {}), 'speed_below_gear')
        obj.speed_limiter = CellConfig.from_dict(data.get("speed_limiter", {}), 'speed_limiter')
        obj.battery_bar_bkg_color = data.get("battery_bar_bkg_color", obj.battery_bar_bkg_color)
        obj.battery_bar_color = data.get("battery_bar_color", obj.battery_bar_color)
        obj.battery_bar_color_regen = data.get("battery_bar_color_regen", obj.battery_bar_color_regen)
        obj.battery_bar_height = data.get("battery_bar_height", obj.battery_bar_height)
        obj.battery_decimal_places = data.get("battery_decimal_places", obj.battery_decimal_places)
        obj.battery_reading_offset_x = data.get("battery_reading_offset_x", obj.battery_reading_offset_x)
        obj.battery_reading_text_alignment = data.get("battery_reading_text_alignment", obj.battery_reading_text_alignment)
        obj.font_color = data.get("font_color", obj.font_color)
        obj.font_scale_speed = data.get("font_scale_speed", obj.font_scale_speed)
        obj.font_size_battery = data.get("font_size_battery", obj.font_size_battery)
        obj.font_size_rpm = data.get("font_size_rpm", obj.font_size_rpm)
        obj.font_weight_battery = data.get("font_weight_battery", obj.font_weight_battery)
        obj.font_weight_gear = data.get("font_weight_gear", obj.font_weight_gear)
        obj.font_weight_rpm = data.get("font_weight_rpm", obj.font_weight_rpm)
        obj.font_weight_speed = data.get("font_weight_speed", obj.font_weight_speed)
        obj.high_battery_threshold = data.get("high_battery_threshold", obj.high_battery_threshold)
        obj.low_battery_threshold = data.get("low_battery_threshold", obj.low_battery_threshold)
        obj.neutral_warning_speed_threshold = data.get("neutral_warning_speed_threshold", obj.neutral_warning_speed_threshold)
        obj.neutral_warning_time_threshold = data.get("neutral_warning_time_threshold", obj.neutral_warning_time_threshold)
        obj.rpm_bar_bkg_color = data.get("rpm_bar_bkg_color", obj.rpm_bar_bkg_color)
        obj.rpm_bar_color = data.get("rpm_bar_color", obj.rpm_bar_color)
        obj.rpm_bar_height = data.get("rpm_bar_height", obj.rpm_bar_height)
        obj.rpm_color_over_rev = data.get("rpm_color_over_rev", obj.rpm_color_over_rev)
        obj.rpm_color_redline = data.get("rpm_color_redline", obj.rpm_color_redline)
        obj.rpm_color_safe = data.get("rpm_color_safe", obj.rpm_color_safe)
        obj.rpm_decimal_places = data.get("rpm_decimal_places", obj.rpm_decimal_places)
        obj.rpm_multiplier_critical = data.get("rpm_multiplier_critical", obj.rpm_multiplier_critical)
        obj.rpm_multiplier_redline = data.get("rpm_multiplier_redline", obj.rpm_multiplier_redline)
        obj.rpm_multiplier_safe = data.get("rpm_multiplier_safe", obj.rpm_multiplier_safe)
        obj.rpm_reading_offset_x = data.get("rpm_reading_offset_x", obj.rpm_reading_offset_x)
        obj.rpm_reading_text_alignment = data.get("rpm_reading_text_alignment", obj.rpm_reading_text_alignment)
        obj.speed_limiter_padding_horizontal = data.get("speed_limiter_padding_horizontal", obj.speed_limiter_padding_horizontal)
        obj.speed_limiter_text = data.get("speed_limiter_text", obj.speed_limiter_text)
        obj.warning_color_high_battery = data.get("warning_color_high_battery", obj.warning_color_high_battery)
        obj.warning_color_low_battery = data.get("warning_color_low_battery", obj.warning_color_low_battery)
        return obj
