# Auto-generated widget
# Widget: damage

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import BarConfig, CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..components import WarningFlashConfig


@dataclass
class Damage(WidgetConfig):
    name: str = "damage"

    # base overrides
    bkg_color: str = '#88000000'
    update_interval: int = 100

    # groups
    bar: BarConfig = field(default_factory=lambda: BarConfig(inner_gap=3))
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=658, position_y=515))

    # cells
    aero_integrity_if_available: CellConfig = field(default_factory=lambda: CellConfig(id='aero_integrity_if_available'))
    background: CellConfig = field(default_factory=lambda: CellConfig(id='background'))
    integrity: CellConfig = field(default_factory=lambda: CellConfig(id='integrity'))
    integrity_reading: CellConfig = field(default_factory=lambda: CellConfig(id='integrity_reading'))
    inverted_integrity: CellConfig = field(default_factory=lambda: CellConfig(id='inverted_integrity', show=False))
    last_impact_cone: CellConfig = field(default_factory=lambda: CellConfig(id='last_impact_cone'))

    # components
    detached_warning_flash: WarningFlashConfig = field(default_factory=lambda: WarningFlashConfig(highlight_duration=0.5, interval=0.5))

    # config
    body_color: str = '#888888'
    body_color_damage_heavy: str = '#FF0000'
    body_color_damage_light: str = '#FFFF00'
    body_color_detached: str = '#000000'
    display_margin: int = 4
    last_impact_cone_angle: int = 15
    last_impact_cone_color: str = '#DDFF0000'
    last_impact_cone_duration: int = 15
    parts_max_height: int = 22
    parts_max_width: int = 16
    parts_width: int = 6
    parts_width_ratio: float = 0.5
    suspension_color: str = '#44CC00'
    suspension_color_damage_heavy: str = '#FF00FF'
    suspension_color_damage_light: str = '#FFFF00'
    suspension_color_damage_medium: str = '#FF6600'
    suspension_color_damage_totaled: str = '#0000FF'
    suspension_damage_heavy_threshold: float = 0.4
    suspension_damage_light_threshold: float = 0.02
    suspension_damage_medium_threshold: float = 0.15
    suspension_damage_totaled_threshold: float = 0.8
    warning_color_detached: str = '#FF0000'
    wheel_color_detached: str = '#000000'
    wheel_height: int = 16
    wheel_width: int = 10

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result["bkg_color"] = self.bkg_color
        result["update_interval"] = self.update_interval
        result.update(self.bar.to_flat())
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.aero_integrity_if_available.to_flat())
        result.update(self.background.to_flat())
        result.update(self.integrity.to_flat())
        result.update(self.integrity_reading.to_flat())
        result.update(self.inverted_integrity.to_flat())
        result.update(self.last_impact_cone.to_flat())
        result["show_detached_warning_flash"] = self.detached_warning_flash.enabled
        result["warning_flash_highlight_duration"] = self.detached_warning_flash.highlight_duration
        result["warning_flash_interval"] = self.detached_warning_flash.interval
        result["body_color"] = self.body_color
        result["body_color_damage_heavy"] = self.body_color_damage_heavy
        result["body_color_damage_light"] = self.body_color_damage_light
        result["body_color_detached"] = self.body_color_detached
        result["display_margin"] = self.display_margin
        result["last_impact_cone_angle"] = self.last_impact_cone_angle
        result["last_impact_cone_color"] = self.last_impact_cone_color
        result["last_impact_cone_duration"] = self.last_impact_cone_duration
        result["parts_max_height"] = self.parts_max_height
        result["parts_max_width"] = self.parts_max_width
        result["parts_width"] = self.parts_width
        result["parts_width_ratio"] = self.parts_width_ratio
        result["suspension_color"] = self.suspension_color
        result["suspension_color_damage_heavy"] = self.suspension_color_damage_heavy
        result["suspension_color_damage_light"] = self.suspension_color_damage_light
        result["suspension_color_damage_medium"] = self.suspension_color_damage_medium
        result["suspension_color_damage_totaled"] = self.suspension_color_damage_totaled
        result["suspension_damage_heavy_threshold"] = self.suspension_damage_heavy_threshold
        result["suspension_damage_light_threshold"] = self.suspension_damage_light_threshold
        result["suspension_damage_medium_threshold"] = self.suspension_damage_medium_threshold
        result["suspension_damage_totaled_threshold"] = self.suspension_damage_totaled_threshold
        result["warning_color_detached"] = self.warning_color_detached
        result["wheel_color_detached"] = self.wheel_color_detached
        result["wheel_height"] = self.wheel_height
        result["wheel_width"] = self.wheel_width
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "Damage":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bkg_color = data.get("bkg_color", obj.bkg_color)
        obj.update_interval = data.get("update_interval", obj.update_interval)
        obj.bar = BarConfig.from_flat(data)
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.aero_integrity_if_available = CellConfig.from_flat(data, 'aero_integrity_if_available')
        obj.background = CellConfig.from_flat(data, 'background')
        obj.integrity = CellConfig.from_flat(data, 'integrity')
        obj.integrity_reading = CellConfig.from_flat(data, 'integrity_reading')
        obj.inverted_integrity = CellConfig.from_flat(data, 'inverted_integrity')
        obj.last_impact_cone = CellConfig.from_flat(data, 'last_impact_cone')
        obj.detached_warning_flash = WarningFlashConfig(
            enabled=data.get("show_detached_warning_flash", obj.detached_warning_flash.enabled),
            highlight_duration=data.get("warning_flash_highlight_duration", obj.detached_warning_flash.highlight_duration),
            interval=data.get("warning_flash_interval", obj.detached_warning_flash.interval),
        )
        obj.body_color = data.get("body_color", obj.body_color)
        obj.body_color_damage_heavy = data.get("body_color_damage_heavy", obj.body_color_damage_heavy)
        obj.body_color_damage_light = data.get("body_color_damage_light", obj.body_color_damage_light)
        obj.body_color_detached = data.get("body_color_detached", obj.body_color_detached)
        obj.display_margin = data.get("display_margin", obj.display_margin)
        obj.last_impact_cone_angle = data.get("last_impact_cone_angle", obj.last_impact_cone_angle)
        obj.last_impact_cone_color = data.get("last_impact_cone_color", obj.last_impact_cone_color)
        obj.last_impact_cone_duration = data.get("last_impact_cone_duration", obj.last_impact_cone_duration)
        obj.parts_max_height = data.get("parts_max_height", obj.parts_max_height)
        obj.parts_max_width = data.get("parts_max_width", obj.parts_max_width)
        obj.parts_width = data.get("parts_width", obj.parts_width)
        obj.parts_width_ratio = data.get("parts_width_ratio", obj.parts_width_ratio)
        obj.suspension_color = data.get("suspension_color", obj.suspension_color)
        obj.suspension_color_damage_heavy = data.get("suspension_color_damage_heavy", obj.suspension_color_damage_heavy)
        obj.suspension_color_damage_light = data.get("suspension_color_damage_light", obj.suspension_color_damage_light)
        obj.suspension_color_damage_medium = data.get("suspension_color_damage_medium", obj.suspension_color_damage_medium)
        obj.suspension_color_damage_totaled = data.get("suspension_color_damage_totaled", obj.suspension_color_damage_totaled)
        obj.suspension_damage_heavy_threshold = data.get("suspension_damage_heavy_threshold", obj.suspension_damage_heavy_threshold)
        obj.suspension_damage_light_threshold = data.get("suspension_damage_light_threshold", obj.suspension_damage_light_threshold)
        obj.suspension_damage_medium_threshold = data.get("suspension_damage_medium_threshold", obj.suspension_damage_medium_threshold)
        obj.suspension_damage_totaled_threshold = data.get("suspension_damage_totaled_threshold", obj.suspension_damage_totaled_threshold)
        obj.warning_color_detached = data.get("warning_color_detached", obj.warning_color_detached)
        obj.wheel_color_detached = data.get("wheel_color_detached", obj.wheel_color_detached)
        obj.wheel_height = data.get("wheel_height", obj.wheel_height)
        obj.wheel_width = data.get("wheel_width", obj.wheel_width)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["bkg_color"] = self.bkg_color
        result["update_interval"] = self.update_interval
        result["bar"] = self.bar.to_dict()
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["aero_integrity_if_available"] = self.aero_integrity_if_available.to_dict()
        result["background"] = self.background.to_dict()
        result["integrity"] = self.integrity.to_dict()
        result["integrity_reading"] = self.integrity_reading.to_dict()
        result["inverted_integrity"] = self.inverted_integrity.to_dict()
        result["last_impact_cone"] = self.last_impact_cone.to_dict()
        result["detached_warning_flash"] = self.detached_warning_flash.to_dict()
        result["body_color"] = self.body_color
        result["body_color_damage_heavy"] = self.body_color_damage_heavy
        result["body_color_damage_light"] = self.body_color_damage_light
        result["body_color_detached"] = self.body_color_detached
        result["display_margin"] = self.display_margin
        result["last_impact_cone_angle"] = self.last_impact_cone_angle
        result["last_impact_cone_color"] = self.last_impact_cone_color
        result["last_impact_cone_duration"] = self.last_impact_cone_duration
        result["parts_max_height"] = self.parts_max_height
        result["parts_max_width"] = self.parts_max_width
        result["parts_width"] = self.parts_width
        result["parts_width_ratio"] = self.parts_width_ratio
        result["suspension_color"] = self.suspension_color
        result["suspension_color_damage_heavy"] = self.suspension_color_damage_heavy
        result["suspension_color_damage_light"] = self.suspension_color_damage_light
        result["suspension_color_damage_medium"] = self.suspension_color_damage_medium
        result["suspension_color_damage_totaled"] = self.suspension_color_damage_totaled
        result["suspension_damage_heavy_threshold"] = self.suspension_damage_heavy_threshold
        result["suspension_damage_light_threshold"] = self.suspension_damage_light_threshold
        result["suspension_damage_medium_threshold"] = self.suspension_damage_medium_threshold
        result["suspension_damage_totaled_threshold"] = self.suspension_damage_totaled_threshold
        result["warning_color_detached"] = self.warning_color_detached
        result["wheel_color_detached"] = self.wheel_color_detached
        result["wheel_height"] = self.wheel_height
        result["wheel_width"] = self.wheel_width
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Damage":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bkg_color = data.get("bkg_color", obj.bkg_color)
        obj.update_interval = data.get("update_interval", obj.update_interval)
        obj.bar = BarConfig.from_dict(data.get("bar", {}))
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.aero_integrity_if_available = CellConfig.from_dict(data.get("aero_integrity_if_available", {}), 'aero_integrity_if_available')
        obj.background = CellConfig.from_dict(data.get("background", {}), 'background')
        obj.integrity = CellConfig.from_dict(data.get("integrity", {}), 'integrity')
        obj.integrity_reading = CellConfig.from_dict(data.get("integrity_reading", {}), 'integrity_reading')
        obj.inverted_integrity = CellConfig.from_dict(data.get("inverted_integrity", {}), 'inverted_integrity')
        obj.last_impact_cone = CellConfig.from_dict(data.get("last_impact_cone", {}), 'last_impact_cone')
        obj.detached_warning_flash = WarningFlashConfig.from_dict(data.get("detached_warning_flash", {}))
        obj.body_color = data.get("body_color", obj.body_color)
        obj.body_color_damage_heavy = data.get("body_color_damage_heavy", obj.body_color_damage_heavy)
        obj.body_color_damage_light = data.get("body_color_damage_light", obj.body_color_damage_light)
        obj.body_color_detached = data.get("body_color_detached", obj.body_color_detached)
        obj.display_margin = data.get("display_margin", obj.display_margin)
        obj.last_impact_cone_angle = data.get("last_impact_cone_angle", obj.last_impact_cone_angle)
        obj.last_impact_cone_color = data.get("last_impact_cone_color", obj.last_impact_cone_color)
        obj.last_impact_cone_duration = data.get("last_impact_cone_duration", obj.last_impact_cone_duration)
        obj.parts_max_height = data.get("parts_max_height", obj.parts_max_height)
        obj.parts_max_width = data.get("parts_max_width", obj.parts_max_width)
        obj.parts_width = data.get("parts_width", obj.parts_width)
        obj.parts_width_ratio = data.get("parts_width_ratio", obj.parts_width_ratio)
        obj.suspension_color = data.get("suspension_color", obj.suspension_color)
        obj.suspension_color_damage_heavy = data.get("suspension_color_damage_heavy", obj.suspension_color_damage_heavy)
        obj.suspension_color_damage_light = data.get("suspension_color_damage_light", obj.suspension_color_damage_light)
        obj.suspension_color_damage_medium = data.get("suspension_color_damage_medium", obj.suspension_color_damage_medium)
        obj.suspension_color_damage_totaled = data.get("suspension_color_damage_totaled", obj.suspension_color_damage_totaled)
        obj.suspension_damage_heavy_threshold = data.get("suspension_damage_heavy_threshold", obj.suspension_damage_heavy_threshold)
        obj.suspension_damage_light_threshold = data.get("suspension_damage_light_threshold", obj.suspension_damage_light_threshold)
        obj.suspension_damage_medium_threshold = data.get("suspension_damage_medium_threshold", obj.suspension_damage_medium_threshold)
        obj.suspension_damage_totaled_threshold = data.get("suspension_damage_totaled_threshold", obj.suspension_damage_totaled_threshold)
        obj.warning_color_detached = data.get("warning_color_detached", obj.warning_color_detached)
        obj.wheel_color_detached = data.get("wheel_color_detached", obj.wheel_color_detached)
        obj.wheel_height = data.get("wheel_height", obj.wheel_height)
        obj.wheel_width = data.get("wheel_width", obj.wheel_width)
        return obj
