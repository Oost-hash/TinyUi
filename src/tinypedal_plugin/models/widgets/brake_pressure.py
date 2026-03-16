# Auto-generated widget
# Widget: brake_pressure

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import BarConfig, CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..components import CaptionConfig


@dataclass
class BrakePressure(WidgetConfig):
    name: str = "brake_pressure"

    # groups
    bar: BarConfig = field(default_factory=BarConfig)
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=253, position_y=476))

    # cells
    brake_input: CellConfig = field(default_factory=lambda: CellConfig(id='brake_input'))

    # components
    caption: CaptionConfig = field(default_factory=lambda: CaptionConfig(caption_text='brake pres', show=False))

    # config
    brake_input_color: str = '#00AAFF'
    brake_input_size: int = 3
    font_color: str = '#AAAAAA'
    highlight_color: str = '#00AAFF'

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result.update(self.bar.to_flat())
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.brake_input.to_flat())
        result["bkg_color_caption"] = self.caption.bkg_color
        result["caption_text"] = self.caption.caption_text
        result["font_color_caption"] = self.caption.font_color
        result["show_caption"] = self.caption.show
        result["brake_input_color"] = self.brake_input_color
        result["brake_input_size"] = self.brake_input_size
        result["font_color"] = self.font_color
        result["highlight_color"] = self.highlight_color
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "BrakePressure":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar = BarConfig.from_flat(data)
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.brake_input = CellConfig.from_flat(data, 'brake_input')
        obj.caption = CaptionConfig(
            bkg_color=data.get("bkg_color_caption", obj.caption.bkg_color),
            caption_text=data.get("caption_text", obj.caption.caption_text),
            font_color=data.get("font_color_caption", obj.caption.font_color),
            show=data.get("show_caption", obj.caption.show),
        )
        obj.brake_input_color = data.get("brake_input_color", obj.brake_input_color)
        obj.brake_input_size = data.get("brake_input_size", obj.brake_input_size)
        obj.font_color = data.get("font_color", obj.font_color)
        obj.highlight_color = data.get("highlight_color", obj.highlight_color)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["bar"] = self.bar.to_dict()
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["brake_input"] = self.brake_input.to_dict()
        result["caption"] = self.caption.to_dict()
        result["brake_input_color"] = self.brake_input_color
        result["brake_input_size"] = self.brake_input_size
        result["font_color"] = self.font_color
        result["highlight_color"] = self.highlight_color
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BrakePressure":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar = BarConfig.from_dict(data.get("bar", {}))
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.brake_input = CellConfig.from_dict(data.get("brake_input", {}), 'brake_input')
        obj.caption = CaptionConfig.from_dict(data.get("caption", {}))
        obj.brake_input_color = data.get("brake_input_color", obj.brake_input_color)
        obj.brake_input_size = data.get("brake_input_size", obj.brake_input_size)
        obj.font_color = data.get("font_color", obj.font_color)
        obj.highlight_color = data.get("highlight_color", obj.highlight_color)
        return obj
