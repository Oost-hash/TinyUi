# editors/tyre_compound/viewmodel.py

from typing import Any, List

from ..core.base_viewmodel import BaseViewModel
from .service import TyreCompound, TyreCompoundService


class TyreCompoundEditorVM(BaseViewModel[TyreCompound]):
    """
    ViewModel for tyre compound editor.
    Notice how similar this is to BrakeEditorVM - that's the point!
    """

    def __init__(self, service: TyreCompoundService):
        super().__init__(service)
        self._service: TyreCompoundService = service

    def import_from_api(self):
        """Import compounds from game API."""
        new_compounds = self._service.import_from_api()

        for name, compound in new_compounds.items():
            if self._model and name not in self._model:
                self.add_item(name, compound.to_dict())

    def add_new_compound(self, base_name: str = "New Compound") -> str:
        """Create and add new compound with unique name."""
        counter = 1
        name = f"{base_name} {counter}"

        while self._model and name in self._model:
            counter += 1
            name = f"{base_name} {counter}"

        compound = self._service.create_compound(name)
        self.add_item(name, compound.to_dict())
        return name

    def update_compound_field(self, compound_name: str, field: str, value: Any):
        """Update a single field."""
        # Special handling for symbol - max 1 char
        if field == "symbol":
            value = str(value)[:1] if value else "?"

        self.update_value(compound_name, field, value)

    def _validate(self) -> bool:
        """Validate all compounds."""
        if not self._model:
            return True

        compounds = {}
        for name, data in self._model.to_dict().items():
            if isinstance(data, TyreCompound):
                compounds[name] = data
            else:
                compounds[name] = TyreCompound.from_dict(name, data)

        is_valid, error = self._service.validate(compounds)

        if not is_valid:
            self.error_occurred.emit(error)

        return is_valid

    def get_row_data(self, key: str, item: Any) -> List[Any]:
        """
        Convert compound to table row.
        Returns: [name, symbol, heatmap]
        """
        if isinstance(item, dict):
            return [key, item.get("symbol", "?"), item.get("heatmap", "default")]
        return [key, "?", ""]

    @property
    def heatmap_options(self) -> List[str]:
        """Get available heatmap names."""
        from tinyui.backend.settings import cfg

        return (
            list(cfg.user.heatmap.keys())
            if hasattr(cfg.user, "heatmap")
            else ["default"]
        )

    @property
    def symbol_options(self) -> List[str]:
        """Common compound symbols."""
        return ["S", "M", "H", "W", "I", "C", "?"]
