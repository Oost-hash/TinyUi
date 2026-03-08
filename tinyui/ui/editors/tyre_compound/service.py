# editors/tyre_compound/service.py

from dataclasses import dataclass
from typing import Any, Dict, Optional

from ..core.editor_service import EditorService
from ..core.validation import (
    RequiredFieldValidator,
    UniqueKeyValidator,
    ValidationChain,
)

# Default heatmap constant - avoids import of backend at module level
HEATMAP_DEFAULT_TYRE = "default"


@dataclass
class TyreCompound:
    """Domain model for tyre compound configuration."""

    name: str
    symbol: str = "?"
    heatmap: str = HEATMAP_DEFAULT_TYRE

    def to_dict(self) -> dict:
        return {"symbol": self.symbol, "heatmap": self.heatmap}

    @classmethod
    def from_dict(cls, name: str, data: dict) -> "TyreCompound":
        return cls(
            name=name,
            symbol=data.get("symbol", "?"),
            heatmap=data.get("heatmap", HEATMAP_DEFAULT_TYRE),
        )


class TyreCompoundService(EditorService[TyreCompound]):
    """
    Service for tyre compound editor.
    Reuses same pattern as BrakeService.
    """

    def __init__(self, store_adapter: Any):
        super().__init__(store_adapter, schema=None)
        self._cfg_attr = "compounds"
        self._cfg_type = None  # Lazy loaded

    @property
    def cfg_type(self):
        if self._cfg_type is None:
            from tinyui.backend.constants import ConfigType
            self._cfg_type = ConfigType.COMPOUNDS
        return self._cfg_type

    def load(self) -> Dict[str, TyreCompound]:
        self.load_started.emit()

        try:
            raw_data = self._store.load(self._cfg_attr)
            models = {
                name: TyreCompound.from_dict(name, data)
                for name, data in raw_data.items()
            }
            self._cache = models
            self.load_completed.emit(models)
            return models

        except Exception as e:
            self.load_failed.emit(str(e))
            return {}

    def save(self, data: Dict[str, TyreCompound]) -> bool:
        self.save_started.emit()

        is_valid, error = self.validate(data)
        if not is_valid:
            self.save_failed.emit(error)
            return False

        raw_data = {name: compound.to_dict() for name, compound in data.items()}

        try:
            self._store.save(self._cfg_attr, self.cfg_type, raw_data)
            self.save_completed.emit()
            return True

        except Exception as e:
            self.save_failed.emit(str(e))
            return False

    def validate(self, data: Dict[str, TyreCompound]) -> tuple[bool, Optional[str]]:
        """Validate using reusable validators."""
        for name, compound in data.items():
            chain = (
                ValidationChain()
                .add(RequiredFieldValidator({"symbol": "Symbol", "heatmap": "Heatmap"}))
                .add(UniqueKeyValidator(lambda: list(data.keys()), "compound_name"))
            )

            context = chain.validate(compound.to_dict(), name)
            if not context.is_valid:
                return False, f"{name}: {context.errors[0].message}"

        return True, None

    def import_from_api(self) -> Dict[str, TyreCompound]:
        """Import compounds from game API."""
        compounds = {}

        try:
            from tinyui.backend.controls import api
            from tinyui.backend.data import set_predefined_compound_symbol

            veh_total = api.read.vehicle.total_vehicles()

            for idx in range(veh_total):
                class_name = api.read.vehicle.class_name(idx)

                # Front and rear compounds
                for position, get_name in [
                    ("front", api.read.tyre.compound_name_front),
                    ("rear", api.read.tyre.compound_name_rear),
                ]:
                    compound_name = f"{class_name} - {get_name(idx)}"

                    if compound_name not in compounds:
                        compounds[compound_name] = TyreCompound(
                            name=compound_name,
                            symbol=set_predefined_compound_symbol(compound_name),
                            heatmap=HEATMAP_DEFAULT_TYRE,
                        )

        except Exception as e:
            self.load_failed.emit(f"API import failed: {str(e)}")

        return compounds

    def create_compound(self, name: str) -> TyreCompound:
        """Create new compound with defaults."""
        return TyreCompound(name=name)
