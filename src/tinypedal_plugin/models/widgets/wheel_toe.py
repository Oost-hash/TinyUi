# Auto-generated widget
# Widget: wheel_toe

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import BarConfig, CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..colors import READING
from ..components import CaptionConfig


@dataclass
class WheelToe(WidgetConfig):
    name: str = "wheel_toe"

    # base overrides
    bar_gap: int = 0

    # groups
    bar: BarConfig = field(default_factory=lambda: BarConfig(horizontal_gap=0, vertical_gap=0))
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=140, position_y=447))

    # cells
    toe_in: CellConfig = field(default_factory=lambda: CellConfig(id='toe_in', decimal_places=2))
    total_toe_angle: CellConfig = field(default_factory=lambda: CellConfig(id='total_toe_angle', font_color=READING.font_color, bkg_color=READING.bkg_color, decimal_places=2))

    # components
    caption: CaptionConfig = field(default_factory=lambda: CaptionConfig(caption_text='toe in'))

    # config
    toe_in_smoothing_samples: int = 10
    total_toe_angle_smoothing_samples: int = 20

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result["bar_gap"] = self.bar_gap
        result.update(self.bar.to_flat())
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.toe_in.to_flat())
        result.update(self.total_toe_angle.to_flat())
        result["bkg_color_caption"] = self.caption.bkg_color
        result["caption_text"] = self.caption.caption_text
        result["font_color_caption"] = self.caption.font_color
        result["show_caption"] = self.caption.show
        result["toe_in_smoothing_samples"] = self.toe_in_smoothing_samples
        result["total_toe_angle_smoothing_samples"] = self.total_toe_angle_smoothing_samples
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "WheelToe":
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
        obj.toe_in = CellConfig.from_flat(data, 'toe_in')
        obj.total_toe_angle = CellConfig.from_flat(data, 'total_toe_angle')
        obj.caption = CaptionConfig(
            bkg_color=data.get("bkg_color_caption", obj.caption.bkg_color),
            caption_text=data.get("caption_text", obj.caption.caption_text),
            font_color=data.get("font_color_caption", obj.caption.font_color),
            show=data.get("show_caption", obj.caption.show),
        )
        obj.toe_in_smoothing_samples = data.get("toe_in_smoothing_samples", obj.toe_in_smoothing_samples)
        obj.total_toe_angle_smoothing_samples = data.get("total_toe_angle_smoothing_samples", obj.total_toe_angle_smoothing_samples)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["bar_gap"] = self.bar_gap
        result["bar"] = self.bar.to_dict()
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["toe_in"] = self.toe_in.to_dict()
        result["total_toe_angle"] = self.total_toe_angle.to_dict()
        result["caption"] = self.caption.to_dict()
        result["toe_in_smoothing_samples"] = self.toe_in_smoothing_samples
        result["total_toe_angle_smoothing_samples"] = self.total_toe_angle_smoothing_samples
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WheelToe":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar_gap = data.get("bar_gap", obj.bar_gap)
        obj.bar = BarConfig.from_dict(data.get("bar", {}))
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.toe_in = CellConfig.from_dict(data.get("toe_in", {}), 'toe_in')
        obj.total_toe_angle = CellConfig.from_dict(data.get("total_toe_angle", {}), 'total_toe_angle')
        obj.caption = CaptionConfig.from_dict(data.get("caption", {}))
        obj.toe_in_smoothing_samples = data.get("toe_in_smoothing_samples", obj.toe_in_smoothing_samples)
        obj.total_toe_angle_smoothing_samples = data.get("total_toe_angle_smoothing_samples", obj.total_toe_angle_smoothing_samples)
        return obj
