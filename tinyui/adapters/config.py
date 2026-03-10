"""Configuration adapter - bridges TinyUi and TinyPedal settings."""

from typing import Any, Dict, Optional
from unittest.mock import MagicMock


class Config:
    """Clean interface to TinyPedal configuration."""

    def __init__(self):
        self._real: Any = None  # Het cfg OBJECT, niet de module
        self._overrides: Dict[str, Any] = {}

    def _get_real(self) -> Any:
        """Get or import the real cfg OBJECT (not module)."""
        if self._real is None:
            try:
                # BELANGRIJK: importeer het cfg OBJECT, niet de setting module
                from tinypedal_repo.tinypedal.setting import cfg as real_cfg_obj

                self._real = real_cfg_obj
            except ImportError:
                self._real = MagicMock()
        return self._real

    def inject(self, real_cfg: Any) -> None:
        """Inject real cfg object."""
        self._real = real_cfg

    # --- Attribute access ---

    def __getattr__(self, name: str) -> Any:
        """Check overrides first, then delegate to real cfg OBJECT."""
        if name in self._overrides:
            return self._overrides[name]
        return getattr(self._get_real(), name)

    def __setattr__(self, name: str, value: Any) -> None:
        """Set on real cfg unless internal."""
        if name in ("_real", "_overrides"):
            super().__setattr__(name, value)
        else:
            setattr(self._get_real(), name, value)

    # --- Test helpers ---

    def override(self, name: str, value: Any) -> None:
        """Temporarily override a config value."""
        self._overrides[name] = value

    def reset(self) -> None:
        """Clear all overrides."""
        self._overrides.clear()

    def is_mocked(self) -> bool:
        """Check if using mock fallback."""
        return isinstance(self._get_real(), MagicMock)
