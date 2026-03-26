#  TinyUI
"""LMU session-domain providers."""

from __future__ import annotations

from .reader import Lap, Session, State, Timing, WeatherNode

from .shared import decode_bytes
from .source import LMUSource


class LMUStateProvider(State):
    def __init__(self, source: LMUSource) -> None:
        self._source = source

    def active(self) -> bool:
        phase = int(self._source.info.data.scoring.scoringInfo.mGamePhase)
        return bool(
            self._source.info.data.telemetry.playerHasVehicle
            and phase not in (0, 7, 8, 9)
        )

    def paused(self) -> bool:
        return self._source.info.data.scoring.scoringInfo.mGamePhase == 9

    def version(self) -> str:
        return str(self._source.info.data.generic.gameVersion)


class LMULapProvider(Lap):
    def __init__(self, source: LMUSource) -> None:
        self._source = source

    def _scor(self, index: int | None):
        idx = self._source.info.data.telemetry.playerVehicleIdx if index is None else index
        return self._source.info.data.scoring.vehScoringInfo[idx]

    def current_lap(self, index: int | None = None) -> int:
        return int(self._scor(index).mLapNumber)

    def completed_laps(self, index: int | None = None) -> int:
        return int(self._scor(index).mTotalLaps)

    def track_length(self) -> float:
        return float(self._source.info.data.scoring.scoringInfo.mLapDist)

    def lap_distance(self, index: int | None = None) -> float:
        return float(self._scor(index).mLapDist)

    def lap_progress(self, index: int | None = None) -> float:
        length = self.track_length()
        return self.lap_distance(index) / length if length > 0 else 0.0

    def current_sector(self, index: int | None = None) -> int:
        raw = int(self._scor(index).mSector)
        return {0: 2, 1: 0, 2: 1}.get(raw, 0)


class LMUSessionProvider(Session):
    def __init__(self, source: LMUSource) -> None:
        self._source = source

    def _si(self):
        return self._source.info.data.scoring.scoringInfo

    def track_name(self) -> str:
        return decode_bytes(self._si().mTrackName)

    def session_time_elapsed(self) -> float:
        return float(self._si().mCurrentET)

    def session_time_left(self) -> float:
        return float(self._si().mEndET - self._si().mCurrentET)

    def session_kind(self) -> int:
        raw = int(self._si().mSession)
        if raw == 0:
            return 0
        if 1 <= raw <= 4:
            return 1
        if 5 <= raw <= 8:
            return 2
        if raw == 9:
            return 3
        return 4

    def is_race_session(self) -> bool:
        return self.session_kind() == 4

    def track_temperature(self) -> float:
        return float(self._si().mTrackTemp)

    def ambient_temperature(self) -> float:
        return float(self._si().mAmbientTemp)

    def raininess(self) -> float:
        return float(self._si().mRaining)

    def weather_forecast(self) -> tuple[WeatherNode, ...]:
        return ()


class LMUTimingProvider(Timing):
    def __init__(self, source: LMUSource) -> None:
        self._source = source

    def _scor(self, index: int | None):
        idx = self._source.info.data.telemetry.playerVehicleIdx if index is None else index
        return self._source.info.data.scoring.vehScoringInfo[idx]

    def current_laptime(self, index: int | None = None) -> float:
        return float(self._scor(index).mTimeIntoLap)

    def last_laptime(self, index: int | None = None) -> float:
        return float(self._scor(index).mLastLapTime)

    def best_laptime(self, index: int | None = None) -> float:
        return float(self._scor(index).mBestLapTime)

    def current_sector1(self, index: int | None = None) -> float:
        return float(self._scor(index).mCurSector1)

    def current_sector2(self, index: int | None = None) -> float:
        return float(self._scor(index).mCurSector2)

    def last_sector1(self, index: int | None = None) -> float:
        return float(self._scor(index).mLastSector1)

    def last_sector2(self, index: int | None = None) -> float:
        return float(self._scor(index).mLastSector2)

    def best_sector1(self, index: int | None = None) -> float:
        return float(self._scor(index).mBestSector1)

    def best_sector2(self, index: int | None = None) -> float:
        return float(self._scor(index).mBestSector2)

    def gap_to_leader(self, index: int | None = None) -> float:
        return float(self._scor(index).mTimeBehindLeader)
