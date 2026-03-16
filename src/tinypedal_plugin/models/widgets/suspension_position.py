# Auto-generated widget
# Widget: suspension_position

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import BarConfig, CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..components import CaptionConfig


@dataclass
class SuspensionPosition(WidgetConfig):
    name: str = "suspension_position"

    # groups
    bar: BarConfig = field(default_factory=BarConfig)
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=145, position_y=670))

    # cells
    maximum_position_range: CellConfig = field(default_factory=lambda: CellConfig(id='maximum_position_range'))
    third_spring_position_mark: CellConfig = field(default_factory=lambda: CellConfig(id='third_spring_position_mark'))

    # components
    caption: CaptionConfig = field(default_factory=lambda: CaptionConfig(caption_text='susp pos', show=False))

    # config
    font_color: str = '#AAAAAA'
    maximum_position_range_color: str = '#FF2222'
    maximum_position_range_size: int = 3
    negative_position_color: str = '#00AAFF'
    position_max_range: int = 100
    positive_position_color: str = '#FFAA00'
    third_spring_position_mark_color: str = '#FFFFFF'
    third_spring_position_mark_width: int = 2

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result.update(self.bar.to_flat())
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.maximum_position_range.to_flat())
        result.update(self.third_spring_position_mark.to_flat())
        result["bkg_color_caption"] = self.caption.bkg_color
        result["caption_text"] = self.caption.caption_text
        result["font_color_caption"] = self.caption.font_color
        result["show_caption"] = self.caption.show
        result["font_color"] = self.font_color
        result["maximum_position_range_color"] = self.maximum_position_range_color
        result["maximum_position_range_size"] = self.maximum_position_range_size
        result["negative_position_color"] = self.negative_position_color
        result["position_max_range"] = self.position_max_range
        result["positive_position_color"] = self.positive_position_color
        result["third_spring_position_mark_color"] = self.third_spring_position_mark_color
        result["third_spring_position_mark_width"] = self.third_spring_position_mark_width
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "SuspensionPosition":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar = BarConfig.from_flat(data)
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.maximum_position_range = CellConfig.from_flat(data, 'maximum_position_range')
        obj.third_spring_position_mark = CellConfig.from_flat(data, 'third_spring_position_mark')
        obj.caption = CaptionConfig(
            bkg_color=data.get("bkg_color_caption", obj.caption.bkg_color),
            caption_text=data.get("caption_text", obj.caption.caption_text),
            font_color=data.get("font_color_caption", obj.caption.font_color),
            show=data.get("show_caption", obj.caption.show),
        )
        obj.font_color = data.get("font_color", obj.font_color)
        obj.maximum_position_range_color = data.get("maximum_position_range_color", obj.maximum_position_range_color)
        obj.maximum_position_range_size = data.get("maximum_position_range_size", obj.maximum_position_range_size)
        obj.negative_position_color = data.get("negative_position_color", obj.negative_position_color)
        obj.position_max_range = data.get("position_max_range", obj.position_max_range)
        obj.positive_position_color = data.get("positive_position_color", obj.positive_position_color)
        obj.third_spring_position_mark_color = data.get("third_spring_position_mark_color", obj.third_spring_position_mark_color)
        obj.third_spring_position_mark_width = data.get("third_spring_position_mark_width", obj.third_spring_position_mark_width)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["bar"] = self.bar.to_dict()
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["maximum_position_range"] = self.maximum_position_range.to_dict()
        result["third_spring_position_mark"] = self.third_spring_position_mark.to_dict()
        result["caption"] = self.caption.to_dict()
        result["font_color"] = self.font_color
        result["maximum_position_range_color"] = self.maximum_position_range_color
        result["maximum_position_range_size"] = self.maximum_position_range_size
        result["negative_position_color"] = self.negative_position_color
        result["position_max_range"] = self.position_max_range
        result["positive_position_color"] = self.positive_position_color
        result["third_spring_position_mark_color"] = self.third_spring_position_mark_color
        result["third_spring_position_mark_width"] = self.third_spring_position_mark_width
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SuspensionPosition":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar = BarConfig.from_dict(data.get("bar", {}))
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.maximum_position_range = CellConfig.from_dict(data.get("maximum_position_range", {}), 'maximum_position_range')
        obj.third_spring_position_mark = CellConfig.from_dict(data.get("third_spring_position_mark", {}), 'third_spring_position_mark')
        obj.caption = CaptionConfig.from_dict(data.get("caption", {}))
        obj.font_color = data.get("font_color", obj.font_color)
        obj.maximum_position_range_color = data.get("maximum_position_range_color", obj.maximum_position_range_color)
        obj.maximum_position_range_size = data.get("maximum_position_range_size", obj.maximum_position_range_size)
        obj.negative_position_color = data.get("negative_position_color", obj.negative_position_color)
        obj.position_max_range = data.get("position_max_range", obj.position_max_range)
        obj.positive_position_color = data.get("positive_position_color", obj.positive_position_color)
        obj.third_spring_position_mark_color = data.get("third_spring_position_mark_color", obj.third_spring_position_mark_color)
        obj.third_spring_position_mark_width = data.get("third_spring_position_mark_width", obj.third_spring_position_mark_width)
        return obj
