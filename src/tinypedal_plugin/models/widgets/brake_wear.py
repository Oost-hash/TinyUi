# Auto-generated widget
# Widget: brake_wear

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..colors import GREEN, RED, SECONDARY, TEAL, YELLOW_DIM
from ..components import CaptionConfig


@dataclass
class BrakeWear(WidgetConfig):
    name: str = "brake_wear"

    # groups
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=688, position_y=720))

    # cells
    lifespan_laps: CellConfig = field(default_factory=lambda: CellConfig(id='lifespan_laps', font_color=YELLOW_DIM.font_color, bkg_color=YELLOW_DIM.bkg_color, caption_text='est. laps', column_index=4))
    lifespan_minutes: CellConfig = field(default_factory=lambda: CellConfig(id='lifespan_minutes', font_color=TEAL.font_color, bkg_color=TEAL.bkg_color, caption_text='est. mins', column_index=5))
    live_wear_difference: CellConfig = field(default_factory=lambda: CellConfig(id='live_wear_difference', font_color=SECONDARY.font_color, bkg_color=SECONDARY.bkg_color, show=False, caption_text='live wear', column_index=3))
    remaining: CellConfig = field(default_factory=lambda: CellConfig(id='remaining', font_color=GREEN.font_color, bkg_color=GREEN.bkg_color, caption_text='brake wear', column_index=1))
    thickness: CellConfig = field(default_factory=lambda: CellConfig(id='thickness', show=False))
    warning: CellConfig = field(default_factory=lambda: CellConfig(id='warning', font_color=RED.font_color, bkg_color=RED.bkg_color))
    wear_difference: CellConfig = field(default_factory=lambda: CellConfig(id='wear_difference', font_color=SECONDARY.font_color, bkg_color=SECONDARY.bkg_color, caption_text='wear diff', column_index=2))

    # components
    caption: CaptionConfig = field(default_factory=CaptionConfig)

    # config
    warning_threshold_laps: int = 5
    warning_threshold_minutes: int = 6
    warning_threshold_remaining: int = 30
    warning_threshold_wear: int = 1

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.lifespan_laps.to_flat())
        result.update(self.lifespan_minutes.to_flat())
        result.update(self.live_wear_difference.to_flat())
        result.update(self.remaining.to_flat())
        result.update(self.thickness.to_flat())
        result.update(self.warning.to_flat())
        result.update(self.wear_difference.to_flat())
        result["bkg_color_caption"] = self.caption.bkg_color
        result["font_color_caption"] = self.caption.font_color
        result["show_caption"] = self.caption.show
        result["warning_threshold_laps"] = self.warning_threshold_laps
        result["warning_threshold_minutes"] = self.warning_threshold_minutes
        result["warning_threshold_remaining"] = self.warning_threshold_remaining
        result["warning_threshold_wear"] = self.warning_threshold_wear
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "BrakeWear":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.lifespan_laps = CellConfig.from_flat(data, 'lifespan_laps')
        obj.lifespan_minutes = CellConfig.from_flat(data, 'lifespan_minutes')
        obj.live_wear_difference = CellConfig.from_flat(data, 'live_wear_difference')
        obj.remaining = CellConfig.from_flat(data, 'remaining')
        obj.thickness = CellConfig.from_flat(data, 'thickness')
        obj.warning = CellConfig.from_flat(data, 'warning')
        obj.wear_difference = CellConfig.from_flat(data, 'wear_difference')
        obj.caption = CaptionConfig(
            bkg_color=data.get("bkg_color_caption", obj.caption.bkg_color),
            font_color=data.get("font_color_caption", obj.caption.font_color),
            show=data.get("show_caption", obj.caption.show),
        )
        obj.warning_threshold_laps = data.get("warning_threshold_laps", obj.warning_threshold_laps)
        obj.warning_threshold_minutes = data.get("warning_threshold_minutes", obj.warning_threshold_minutes)
        obj.warning_threshold_remaining = data.get("warning_threshold_remaining", obj.warning_threshold_remaining)
        obj.warning_threshold_wear = data.get("warning_threshold_wear", obj.warning_threshold_wear)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["lifespan_laps"] = self.lifespan_laps.to_dict()
        result["lifespan_minutes"] = self.lifespan_minutes.to_dict()
        result["live_wear_difference"] = self.live_wear_difference.to_dict()
        result["remaining"] = self.remaining.to_dict()
        result["thickness"] = self.thickness.to_dict()
        result["warning"] = self.warning.to_dict()
        result["wear_difference"] = self.wear_difference.to_dict()
        result["caption"] = self.caption.to_dict()
        result["warning_threshold_laps"] = self.warning_threshold_laps
        result["warning_threshold_minutes"] = self.warning_threshold_minutes
        result["warning_threshold_remaining"] = self.warning_threshold_remaining
        result["warning_threshold_wear"] = self.warning_threshold_wear
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BrakeWear":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.lifespan_laps = CellConfig.from_dict(data.get("lifespan_laps", {}), 'lifespan_laps')
        obj.lifespan_minutes = CellConfig.from_dict(data.get("lifespan_minutes", {}), 'lifespan_minutes')
        obj.live_wear_difference = CellConfig.from_dict(data.get("live_wear_difference", {}), 'live_wear_difference')
        obj.remaining = CellConfig.from_dict(data.get("remaining", {}), 'remaining')
        obj.thickness = CellConfig.from_dict(data.get("thickness", {}), 'thickness')
        obj.warning = CellConfig.from_dict(data.get("warning", {}), 'warning')
        obj.wear_difference = CellConfig.from_dict(data.get("wear_difference", {}), 'wear_difference')
        obj.caption = CaptionConfig.from_dict(data.get("caption", {}))
        obj.warning_threshold_laps = data.get("warning_threshold_laps", obj.warning_threshold_laps)
        obj.warning_threshold_minutes = data.get("warning_threshold_minutes", obj.warning_threshold_minutes)
        obj.warning_threshold_remaining = data.get("warning_threshold_remaining", obj.warning_threshold_remaining)
        obj.warning_threshold_wear = data.get("warning_threshold_wear", obj.warning_threshold_wear)
        return obj
