#  TinyUI
#  Copyright (C) 2026 Oost-hash
#
#  This file is part of TinyUI.
#
#  TinyUI is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  TinyUI is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  TinyUI builds on TinyPedal by s-victor (https://github.com/s-victor/TinyPedal),
#  licensed under GPLv3.

"""ConfigResolver — bepaalt alle persistence paden."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any


def _os_config_dir(app_name: str) -> Path:
    """Return the OS-level user config directory for the given app name."""
    if sys.platform == "win32":
        base = os.getenv("APPDATA", str(Path.home()))
        return Path(base) / app_name
    # Linux / macOS — XDG_CONFIG_HOME or ~/.config
    xdg = os.getenv("XDG_CONFIG_HOME", str(Path.home() / ".config"))
    return Path(xdg) / app_name


class ConfigResolver:
    """Bepaalt alle persistence paden. Niet afhankelijk van AppPaths.
    
    Deze class bepaalt zelfstandig waar configuratie, cache en logs worden
    opgeslagen. Dit is altijd op OS-niveau (bijv. %APPDATA% op Windows),
    nooit naast de executable.
    """

    APP_NAME = "TinyUI"

    def __init__(self) -> None:
        self._base_dir = _os_config_dir(self.APP_NAME)
        self._bootstrap = self._load_bootstrap()

    def _load_bootstrap(self) -> dict[str, Any]:
        """Read bootstrap.toml if present.
        
        Bootstrap is always in the OS-standard location, even if the
        user has configured a custom config_dir.
        """
        bootstrap_path = self._base_dir / "bootstrap.toml"
        if bootstrap_path.exists():
            try:
                # tomllib is standard in Python 3.11+, reads binary
                import tomllib
                with open(bootstrap_path, "rb") as f:
                    return tomllib.load(f)
            except Exception:
                # Corrupt bootstrap, ignore
                pass
        return {}

    @property
    def base_dir(self) -> Path:
        """Basis persistence directory (altijd OS-standaard).
        
        Dit is de root van alle TinyUI data op dit systeem.
        """
        return self._base_dir

    @property
    def config_root(self) -> Path:
        """Root van alle configuratie (kan overridden zijn via bootstrap)."""
        custom = self._bootstrap.get("config_dir", "")
        if custom:
            return Path(custom)
        return self._base_dir / "config"

    @property
    def cache_dir(self) -> Path:
        """Cache directory (kan gewist worden zonder dataverlies)."""
        return self._base_dir / "cache"

    @property
    def logs_dir(self) -> Path:
        """Logs directory."""
        return self._base_dir / "logs"

    def config_set_dir(self, set_id: str) -> Path:
        """Directory voor een specifieke config set."""
        return self.config_root / set_id

    def namespace_dir(self, set_id: str, namespace: str) -> Path:
        """Directory voor een namespace binnen een config set."""
        return self.config_set_dir(set_id) / namespace

    def write_bootstrap(
        self,
        config_dir: Path | None = None,
        config_set: str | None = None,
    ) -> None:
        """Schrijf bootstrap.toml bij gebruikerswijziging.
        
        Wordt altijd geschreven naar de OS-standaard locatie,
        nooit naar een custom locatie.
        """
        bootstrap: dict[str, Any] = {}
        if config_dir is not None:
            bootstrap["config_dir"] = str(config_dir)
        if config_set is not None:
            bootstrap["config_set"] = config_set

        if not bootstrap:
            return  # Nothing to write

        self._base_dir.mkdir(parents=True, exist_ok=True)
        bootstrap_path = self._base_dir / "bootstrap.toml"

        import toml
        with open(bootstrap_path, "w", encoding="utf-8") as f:
            toml.dump(bootstrap, f)
