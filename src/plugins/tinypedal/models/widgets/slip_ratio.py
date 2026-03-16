# Auto-generated widget
# Widget: slip_ratio

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import BarConfig, FontConfig, PositionConfig, WidgetConfig
from ..components import CaptionConfig


@dataclass
class SlipRatio(WidgetConfig):
    name: str = "slip_ratio"

    # groups
    bar: BarConfig = field(default_factory=BarConfig)
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=280, position_y=712))

    # components
    caption: CaptionConfig = field(default_factory=lambda: CaptionConfig(caption_text='slip ratio', show=False))

    # config
    critical_slip_ratio_color: str = '#FF00FF'
    font_color: str = '#AAAAAA'
    optimal_slip_ratio_color: str = '#FFFFFF'
    slip_ratio_max_range: int = 50
    slip_ratio_optimal_range: int = 30

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result.update(self.bar.to_flat())
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result["bkg_color_caption"] = self.caption.bkg_color
        result["caption_text"] = self.caption.caption_text
        result["font_color_caption"] = self.caption.font_color
        result["show_caption"] = self.caption.show
        result["critical_slip_ratio_color"] = self.critical_slip_ratio_color
        result["font_color"] = self.font_color
        result["optimal_slip_ratio_color"] = self.optimal_slip_ratio_color
        result["slip_ratio_max_range"] = self.slip_ratio_max_range
        result["slip_ratio_optimal_range"] = self.slip_ratio_optimal_range
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "SlipRatio":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar = BarConfig.from_flat(data)
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.caption = CaptionConfig(
            bkg_color=data.get("bkg_color_caption", obj.caption.bkg_color),
            caption_text=data.get("caption_text", obj.caption.caption_text),
            font_color=data.get("font_color_caption", obj.caption.font_color),
            show=data.get("show_caption", obj.caption.show),
        )
        obj.critical_slip_ratio_color = data.get("critical_slip_ratio_color", obj.critical_slip_ratio_color)
        obj.font_color = data.get("font_color", obj.font_color)
        obj.optimal_slip_ratio_color = data.get("optimal_slip_ratio_color", obj.optimal_slip_ratio_color)
        obj.slip_ratio_max_range = data.get("slip_ratio_max_range", obj.slip_ratio_max_range)
        obj.slip_ratio_optimal_range = data.get("slip_ratio_optimal_range", obj.slip_ratio_optimal_range)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["bar"] = self.bar.to_dict()
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["caption"] = self.caption.to_dict()
        result["critical_slip_ratio_color"] = self.critical_slip_ratio_color
        result["font_color"] = self.font_color
        result["optimal_slip_ratio_color"] = self.optimal_slip_ratio_color
        result["slip_ratio_max_range"] = self.slip_ratio_max_range
        result["slip_ratio_optimal_range"] = self.slip_ratio_optimal_range
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SlipRatio":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar = BarConfig.from_dict(data.get("bar", {}))
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.caption = CaptionConfig.from_dict(data.get("caption", {}))
        obj.critical_slip_ratio_color = data.get("critical_slip_ratio_color", obj.critical_slip_ratio_color)
        obj.font_color = data.get("font_color", obj.font_color)
        obj.optimal_slip_ratio_color = data.get("optimal_slip_ratio_color", obj.optimal_slip_ratio_color)
        obj.slip_ratio_max_range = data.get("slip_ratio_max_range", obj.slip_ratio_max_range)
        obj.slip_ratio_optimal_range = data.get("slip_ratio_optimal_range", obj.slip_ratio_optimal_range)
        return obj
