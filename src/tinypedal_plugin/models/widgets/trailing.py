# Auto-generated widget
# Widget: trailing

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import CellConfig, PositionConfig, WidgetConfig


@dataclass
class Trailing(WidgetConfig):
    name: str = "trailing"

    # base overrides
    bkg_color: str = '#CC222222'

    # groups
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=433, position_y=610))

    # cells
    absolute_ffb: CellConfig = field(default_factory=lambda: CellConfig(id='absolute_ffb'))
    brake: CellConfig = field(default_factory=lambda: CellConfig(id='brake'))
    clutch: CellConfig = field(default_factory=lambda: CellConfig(id='clutch'))
    ffb: CellConfig = field(default_factory=lambda: CellConfig(id='ffb'))
    inverted_pedal: CellConfig = field(default_factory=lambda: CellConfig(id='inverted_pedal', show=False))
    inverted_steering: CellConfig = field(default_factory=lambda: CellConfig(id='inverted_steering', show=False))
    inverted_trailing: CellConfig = field(default_factory=lambda: CellConfig(id='inverted_trailing'))
    raw_brake: CellConfig = field(default_factory=lambda: CellConfig(id='raw_brake', show=False))
    raw_clutch: CellConfig = field(default_factory=lambda: CellConfig(id='raw_clutch', show=False))
    raw_throttle: CellConfig = field(default_factory=lambda: CellConfig(id='raw_throttle', show=False))
    speed: CellConfig = field(default_factory=lambda: CellConfig(id='speed', show=False))
    steering: CellConfig = field(default_factory=lambda: CellConfig(id='steering', show=False))
    throttle: CellConfig = field(default_factory=lambda: CellConfig(id='throttle'))
    wheel_lock: CellConfig = field(default_factory=lambda: CellConfig(id='wheel_lock'))
    wheel_slip: CellConfig = field(default_factory=lambda: CellConfig(id='wheel_slip'))

    # components
    reference_line: dict = field(default_factory=lambda: {
    1: {'color': '#666666', 'offset': 0.25, 'style': 0, 'width': 1},
    2: {'color': '#666666', 'offset': 0.5, 'style': 0, 'width': 1},
    3: {'color': '#666666', 'offset': 0.75, 'style': 0, 'width': 1},
    4: {'color': '#666666', 'offset': 0, 'style': 0, 'width': 0},
    5: {'color': '#666666', 'offset': 0, 'style': 0, 'width': 0},
})

    # config
    brake_color: str = '#FF2200'
    brake_line_style: int = 0
    brake_line_width: int = 2
    clutch_color: str = '#00C2F2'
    clutch_line_style: int = 0
    clutch_line_width: int = 2
    display_height: int = 60
    display_margin: int = 2
    display_scale: int = 2
    display_width: int = 300
    draw_order_index_brake: int = 1
    draw_order_index_clutch: int = 5
    draw_order_index_ffb: int = 6
    draw_order_index_speed: int = 8
    draw_order_index_steering: int = 7
    draw_order_index_throttle: int = 2
    draw_order_index_wheel_lock: int = 4
    draw_order_index_wheel_slip: int = 3
    ffb_color: str = '#888888'
    ffb_line_style: int = 0
    ffb_line_width: int = 2
    speed_color: str = '#FFFF00'
    speed_line_style: int = 0
    speed_line_width: int = 2
    steering_color: str = '#FFFFFF'
    steering_line_style: int = 0
    steering_line_width: int = 2
    throttle_color: str = '#77FF00'
    throttle_line_style: int = 0
    throttle_line_width: int = 2
    time_scale: int = 1
    wheel_lock_color: str = '#FFFF00'
    wheel_lock_line_style: int = 1
    wheel_lock_line_width: int = 6
    wheel_lock_threshold: float = 0.3
    wheel_slip_color: str = '#FF00FF'
    wheel_slip_line_style: int = 1
    wheel_slip_line_width: int = 6
    wheel_slip_threshold: float = 0.1

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result["bkg_color"] = self.bkg_color
        result.update(self.position.to_flat())
        result.update(self.absolute_ffb.to_flat())
        result.update(self.brake.to_flat())
        result.update(self.clutch.to_flat())
        result.update(self.ffb.to_flat())
        result.update(self.inverted_pedal.to_flat())
        result.update(self.inverted_steering.to_flat())
        result.update(self.inverted_trailing.to_flat())
        result.update(self.raw_brake.to_flat())
        result.update(self.raw_clutch.to_flat())
        result.update(self.raw_throttle.to_flat())
        result.update(self.speed.to_flat())
        result.update(self.steering.to_flat())
        result.update(self.throttle.to_flat())
        result.update(self.wheel_lock.to_flat())
        result.update(self.wheel_slip.to_flat())
        result["reference_line_1_color"] = self.reference_line[1]["color"]
        result["reference_line_1_offset"] = self.reference_line[1]["offset"]
        result["reference_line_1_style"] = self.reference_line[1]["style"]
        result["reference_line_1_width"] = self.reference_line[1]["width"]
        result["reference_line_2_color"] = self.reference_line[2]["color"]
        result["reference_line_2_offset"] = self.reference_line[2]["offset"]
        result["reference_line_2_style"] = self.reference_line[2]["style"]
        result["reference_line_2_width"] = self.reference_line[2]["width"]
        result["reference_line_3_color"] = self.reference_line[3]["color"]
        result["reference_line_3_offset"] = self.reference_line[3]["offset"]
        result["reference_line_3_style"] = self.reference_line[3]["style"]
        result["reference_line_3_width"] = self.reference_line[3]["width"]
        result["reference_line_4_color"] = self.reference_line[4]["color"]
        result["reference_line_4_offset"] = self.reference_line[4]["offset"]
        result["reference_line_4_style"] = self.reference_line[4]["style"]
        result["reference_line_4_width"] = self.reference_line[4]["width"]
        result["reference_line_5_color"] = self.reference_line[5]["color"]
        result["reference_line_5_offset"] = self.reference_line[5]["offset"]
        result["reference_line_5_style"] = self.reference_line[5]["style"]
        result["reference_line_5_width"] = self.reference_line[5]["width"]
        result["show_reference_line"] = True
        result["brake_color"] = self.brake_color
        result["brake_line_style"] = self.brake_line_style
        result["brake_line_width"] = self.brake_line_width
        result["clutch_color"] = self.clutch_color
        result["clutch_line_style"] = self.clutch_line_style
        result["clutch_line_width"] = self.clutch_line_width
        result["display_height"] = self.display_height
        result["display_margin"] = self.display_margin
        result["display_scale"] = self.display_scale
        result["display_width"] = self.display_width
        result["draw_order_index_brake"] = self.draw_order_index_brake
        result["draw_order_index_clutch"] = self.draw_order_index_clutch
        result["draw_order_index_ffb"] = self.draw_order_index_ffb
        result["draw_order_index_speed"] = self.draw_order_index_speed
        result["draw_order_index_steering"] = self.draw_order_index_steering
        result["draw_order_index_throttle"] = self.draw_order_index_throttle
        result["draw_order_index_wheel_lock"] = self.draw_order_index_wheel_lock
        result["draw_order_index_wheel_slip"] = self.draw_order_index_wheel_slip
        result["ffb_color"] = self.ffb_color
        result["ffb_line_style"] = self.ffb_line_style
        result["ffb_line_width"] = self.ffb_line_width
        result["speed_color"] = self.speed_color
        result["speed_line_style"] = self.speed_line_style
        result["speed_line_width"] = self.speed_line_width
        result["steering_color"] = self.steering_color
        result["steering_line_style"] = self.steering_line_style
        result["steering_line_width"] = self.steering_line_width
        result["throttle_color"] = self.throttle_color
        result["throttle_line_style"] = self.throttle_line_style
        result["throttle_line_width"] = self.throttle_line_width
        result["time_scale"] = self.time_scale
        result["wheel_lock_color"] = self.wheel_lock_color
        result["wheel_lock_line_style"] = self.wheel_lock_line_style
        result["wheel_lock_line_width"] = self.wheel_lock_line_width
        result["wheel_lock_threshold"] = self.wheel_lock_threshold
        result["wheel_slip_color"] = self.wheel_slip_color
        result["wheel_slip_line_style"] = self.wheel_slip_line_style
        result["wheel_slip_line_width"] = self.wheel_slip_line_width
        result["wheel_slip_threshold"] = self.wheel_slip_threshold
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "Trailing":
        obj = cls()
        obj.name = data.get("name", obj.name)
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bkg_color = data.get("bkg_color", obj.bkg_color)
        obj.position = PositionConfig.from_flat(data)
        obj.absolute_ffb = CellConfig.from_flat(data, 'absolute_ffb')
        obj.brake = CellConfig.from_flat(data, 'brake')
        obj.clutch = CellConfig.from_flat(data, 'clutch')
        obj.ffb = CellConfig.from_flat(data, 'ffb')
        obj.inverted_pedal = CellConfig.from_flat(data, 'inverted_pedal')
        obj.inverted_steering = CellConfig.from_flat(data, 'inverted_steering')
        obj.inverted_trailing = CellConfig.from_flat(data, 'inverted_trailing')
        obj.raw_brake = CellConfig.from_flat(data, 'raw_brake')
        obj.raw_clutch = CellConfig.from_flat(data, 'raw_clutch')
        obj.raw_throttle = CellConfig.from_flat(data, 'raw_throttle')
        obj.speed = CellConfig.from_flat(data, 'speed')
        obj.steering = CellConfig.from_flat(data, 'steering')
        obj.throttle = CellConfig.from_flat(data, 'throttle')
        obj.wheel_lock = CellConfig.from_flat(data, 'wheel_lock')
        obj.wheel_slip = CellConfig.from_flat(data, 'wheel_slip')
        obj.reference_line = {
            1: {"color": data.get("reference_line_1_color", '#666666'), "offset": data.get("reference_line_1_offset", 0.25), "style": data.get("reference_line_1_style", 0), "width": data.get("reference_line_1_width", 1)},
            2: {"color": data.get("reference_line_2_color", '#666666'), "offset": data.get("reference_line_2_offset", 0.5), "style": data.get("reference_line_2_style", 0), "width": data.get("reference_line_2_width", 1)},
            3: {"color": data.get("reference_line_3_color", '#666666'), "offset": data.get("reference_line_3_offset", 0.75), "style": data.get("reference_line_3_style", 0), "width": data.get("reference_line_3_width", 1)},
            4: {"color": data.get("reference_line_4_color", '#666666'), "offset": data.get("reference_line_4_offset", 0), "style": data.get("reference_line_4_style", 0), "width": data.get("reference_line_4_width", 0)},
            5: {"color": data.get("reference_line_5_color", '#666666'), "offset": data.get("reference_line_5_offset", 0), "style": data.get("reference_line_5_style", 0), "width": data.get("reference_line_5_width", 0)},
        }
        obj.brake_color = data.get("brake_color", obj.brake_color)
        obj.brake_line_style = data.get("brake_line_style", obj.brake_line_style)
        obj.brake_line_width = data.get("brake_line_width", obj.brake_line_width)
        obj.clutch_color = data.get("clutch_color", obj.clutch_color)
        obj.clutch_line_style = data.get("clutch_line_style", obj.clutch_line_style)
        obj.clutch_line_width = data.get("clutch_line_width", obj.clutch_line_width)
        obj.display_height = data.get("display_height", obj.display_height)
        obj.display_margin = data.get("display_margin", obj.display_margin)
        obj.display_scale = data.get("display_scale", obj.display_scale)
        obj.display_width = data.get("display_width", obj.display_width)
        obj.draw_order_index_brake = data.get("draw_order_index_brake", obj.draw_order_index_brake)
        obj.draw_order_index_clutch = data.get("draw_order_index_clutch", obj.draw_order_index_clutch)
        obj.draw_order_index_ffb = data.get("draw_order_index_ffb", obj.draw_order_index_ffb)
        obj.draw_order_index_speed = data.get("draw_order_index_speed", obj.draw_order_index_speed)
        obj.draw_order_index_steering = data.get("draw_order_index_steering", obj.draw_order_index_steering)
        obj.draw_order_index_throttle = data.get("draw_order_index_throttle", obj.draw_order_index_throttle)
        obj.draw_order_index_wheel_lock = data.get("draw_order_index_wheel_lock", obj.draw_order_index_wheel_lock)
        obj.draw_order_index_wheel_slip = data.get("draw_order_index_wheel_slip", obj.draw_order_index_wheel_slip)
        obj.ffb_color = data.get("ffb_color", obj.ffb_color)
        obj.ffb_line_style = data.get("ffb_line_style", obj.ffb_line_style)
        obj.ffb_line_width = data.get("ffb_line_width", obj.ffb_line_width)
        obj.speed_color = data.get("speed_color", obj.speed_color)
        obj.speed_line_style = data.get("speed_line_style", obj.speed_line_style)
        obj.speed_line_width = data.get("speed_line_width", obj.speed_line_width)
        obj.steering_color = data.get("steering_color", obj.steering_color)
        obj.steering_line_style = data.get("steering_line_style", obj.steering_line_style)
        obj.steering_line_width = data.get("steering_line_width", obj.steering_line_width)
        obj.throttle_color = data.get("throttle_color", obj.throttle_color)
        obj.throttle_line_style = data.get("throttle_line_style", obj.throttle_line_style)
        obj.throttle_line_width = data.get("throttle_line_width", obj.throttle_line_width)
        obj.time_scale = data.get("time_scale", obj.time_scale)
        obj.wheel_lock_color = data.get("wheel_lock_color", obj.wheel_lock_color)
        obj.wheel_lock_line_style = data.get("wheel_lock_line_style", obj.wheel_lock_line_style)
        obj.wheel_lock_line_width = data.get("wheel_lock_line_width", obj.wheel_lock_line_width)
        obj.wheel_lock_threshold = data.get("wheel_lock_threshold", obj.wheel_lock_threshold)
        obj.wheel_slip_color = data.get("wheel_slip_color", obj.wheel_slip_color)
        obj.wheel_slip_line_style = data.get("wheel_slip_line_style", obj.wheel_slip_line_style)
        obj.wheel_slip_line_width = data.get("wheel_slip_line_width", obj.wheel_slip_line_width)
        obj.wheel_slip_threshold = data.get("wheel_slip_threshold", obj.wheel_slip_threshold)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["bkg_color"] = self.bkg_color
        result["position"] = self.position.to_dict()
        result["absolute_ffb"] = self.absolute_ffb.to_dict()
        result["brake"] = self.brake.to_dict()
        result["clutch"] = self.clutch.to_dict()
        result["ffb"] = self.ffb.to_dict()
        result["inverted_pedal"] = self.inverted_pedal.to_dict()
        result["inverted_steering"] = self.inverted_steering.to_dict()
        result["inverted_trailing"] = self.inverted_trailing.to_dict()
        result["raw_brake"] = self.raw_brake.to_dict()
        result["raw_clutch"] = self.raw_clutch.to_dict()
        result["raw_throttle"] = self.raw_throttle.to_dict()
        result["speed"] = self.speed.to_dict()
        result["steering"] = self.steering.to_dict()
        result["throttle"] = self.throttle.to_dict()
        result["wheel_lock"] = self.wheel_lock.to_dict()
        result["wheel_slip"] = self.wheel_slip.to_dict()
        result["reference_line"] = self.reference_line
        result["brake_color"] = self.brake_color
        result["brake_line_style"] = self.brake_line_style
        result["brake_line_width"] = self.brake_line_width
        result["clutch_color"] = self.clutch_color
        result["clutch_line_style"] = self.clutch_line_style
        result["clutch_line_width"] = self.clutch_line_width
        result["display_height"] = self.display_height
        result["display_margin"] = self.display_margin
        result["display_scale"] = self.display_scale
        result["display_width"] = self.display_width
        result["draw_order_index_brake"] = self.draw_order_index_brake
        result["draw_order_index_clutch"] = self.draw_order_index_clutch
        result["draw_order_index_ffb"] = self.draw_order_index_ffb
        result["draw_order_index_speed"] = self.draw_order_index_speed
        result["draw_order_index_steering"] = self.draw_order_index_steering
        result["draw_order_index_throttle"] = self.draw_order_index_throttle
        result["draw_order_index_wheel_lock"] = self.draw_order_index_wheel_lock
        result["draw_order_index_wheel_slip"] = self.draw_order_index_wheel_slip
        result["ffb_color"] = self.ffb_color
        result["ffb_line_style"] = self.ffb_line_style
        result["ffb_line_width"] = self.ffb_line_width
        result["speed_color"] = self.speed_color
        result["speed_line_style"] = self.speed_line_style
        result["speed_line_width"] = self.speed_line_width
        result["steering_color"] = self.steering_color
        result["steering_line_style"] = self.steering_line_style
        result["steering_line_width"] = self.steering_line_width
        result["throttle_color"] = self.throttle_color
        result["throttle_line_style"] = self.throttle_line_style
        result["throttle_line_width"] = self.throttle_line_width
        result["time_scale"] = self.time_scale
        result["wheel_lock_color"] = self.wheel_lock_color
        result["wheel_lock_line_style"] = self.wheel_lock_line_style
        result["wheel_lock_line_width"] = self.wheel_lock_line_width
        result["wheel_lock_threshold"] = self.wheel_lock_threshold
        result["wheel_slip_color"] = self.wheel_slip_color
        result["wheel_slip_line_style"] = self.wheel_slip_line_style
        result["wheel_slip_line_width"] = self.wheel_slip_line_width
        result["wheel_slip_threshold"] = self.wheel_slip_threshold
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Trailing":
        obj = cls()
        for key in ("enable", "update_interval", "opacity",
                    "bar_gap", "bar_padding", "layout", "bkg_color"):
            if key in data:
                setattr(obj, key, data[key])
        obj.bkg_color = data.get("bkg_color", obj.bkg_color)
        obj.position = PositionConfig.from_dict(data.get("position", {}))
        obj.absolute_ffb = CellConfig.from_dict(data.get("absolute_ffb", {}), 'absolute_ffb')
        obj.brake = CellConfig.from_dict(data.get("brake", {}), 'brake')
        obj.clutch = CellConfig.from_dict(data.get("clutch", {}), 'clutch')
        obj.ffb = CellConfig.from_dict(data.get("ffb", {}), 'ffb')
        obj.inverted_pedal = CellConfig.from_dict(data.get("inverted_pedal", {}), 'inverted_pedal')
        obj.inverted_steering = CellConfig.from_dict(data.get("inverted_steering", {}), 'inverted_steering')
        obj.inverted_trailing = CellConfig.from_dict(data.get("inverted_trailing", {}), 'inverted_trailing')
        obj.raw_brake = CellConfig.from_dict(data.get("raw_brake", {}), 'raw_brake')
        obj.raw_clutch = CellConfig.from_dict(data.get("raw_clutch", {}), 'raw_clutch')
        obj.raw_throttle = CellConfig.from_dict(data.get("raw_throttle", {}), 'raw_throttle')
        obj.speed = CellConfig.from_dict(data.get("speed", {}), 'speed')
        obj.steering = CellConfig.from_dict(data.get("steering", {}), 'steering')
        obj.throttle = CellConfig.from_dict(data.get("throttle", {}), 'throttle')
        obj.wheel_lock = CellConfig.from_dict(data.get("wheel_lock", {}), 'wheel_lock')
        obj.wheel_slip = CellConfig.from_dict(data.get("wheel_slip", {}), 'wheel_slip')
        obj.reference_line = data.get("reference_line", obj.reference_line)
        obj.brake_color = data.get("brake_color", obj.brake_color)
        obj.brake_line_style = data.get("brake_line_style", obj.brake_line_style)
        obj.brake_line_width = data.get("brake_line_width", obj.brake_line_width)
        obj.clutch_color = data.get("clutch_color", obj.clutch_color)
        obj.clutch_line_style = data.get("clutch_line_style", obj.clutch_line_style)
        obj.clutch_line_width = data.get("clutch_line_width", obj.clutch_line_width)
        obj.display_height = data.get("display_height", obj.display_height)
        obj.display_margin = data.get("display_margin", obj.display_margin)
        obj.display_scale = data.get("display_scale", obj.display_scale)
        obj.display_width = data.get("display_width", obj.display_width)
        obj.draw_order_index_brake = data.get("draw_order_index_brake", obj.draw_order_index_brake)
        obj.draw_order_index_clutch = data.get("draw_order_index_clutch", obj.draw_order_index_clutch)
        obj.draw_order_index_ffb = data.get("draw_order_index_ffb", obj.draw_order_index_ffb)
        obj.draw_order_index_speed = data.get("draw_order_index_speed", obj.draw_order_index_speed)
        obj.draw_order_index_steering = data.get("draw_order_index_steering", obj.draw_order_index_steering)
        obj.draw_order_index_throttle = data.get("draw_order_index_throttle", obj.draw_order_index_throttle)
        obj.draw_order_index_wheel_lock = data.get("draw_order_index_wheel_lock", obj.draw_order_index_wheel_lock)
        obj.draw_order_index_wheel_slip = data.get("draw_order_index_wheel_slip", obj.draw_order_index_wheel_slip)
        obj.ffb_color = data.get("ffb_color", obj.ffb_color)
        obj.ffb_line_style = data.get("ffb_line_style", obj.ffb_line_style)
        obj.ffb_line_width = data.get("ffb_line_width", obj.ffb_line_width)
        obj.speed_color = data.get("speed_color", obj.speed_color)
        obj.speed_line_style = data.get("speed_line_style", obj.speed_line_style)
        obj.speed_line_width = data.get("speed_line_width", obj.speed_line_width)
        obj.steering_color = data.get("steering_color", obj.steering_color)
        obj.steering_line_style = data.get("steering_line_style", obj.steering_line_style)
        obj.steering_line_width = data.get("steering_line_width", obj.steering_line_width)
        obj.throttle_color = data.get("throttle_color", obj.throttle_color)
        obj.throttle_line_style = data.get("throttle_line_style", obj.throttle_line_style)
        obj.throttle_line_width = data.get("throttle_line_width", obj.throttle_line_width)
        obj.time_scale = data.get("time_scale", obj.time_scale)
        obj.wheel_lock_color = data.get("wheel_lock_color", obj.wheel_lock_color)
        obj.wheel_lock_line_style = data.get("wheel_lock_line_style", obj.wheel_lock_line_style)
        obj.wheel_lock_line_width = data.get("wheel_lock_line_width", obj.wheel_lock_line_width)
        obj.wheel_lock_threshold = data.get("wheel_lock_threshold", obj.wheel_lock_threshold)
        obj.wheel_slip_color = data.get("wheel_slip_color", obj.wheel_slip_color)
        obj.wheel_slip_line_style = data.get("wheel_slip_line_style", obj.wheel_slip_line_style)
        obj.wheel_slip_line_width = data.get("wheel_slip_line_width", obj.wheel_slip_line_width)
        obj.wheel_slip_threshold = data.get("wheel_slip_threshold", obj.wheel_slip_threshold)
        return obj
