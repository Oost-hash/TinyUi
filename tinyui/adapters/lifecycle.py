"""TinyPedal core lifecycle manager."""

import logging
import signal
import sys
import time
from typing import Optional

from .config import Config
from .lazy import LazyModule

logger = logging.getLogger("TinyUi")


class Lifecycle:
    """Manages TinyPedal lifecycle: API, modules, widgets, overlays, hotkeys."""

    def __init__(self, config: Optional[Config] = None):
        self.cfg = config or Config()

        # Lazy-loaded controllers
        self.api = LazyModule("tinypedal_repo.tinypedal.api_control", "api")
        self.modules = LazyModule("tinypedal_repo.tinypedal.module_control", "mctrl")
        self.widgets = LazyModule("tinypedal_repo.tinypedal.module_control", "wctrl")
        self.overlay = LazyModule("tinypedal_repo.tinypedal.overlay_control", "octrl")
        self.hotkey = LazyModule("tinypedal_repo.tinypedal.hotkey_control", "kctrl")
        self.updater = LazyModule("tinypedal_repo.tinypedal.update", "update_checker")

        self._running = False

    # --- Lifecycle ---

    def start(self) -> "Lifecycle":
        """Full startup sequence. Call AFTER QApplication exists."""
        logger.info("Starting TinyPedal...")

        self._setup_signals()
        self._load_preset()
        self._start_api()
        self._start_modules()
        self._start_widgets()
        self._finalize()

        self._running = True
        logger.info("Tiny Pedal started successfully")
        return self

    def close(self) -> None:
        """Graceful shutdown."""
        if not self._running:
            return

        logger.info("Shutting down TinyPedal...")

        self.hotkey.disable()
        self.widgets.close()
        self.modules.close()
        self.overlay.disable()

        # Stop API
        self.api.stop()

        del self.api
        del self.modules
        del self.widgets
        del self.overlay
        del self.hotkey
        del self.updater

        import gc

        gc.collect()

        self._running = False
        logger.info("Tinypedal stopped")

    def reload(self, reload_preset: bool = False) -> None:
        """Reload configuration and restart modules."""
        logger.info("Reloading TinyPedal...")

        self._wait_for_save()

        self.hotkey.disable()
        self.widgets.close()
        self.modules.close()
        self.overlay.disable()

        if reload_preset:
            self.cfg.load_user()
            self.cfg.save(0)

        self.api.restart()
        self.overlay.enable()
        self.modules.start()
        self.widgets.start()
        self.hotkey.enable()

        logger.info("Tiny Pedal reloaded")

    # --- Internal helpers ---

    def _setup_signals(self) -> None:
        """Setup graceful shutdown on Ctrl+C."""

        def handler(signum, frame):
            logger.info("Interrupted, shutting down...")
            self.close()
            sys.exit(0)

        signal.signal(signal.SIGINT, handler)

    def _load_preset(self) -> None:
        """Load first available preset."""
        from tinypedal_repo.tinypedal.const_file import FileExt

        first_preset = f"{self.cfg.preset_files()[0]}{FileExt.JSON}"
        self.cfg.set_next_to_load(first_preset)
        self.cfg.load_user()
        self.cfg.save()

        logger.info(f"Loaded preset: {self.cfg.filename.setting}")

    def _start_api(self) -> None:
        """Start telemetry API."""
        self.api.connect()
        self.api.start()
        logger.info(f"API started: {self.api.alias}")

    def _start_modules(self) -> None:
        """Start all modules."""
        self.modules.start()
        active = self.modules.number_active
        total = self.modules.number_total
        logger.info(f"Modules: {active}/{total} active")

    def _start_widgets(self) -> None:
        """Start all widgets."""
        self.widgets.start()
        active = self.widgets.number_active
        total = self.widgets.number_total
        logger.info(f"Widgets: {active}/{total} active")

    def _finalize(self) -> None:
        """Enable controls and check for updates."""
        self.overlay.enable()
        self.hotkey.enable()

        if self.cfg.application.get("check_for_updates_on_startup"):
            self.updater.check(False)

    def _wait_for_save(self) -> None:
        """Block until config save completes."""
        if self.cfg.is_saving:
            self.cfg.save(next_task=True)
            while self.cfg.is_saving:
                time.sleep(0.01)
