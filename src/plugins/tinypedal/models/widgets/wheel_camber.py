# Auto-generated widget
# Widget: wheel_camber

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import BarConfig, CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..colors import READING
from ..components import CaptionConfig


@dataclass
class WheelCamber(WidgetConfig):
    name: str = "wheel_camber"

    # base overrides
    bar_gap: int = 0

    # groups
    bar: BarConfig = field(default_factory=lambda: BarConfig(horizontal_gap=0, vertical_gap=0))
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=140, position_y=395))

    # cells
    camber: CellConfig = field(default_factory=lambda: CellConfig(id='camber', decimal_places=2))
    camber_difference: CellConfig = field(default_factory=lambda: CellConfig(id='camber_difference', font_color=READING.font_color, bkg_color=READING.bkg_color, decimal_places=1))

    # components
    caption: CaptionConfig = field(default_factory=lambda: CaptionConfig(caption_text='camber'))

    # config
    camber_difference_smoothing_samples: int = 20
    camber_smoothing_samples: int = 10

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result["bar_gap"] = self.bar_gap
        result.update(self.bar.to_flat())
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.camber.to_flat())
        result.update(self.camber_difference.to_flat())
        result["bkg_color_caption"] = self.caption.bkg_color
        result["caption_text"] = self.caption.caption_text
        result["font_color_caption"] = self.caption.font_color
        result["show_caption"] = self.caption.show
        result["camber_difference_smoothing_samples"] = self.camber_difference_smoothing_samples
        result["camber_smoothing_samples"] = self.camber_smoothing_samples
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "WheelCamber":
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
        obj.camber = CellConfig.from_flat(data, 'camber')
        obj.camber_difference = CellConfig.from_flat(data, 'camber_difference')
        obj.caption = CaptionConfig(
            bkg_color=data.get("bkg_color_caption", obj.caption.bkg_color),
            caption_text=data.get("caption_text", obj.caption.caption_text),
            font_color=data.get("font_color_caption", obj.caption.font_color),
            show=data.get("show_caption", obj.caption.show),
        )
        obj.camber_difference_smoothing_samples = data.get("camber_difference_smoothing_samples", obj.camber_difference_smoothing_samples)
        obj.camber_smoothing_samples = data.get("camber_smoothing_samples", obj.camber_smoothing_samples)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["bar_gap"] = self.bar_gap
        result["bar"] = self.bar.to_dict()
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["camber"] = self.camber.to_dict()
        result["camber_difference"] = self.camber_difference.to_dict()
        result["caption"] = self.caption.to_dict()
        result["camber_difference_smoothing_samples"] = self.camber_difference_smoothing_samples
        result["camber_smoothing_samples"] = self.camber_smoothing_samples
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WheelCamber":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar_gap = data.get("bar_gap", obj.bar_gap)
        obj.bar = BarConfig.from_dict(data.get("bar", {}))
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.camber = CellConfig.from_dict(data.get("camber", {}), 'camber')
        obj.camber_difference = CellConfig.from_dict(data.get("camber_difference", {}), 'camber_difference')
        obj.caption = CaptionConfig.from_dict(data.get("caption", {}))
        obj.camber_difference_smoothing_samples = data.get("camber_difference_smoothing_samples", obj.camber_difference_smoothing_samples)
        obj.camber_smoothing_samples = data.get("camber_smoothing_samples", obj.camber_smoothing_samples)
        return obj
