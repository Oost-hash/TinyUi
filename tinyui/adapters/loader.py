"""Loader adapter - replaces tinypedal.loader to break circular imports."""

import logging
import os
import sys
import time

from .config import Config
from .lazy import LazyModule

logger = logging.getLogger("TinyUi")


class Loader:
    """Drop-in replacement for tinypedal.loader.

    This is injected into sys.modules["tinypedal_repo.tinypedal.loader"]
    to intercept calls from legacy TinyPedal code.
    """

    def __init__(self, config: Config):
        self.cfg = config

        # Lazy-loaded dependencies
        self._api = LazyModule("tinypedal_repo.tinypedal.api_control", "api")
        self._modules = LazyModule("tinypedal_repo.tinypedal.module_control", "mctrl")
        self._widgets = LazyModule("tinypedal_repo.tinypedal.module_control", "wctrl")
        self._overlay = LazyModule("tinypedal_repo.tinypedal.overlay_control", "octrl")
        self._hotkey = LazyModule("tinypedal_repo.tinypedal.hotkey_control", "kctrl")

    # --- Public API matching original loader.py ---

    def start(self) -> None:
        """Called by original TinyPedal startup. We handle it differently."""
        logger.info("Loader adapter start called")

        from tinypedal_repo.tinypedal.const_file import FileExt

        # Load preset
        preset = f"{self.cfg.preset_files()[0]}{FileExt.JSON}"
        self.cfg.set_next_to_load(preset)
        self.cfg.load_user()
        self.cfg.save()

        # Start
        self._api.connect()
        self._api.start()
        self._modules.start()
        self._widgets.start()
        # Note: UI finalization is handled by main, not here

    def close(self) -> None:
        """Close everything."""
        logger.info("Loader adapter close called")
        self._unload()
        self._api.stop()

    def restart(self) -> None:
        """Hard restart of entire application."""
        logger.info("Loader adapter restart called")
        self.close()

        self._wait_for_save()

        # Flag and exec
        os.environ["TINYPEDAL_RESTART"] = "TRUE"
        exe = sys.executable
        args = sys.argv if "tinypedal.exe" not in exe else [exe] + sys.argv[1:]
        os.execl(exe, *args)

    def reload(self, reload_preset: bool = False) -> None:
        """Soft reload of preset/modules."""
        logger.info(f"Loader adapter reload (preset={reload_preset})")

        self._wait_for_save()
        self._unload()

        if reload_preset:
            self.cfg.load_user()
            self.cfg.save(0)

        self._api.restart()
        self._load()

    def load_modules(self) -> None:
        """Load and enable all modules."""
        self._overlay.enable()
        self._modules.start()
        self._widgets.start()
        self._hotkey.enable()

    def unload_modules(self) -> None:
        """Unload and disable all modules."""
        self._unload()

    # --- Internal helpers ---

    def _load(self) -> None:
        """Enable all controls."""
        self._overlay.enable()
        self._modules.start()
        self._widgets.start()
        self._hotkey.enable()

    def _unload(self) -> None:
        """Disable all controls."""
        self._hotkey.disable()
        self._widgets.close()
        self._modules.close()
        self._overlay.disable()

    def _wait_for_save(self) -> None:
        """Block until config is saved."""
        if self.cfg.is_saving:
            self.cfg.save(next_task=True)
            while self.cfg.is_saving:
                time.sleep(0.01)

    # --- Signal handler compatibility ---

    def int_signal_handler(self, signum, frame) -> None:
        """SIGINT handler."""
        self.close()
        sys.exit(0)
