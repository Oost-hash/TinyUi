# Auto-generated widget
# Widget: pit_stop_estimate

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import BarConfig, CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..colors import DATA, DATA_DIM, INVERTED
from ..components import CaptionConfig


@dataclass
class PitStopEstimate(WidgetConfig):
    name: str = "pit_stop_estimate"

    # base overrides
    bar_gap: int = 0
    update_interval: int = 50

    # groups
    bar: BarConfig = field(default_factory=lambda: BarConfig(bar_width=5))
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=360, position_y=934))

    # cells
    actual_relative_refill: CellConfig = field(default_factory=lambda: CellConfig(id='actual_relative_refill', font_color=INVERTED.font_color, bkg_color=INVERTED.bkg_color, decimal_places=2, caption_text='refill'))
    lower: CellConfig = field(default_factory=lambda: CellConfig(id='lower', column_index=3))
    minimum_total_duration: CellConfig = field(default_factory=lambda: CellConfig(id='minimum_total_duration', font_color=DATA_DIM.font_color, bkg_color=DATA_DIM.bkg_color, decimal_places=2, caption_text='min'))
    pass_duration: CellConfig = field(default_factory=lambda: CellConfig(id='pass_duration', font_color=INVERTED.font_color, bkg_color=INVERTED.bkg_color, decimal_places=2, caption_text='pass'))
    pit_occupancy: CellConfig = field(default_factory=lambda: CellConfig(id='pit_occupancy', font_color=INVERTED.font_color, bkg_color=INVERTED.bkg_color, caption_text='p/in'))
    pit_requests: CellConfig = field(default_factory=lambda: CellConfig(id='pit_requests', font_color=DATA.font_color, bkg_color=DATA.bkg_color, caption_text='r/out'))
    pit_timer: CellConfig = field(default_factory=lambda: CellConfig(id='pit_timer', font_color=DATA.font_color, bkg_color=DATA.bkg_color, decimal_places=2, caption_text='timer'))
    relative_refilling: CellConfig = field(default_factory=lambda: CellConfig(id='relative_refilling'))
    stop_duration: CellConfig = field(default_factory=lambda: CellConfig(id='stop_duration', bkg_color='#0099FF', decimal_places=2, caption_text='stop'))
    total_relative_refill: CellConfig = field(default_factory=lambda: CellConfig(id='total_relative_refill', font_color=DATA.font_color, bkg_color=DATA.bkg_color, decimal_places=2, caption_text='total'))
    upper: CellConfig = field(default_factory=lambda: CellConfig(id='upper', column_index=1))

    # components
    caption: CaptionConfig = field(default_factory=CaptionConfig)

    # config
    additional_pitstop_time: int = 2
    lengthy_stop_duration_threshold: int = 60
    stop_go_penalty_time: int = 10
    swap_lower_caption: bool = False
    swap_upper_caption: bool = False
    warning_color_lengthy_stop: str = '#FF2200'

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result["bar_gap"] = self.bar_gap
        result["update_interval"] = self.update_interval
        result.update(self.bar.to_flat())
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.actual_relative_refill.to_flat())
        result.update(self.lower.to_flat())
        result.update(self.minimum_total_duration.to_flat())
        result.update(self.pass_duration.to_flat())
        result.update(self.pit_occupancy.to_flat())
        result.update(self.pit_requests.to_flat())
        result.update(self.pit_timer.to_flat())
        result.update(self.relative_refilling.to_flat())
        result.update(self.stop_duration.to_flat())
        result.update(self.total_relative_refill.to_flat())
        result.update(self.upper.to_flat())
        result["bkg_color_caption"] = self.caption.bkg_color
        result["font_color_caption"] = self.caption.font_color
        result["show_caption"] = self.caption.show
        result["additional_pitstop_time"] = self.additional_pitstop_time
        result["lengthy_stop_duration_threshold"] = self.lengthy_stop_duration_threshold
        result["stop_go_penalty_time"] = self.stop_go_penalty_time
        result["swap_lower_caption"] = self.swap_lower_caption
        result["swap_upper_caption"] = self.swap_upper_caption
        result["warning_color_lengthy_stop"] = self.warning_color_lengthy_stop
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "PitStopEstimate":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar_gap = data.get("bar_gap", obj.bar_gap)
        obj.update_interval = data.get("update_interval", obj.update_interval)
        obj.bar = BarConfig.from_flat(data)
        obj.font = FontConfig.from_flat(data)
        obj.position = PositionConfig.from_flat(data)
        obj.actual_relative_refill = CellConfig.from_flat(data, 'actual_relative_refill')
        obj.lower = CellConfig.from_flat(data, 'lower')
        obj.minimum_total_duration = CellConfig.from_flat(data, 'minimum_total_duration')
        obj.pass_duration = CellConfig.from_flat(data, 'pass_duration')
        obj.pit_occupancy = CellConfig.from_flat(data, 'pit_occupancy')
        obj.pit_requests = CellConfig.from_flat(data, 'pit_requests')
        obj.pit_timer = CellConfig.from_flat(data, 'pit_timer')
        obj.relative_refilling = CellConfig.from_flat(data, 'relative_refilling')
        obj.stop_duration = CellConfig.from_flat(data, 'stop_duration')
        obj.total_relative_refill = CellConfig.from_flat(data, 'total_relative_refill')
        obj.upper = CellConfig.from_flat(data, 'upper')
        obj.caption = CaptionConfig(
            bkg_color=data.get("bkg_color_caption", obj.caption.bkg_color),
            font_color=data.get("font_color_caption", obj.caption.font_color),
            show=data.get("show_caption", obj.caption.show),
        )
        obj.additional_pitstop_time = data.get("additional_pitstop_time", obj.additional_pitstop_time)
        obj.lengthy_stop_duration_threshold = data.get("lengthy_stop_duration_threshold", obj.lengthy_stop_duration_threshold)
        obj.stop_go_penalty_time = data.get("stop_go_penalty_time", obj.stop_go_penalty_time)
        obj.swap_lower_caption = data.get("swap_lower_caption", obj.swap_lower_caption)
        obj.swap_upper_caption = data.get("swap_upper_caption", obj.swap_upper_caption)
        obj.warning_color_lengthy_stop = data.get("warning_color_lengthy_stop", obj.warning_color_lengthy_stop)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["bar_gap"] = self.bar_gap
        result["update_interval"] = self.update_interval
        result["bar"] = self.bar.to_dict()
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["actual_relative_refill"] = self.actual_relative_refill.to_dict()
        result["lower"] = self.lower.to_dict()
        result["minimum_total_duration"] = self.minimum_total_duration.to_dict()
        result["pass_duration"] = self.pass_duration.to_dict()
        result["pit_occupancy"] = self.pit_occupancy.to_dict()
        result["pit_requests"] = self.pit_requests.to_dict()
        result["pit_timer"] = self.pit_timer.to_dict()
        result["relative_refilling"] = self.relative_refilling.to_dict()
        result["stop_duration"] = self.stop_duration.to_dict()
        result["total_relative_refill"] = self.total_relative_refill.to_dict()
        result["upper"] = self.upper.to_dict()
        result["caption"] = self.caption.to_dict()
        result["additional_pitstop_time"] = self.additional_pitstop_time
        result["lengthy_stop_duration_threshold"] = self.lengthy_stop_duration_threshold
        result["stop_go_penalty_time"] = self.stop_go_penalty_time
        result["swap_lower_caption"] = self.swap_lower_caption
        result["swap_upper_caption"] = self.swap_upper_caption
        result["warning_color_lengthy_stop"] = self.warning_color_lengthy_stop
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PitStopEstimate":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bar_gap = data.get("bar_gap", obj.bar_gap)
        obj.update_interval = data.get("update_interval", obj.update_interval)
        obj.bar = BarConfig.from_dict(data.get("bar", {}))
        obj.font = FontConfig.from_dict(data.get("font", {}))
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.actual_relative_refill = CellConfig.from_dict(data.get("actual_relative_refill", {}), 'actual_relative_refill')
        obj.lower = CellConfig.from_dict(data.get("lower", {}), 'lower')
        obj.minimum_total_duration = CellConfig.from_dict(data.get("minimum_total_duration", {}), 'minimum_total_duration')
        obj.pass_duration = CellConfig.from_dict(data.get("pass_duration", {}), 'pass_duration')
        obj.pit_occupancy = CellConfig.from_dict(data.get("pit_occupancy", {}), 'pit_occupancy')
        obj.pit_requests = CellConfig.from_dict(data.get("pit_requests", {}), 'pit_requests')
        obj.pit_timer = CellConfig.from_dict(data.get("pit_timer", {}), 'pit_timer')
        obj.relative_refilling = CellConfig.from_dict(data.get("relative_refilling", {}), 'relative_refilling')
        obj.stop_duration = CellConfig.from_dict(data.get("stop_duration", {}), 'stop_duration')
        obj.total_relative_refill = CellConfig.from_dict(data.get("total_relative_refill", {}), 'total_relative_refill')
        obj.upper = CellConfig.from_dict(data.get("upper", {}), 'upper')
        obj.caption = CaptionConfig.from_dict(data.get("caption", {}))
        obj.additional_pitstop_time = data.get("additional_pitstop_time", obj.additional_pitstop_time)
        obj.lengthy_stop_duration_threshold = data.get("lengthy_stop_duration_threshold", obj.lengthy_stop_duration_threshold)
        obj.stop_go_penalty_time = data.get("stop_go_penalty_time", obj.stop_go_penalty_time)
        obj.swap_lower_caption = data.get("swap_lower_caption", obj.swap_lower_caption)
        obj.swap_upper_caption = data.get("swap_upper_caption", obj.swap_upper_caption)
        obj.warning_color_lengthy_stop = data.get("warning_color_lengthy_stop", obj.warning_color_lengthy_stop)
        return obj
