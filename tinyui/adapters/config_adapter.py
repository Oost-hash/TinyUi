# tinyui/backend/config_adapter.py
from typing import Any, Dict
from unittest.mock import MagicMock


class ConfigAdapter:
    """Adapter voor TinyPedal's setting.cfg met overschrijfbaarheid."""

    def __init__(self, real_cfg=None):
        # Echte cfg (uit tinypedal.setting) – wordt later geïnjecteerd
        self._real = real_cfg
        # Woordenboek voor tijdelijke overschrijvingen (handig in tests)
        self._overrides: Dict[str, Any] = {}

    @property
    def real(self):
        """Geef de echte cfg terug, of een lege mock als die nog niet is gezet."""
        if self._real is None:
            # Fallback voor wanneer de adapter zonder echte cfg wordt gebruikt
            return MagicMock()
        return self._real

    def __getattr__(self, name: str) -> Any:
        """Geef attribuut uit overrides of van de echte cfg."""
        if name in self._overrides:
            return self._overrides[name]
        return getattr(self.real, name)

    def __setattr__(self, name: str, value: Any) -> None:
        """Schrijf naar echte cfg, behalve voor interne attributen."""
        if name in ("_real", "_overrides"):
            super().__setattr__(name, value)
        else:
            setattr(self.real, name, value)

    # ----- Test-hulpmiddelen -----
    def override(self, name: str, value: Any) -> None:
        """Overschrijf een attribuut voor de duur van de test."""
        self._overrides[name] = value

    def reset_overrides(self) -> None:
        """Wis alle overschrijvingen."""
        self._overrides.clear()

    def inject_real(self, real_cfg) -> None:
        """Zet de echte cfg (wordt aangeroepen bij initialisatie van de backend)."""
        self._real = real_cfg
