# Auto-generated widget
# Widget: tyre_load

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import BarConfig, CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..components import CaptionConfig


@dataclass
class TyreLoad(WidgetConfig):
    name: str = "tyre_load"

    # groups
    bar: BarConfig = field(default_factory=BarConfig)
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=253, position_y=430))

    # cells
    tyre_load_ratio: CellConfig = field(default_factory=lambda: CellConfig(id='tyre_load_ratio'))

    # components
    caption: CaptionConfig = field(default_factory=lambda: CaptionConfig(caption_text='tyre load', show=False))

    # config
    font_color: str = '#AAAAAA'
    highlight_color: str = '#FFFFFF'

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result.update(self.bar.to_flat())
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.tyre_load_ratio.to_flat())
        result["bkg_color_caption"] = self.caption.bkg_color
        result["caption_text"] = self.caption.caption_text
        result["font_color_caption"] = self.caption.font_color
        result["show_caption"] = self.caption.show
        result["font_color"] = self.font_color
        result["highlight_color"] = self.highlight_color
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "TyreLoad":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar = BarConfig.from_flat(data)
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.tyre_load_ratio = CellConfig.from_flat(data, 'tyre_load_ratio')
        obj.caption = CaptionConfig(
            bkg_color=data.get("bkg_color_caption", obj.caption.bkg_color),
            caption_text=data.get("caption_text", obj.caption.caption_text),
            font_color=data.get("font_color_caption", obj.caption.font_color),
            show=data.get("show_caption", obj.caption.show),
        )
        obj.font_color = data.get("font_color", obj.font_color)
        obj.highlight_color = data.get("highlight_color", obj.highlight_color)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["bar"] = self.bar.to_dict()
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["tyre_load_ratio"] = self.tyre_load_ratio.to_dict()
        result["caption"] = self.caption.to_dict()
        result["font_color"] = self.font_color
        result["highlight_color"] = self.highlight_color
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TyreLoad":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar = BarConfig.from_dict(data.get("bar", {}))
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.tyre_load_ratio = CellConfig.from_dict(data.get("tyre_load_ratio", {}), 'tyre_load_ratio')
        obj.caption = CaptionConfig.from_dict(data.get("caption", {}))
        obj.font_color = data.get("font_color", obj.font_color)
        obj.highlight_color = data.get("highlight_color", obj.highlight_color)
        return obj
