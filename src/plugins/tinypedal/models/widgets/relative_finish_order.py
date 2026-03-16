# Auto-generated widget
# Widget: relative_finish_order

from dataclasses import dataclass, field
from typing import Any, Dict

from ..base import BarConfig, CellConfig, FontConfig, PositionConfig, WidgetConfig
from ..colors import DARK_GREEN, DARK_ORANGE, DATA, DATA_DIM, GREEN, LIGHT_INVERT, MID_GRAY, ORANGE


@dataclass
class RelativeFinishOrder(WidgetConfig):
    name: str = "relative_finish_order"

    # base overrides
    bar_gap: int = 0
    update_interval: int = 100

    # groups
    bar: BarConfig = field(default_factory=lambda: BarConfig(bar_width=5))
    font: FontConfig = field(default_factory=FontConfig)
    position: PositionConfig = field(default_factory=lambda: PositionConfig(position_x=360, position_y=824))

    # cells
    absolute_refilling: CellConfig = field(default_factory=lambda: CellConfig(id='absolute_refilling', show=False))
    extra_refilling: CellConfig = field(default_factory=lambda: CellConfig(id='extra_refilling'))
    laps: CellConfig = field(default_factory=lambda: CellConfig(id='laps', decimal_places=2))
    leader: CellConfig = field(default_factory=lambda: CellConfig(id='leader', font_color='#333333', bkg_color='#EEEEEE'))
    near_finish: CellConfig = field(default_factory=lambda: CellConfig(id='near_finish', font_color=DARK_ORANGE.font_color, bkg_color=DARK_ORANGE.bkg_color))
    near_start: CellConfig = field(default_factory=lambda: CellConfig(id='near_start', font_color=DARK_GREEN.font_color, bkg_color=DARK_GREEN.bkg_color))
    pit_time: CellConfig = field(default_factory=lambda: CellConfig(id='pit_time', font_color=MID_GRAY.font_color, bkg_color=MID_GRAY.bkg_color))
    player: CellConfig = field(default_factory=lambda: CellConfig(id='player', font_color=LIGHT_INVERT.font_color, bkg_color=LIGHT_INVERT.bkg_color))
    refill: CellConfig = field(default_factory=lambda: CellConfig(id='refill', font_color=DATA_DIM.font_color, bkg_color=DATA_DIM.bkg_color, decimal_places=1))

    # components
    prediction: dict = field(default_factory=lambda: {
    1: {'leader_pit_time': 30, 'player_pit_time': 30},
    2: {'leader_pit_time': 40, 'player_pit_time': 40},
    3: {'leader_pit_time': 50, 'player_pit_time': 50},
    4: {'leader_pit_time': 60, 'player_pit_time': 60},
    5: {'leader_pit_time': 70, 'player_pit_time': 70},
    6: {'leader_pit_time': 80, 'player_pit_time': 80},
    7: {'leader_pit_time': 90, 'player_pit_time': 90},
    8: {'leader_pit_time': 100, 'player_pit_time': 100},
    9: {'leader_pit_time': 110, 'player_pit_time': 110},
    10: {'leader_pit_time': 120, 'player_pit_time': 120},
})

    # config
    leader_laptime_pace_margin: int = 5
    leader_laptime_pace_samples: int = 6
    near_finish_range: int = 20
    near_start_range: int = 20
    number_of_extra_laps: int = 1
    number_of_prediction: int = 4

    def to_flat(self) -> Dict[str, Any]:
        result = super().to_flat()
        result["name"] = self.name
        result["bar_gap"] = self.bar_gap
        result["update_interval"] = self.update_interval
        result.update(self.bar.to_flat())
        result.update(self.font.to_flat())
        result.update(self.position.to_flat())
        result.update(self.absolute_refilling.to_flat())
        result.update(self.extra_refilling.to_flat())
        result.update(self.laps.to_flat())
        result.update(self.leader.to_flat())
        result.update(self.near_finish.to_flat())
        result.update(self.near_start.to_flat())
        result.update(self.pit_time.to_flat())
        result.update(self.player.to_flat())
        result.update(self.refill.to_flat())
        result["prediction_1_leader_pit_time"] = self.prediction[1]["leader_pit_time"]
        result["prediction_1_player_pit_time"] = self.prediction[1]["player_pit_time"]
        result["prediction_2_leader_pit_time"] = self.prediction[2]["leader_pit_time"]
        result["prediction_2_player_pit_time"] = self.prediction[2]["player_pit_time"]
        result["prediction_3_leader_pit_time"] = self.prediction[3]["leader_pit_time"]
        result["prediction_3_player_pit_time"] = self.prediction[3]["player_pit_time"]
        result["prediction_4_leader_pit_time"] = self.prediction[4]["leader_pit_time"]
        result["prediction_4_player_pit_time"] = self.prediction[4]["player_pit_time"]
        result["prediction_5_leader_pit_time"] = self.prediction[5]["leader_pit_time"]
        result["prediction_5_player_pit_time"] = self.prediction[5]["player_pit_time"]
        result["prediction_6_leader_pit_time"] = self.prediction[6]["leader_pit_time"]
        result["prediction_6_player_pit_time"] = self.prediction[6]["player_pit_time"]
        result["prediction_7_leader_pit_time"] = self.prediction[7]["leader_pit_time"]
        result["prediction_7_player_pit_time"] = self.prediction[7]["player_pit_time"]
        result["prediction_8_leader_pit_time"] = self.prediction[8]["leader_pit_time"]
        result["prediction_8_player_pit_time"] = self.prediction[8]["player_pit_time"]
        result["prediction_9_leader_pit_time"] = self.prediction[9]["leader_pit_time"]
        result["prediction_9_player_pit_time"] = self.prediction[9]["player_pit_time"]
        result["prediction_10_leader_pit_time"] = self.prediction[10]["leader_pit_time"]
        result["prediction_10_player_pit_time"] = self.prediction[10]["player_pit_time"]
        result["leader_laptime_pace_margin"] = self.leader_laptime_pace_margin
        result["leader_laptime_pace_samples"] = self.leader_laptime_pace_samples
        result["near_finish_range"] = self.near_finish_range
        result["near_start_range"] = self.near_start_range
        result["number_of_extra_laps"] = self.number_of_extra_laps
        result["number_of_prediction"] = self.number_of_prediction
        return result

    @classmethod
    def from_flat(cls, data: Dict[str, Any]) -> "RelativeFinishOrder":
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
        obj.absolute_refilling = CellConfig.from_flat(data, 'absolute_refilling')
        obj.extra_refilling = CellConfig.from_flat(data, 'extra_refilling')
        obj.laps = CellConfig.from_flat(data, 'laps')
        obj.leader = CellConfig.from_flat(data, 'leader')
        obj.near_finish = CellConfig.from_flat(data, 'near_finish')
        obj.near_start = CellConfig.from_flat(data, 'near_start')
        obj.pit_time = CellConfig.from_flat(data, 'pit_time')
        obj.player = CellConfig.from_flat(data, 'player')
        obj.refill = CellConfig.from_flat(data, 'refill')
        obj.prediction = {
            1: {"leader_pit_time": data.get("prediction_1_leader_pit_time", 30), "player_pit_time": data.get("prediction_1_player_pit_time", 30)},
            2: {"leader_pit_time": data.get("prediction_2_leader_pit_time", 40), "player_pit_time": data.get("prediction_2_player_pit_time", 40)},
            3: {"leader_pit_time": data.get("prediction_3_leader_pit_time", 50), "player_pit_time": data.get("prediction_3_player_pit_time", 50)},
            4: {"leader_pit_time": data.get("prediction_4_leader_pit_time", 60), "player_pit_time": data.get("prediction_4_player_pit_time", 60)},
            5: {"leader_pit_time": data.get("prediction_5_leader_pit_time", 70), "player_pit_time": data.get("prediction_5_player_pit_time", 70)},
            6: {"leader_pit_time": data.get("prediction_6_leader_pit_time", 80), "player_pit_time": data.get("prediction_6_player_pit_time", 80)},
            7: {"leader_pit_time": data.get("prediction_7_leader_pit_time", 90), "player_pit_time": data.get("prediction_7_player_pit_time", 90)},
            8: {"leader_pit_time": data.get("prediction_8_leader_pit_time", 100), "player_pit_time": data.get("prediction_8_player_pit_time", 100)},
            9: {"leader_pit_time": data.get("prediction_9_leader_pit_time", 110), "player_pit_time": data.get("prediction_9_player_pit_time", 110)},
            10: {"leader_pit_time": data.get("prediction_10_leader_pit_time", 120), "player_pit_time": data.get("prediction_10_player_pit_time", 120)},
        }
        obj.leader_laptime_pace_margin = data.get("leader_laptime_pace_margin", obj.leader_laptime_pace_margin)
        obj.leader_laptime_pace_samples = data.get("leader_laptime_pace_samples", obj.leader_laptime_pace_samples)
        obj.near_finish_range = data.get("near_finish_range", obj.near_finish_range)
        obj.near_start_range = data.get("near_start_range", obj.near_start_range)
        obj.number_of_extra_laps = data.get("number_of_extra_laps", obj.number_of_extra_laps)
        obj.number_of_prediction = data.get("number_of_prediction", obj.number_of_prediction)
        return obj

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result["bar_gap"] = self.bar_gap
        result["update_interval"] = self.update_interval
        result["bar"] = self.bar.to_dict()
        result["font"] = self.font.to_dict()
        result["position"] = self.position.to_dict()
        result["absolute_refilling"] = self.absolute_refilling.to_dict()
        result["extra_refilling"] = self.extra_refilling.to_dict()
        result["laps"] = self.laps.to_dict()
        result["leader"] = self.leader.to_dict()
        result["near_finish"] = self.near_finish.to_dict()
        result["near_start"] = self.near_start.to_dict()
        result["pit_time"] = self.pit_time.to_dict()
        result["player"] = self.player.to_dict()
        result["refill"] = self.refill.to_dict()
        result["prediction"] = self.prediction
        result["leader_laptime_pace_margin"] = self.leader_laptime_pace_margin
        result["leader_laptime_pace_samples"] = self.leader_laptime_pace_samples
        result["near_finish_range"] = self.near_finish_range
        result["near_start_range"] = self.near_start_range
        result["number_of_extra_laps"] = self.number_of_extra_laps
        result["number_of_prediction"] = self.number_of_prediction
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RelativeFinishOrder":
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
        obj.absolute_refilling = CellConfig.from_dict(data.get("absolute_refilling", {}), 'absolute_refilling')
        obj.extra_refilling = CellConfig.from_dict(data.get("extra_refilling", {}), 'extra_refilling')
        obj.laps = CellConfig.from_dict(data.get("laps", {}), 'laps')
        obj.leader = CellConfig.from_dict(data.get("leader", {}), 'leader')
        obj.near_finish = CellConfig.from_dict(data.get("near_finish", {}), 'near_finish')
        obj.near_start = CellConfig.from_dict(data.get("near_start", {}), 'near_start')
        obj.pit_time = CellConfig.from_dict(data.get("pit_time", {}), 'pit_time')
        obj.player = CellConfig.from_dict(data.get("player", {}), 'player')
        obj.refill = CellConfig.from_dict(data.get("refill", {}), 'refill')
        obj.prediction = data.get("prediction", obj.prediction)
        obj.leader_laptime_pace_margin = data.get("leader_laptime_pace_margin", obj.leader_laptime_pace_margin)
        obj.leader_laptime_pace_samples = data.get("leader_laptime_pace_samples", obj.leader_laptime_pace_samples)
        obj.near_finish_range = data.get("near_finish_range", obj.near_finish_range)
        obj.near_start_range = data.get("near_start_range", obj.near_start_range)
        obj.number_of_extra_laps = data.get("number_of_extra_laps", obj.number_of_extra_laps)
        obj.number_of_prediction = data.get("number_of_prediction", obj.number_of_prediction)
        return obj
