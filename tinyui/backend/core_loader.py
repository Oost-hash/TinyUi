#
#  TinyUi - Core Loader for TinyPedal
#  Copyright (C) 2026 Oost-hash
#

"""TinyPedal Core Loader - Laadt alleen de core, geen UI"""

import logging
import signal
import sys
import time

from tinyui.backend.constants import FileExt
from tinyui.backend.settings import cfg

logger = logging.getLogger("TinyUi")


class TinyPedalCore:
    """Beheert TinyPedal core lifecycle (api, modules, widgets)"""

    def __init__(self):
        self.api = None
        self.mctrl = None
        self.wctrl = None
        self.octrl = None
        self.kctrl = None
        self.update_checker = None
        self._running = False

    def _init_globals(self):
        """Initialize alle TinyPedal globals - pas aangeroepen in start()"""
        from tinyui.backend.controls import api, loader, mctrl, octrl, wctrl
        from tinyui.backend.misc import update_checker

        self.api = api
        self.mctrl = mctrl
        self.wctrl = wctrl
        self.octrl = octrl
        self.kctrl = loader.kctrl
        self.update_checker = update_checker

        logger.info("TinyPedal core globals geinitialiseerd")

    def _setup_signal_handler(self):
        """Setup SIGINT handler voor graceful shutdown"""

        def int_signal_handler(sign, frame):
            logger.info("Keyboard interrupt ontvangen, sluiten...")
            self.close()
            sys.exit()

        signal.signal(signal.SIGINT, int_signal_handler)

    def _load_preset(self):
        """Laad eerste preset"""
        cfg.set_next_to_load(f"{cfg.preset_files()[0]}{FileExt.JSON}")
        cfg.load_user()
        cfg.save()
        logger.info(f"Preset geladen: {cfg.filename.setting}")

    def _start_api(self):
        """Start telemetry API"""
        self.api.connect()
        self.api.start()
        logger.info(f"API gestart: {self.api.alias}")

    def _start_modules(self):
        """Start alle modules"""
        self.mctrl.start()
        logger.info(
            f"Modules gestart: {self.mctrl.number_active}/{self.mctrl.number_total}"
        )

    def _start_widgets(self):
        """Start alle widgets"""
        self.wctrl.start()
        logger.info(
            f"Widgets gestart: {self.wctrl.number_active}/{self.wctrl.number_total}"
        )

    def _finalize(self):
        """Finalize startup - enable controls"""
        self.octrl.enable()
        self.kctrl.enable()

        if cfg.application["check_for_updates_on_startup"]:
            self.update_checker.check(False)

        self._running = True
        logger.info("TinyPedal core volledig gestart")

    def start(self):
        """Volledige startup sequence - roep dit aan NA dat QApplication bestaat"""
        logger.info("STARTING TINYPEDAL CORE...")

        self._setup_signal_handler()
        self._init_globals()  # Pas hier de imports!
        self._load_preset()
        self._start_api()
        self._start_modules()
        self._start_widgets()
        self._finalize()

        return self

    def close(self):
        """Graceful shutdown"""
        if not self._running:
            return

        logger.info("CLOSING TINYPEDAL CORE...")

        if self.kctrl:
            self.kctrl.disable()
        if self.wctrl:
            self.wctrl.close()
        if self.mctrl:
            self.mctrl.close()
        if self.octrl:
            self.octrl.disable()
        if self.api:
            self.api.stop()

        self._running = False
        logger.info("TinyPedal core gestopt")

    def reload(self, reload_preset: bool = False):
        """Reload preset/modules/widgets"""
        logger.info("RELOADING TINYPEDAL CORE...")

        if cfg.is_saving:
            cfg.save(next_task=True)
            while cfg.is_saving:
                time.sleep(0.01)

        self.kctrl.disable()
        self.wctrl.close()
        self.mctrl.close()
        self.octrl.disable()

        if reload_preset:
            cfg.load_user()
            cfg.save(0)

        self.api.restart()
        self.octrl.enable()
        self.mctrl.start()
        self.wctrl.start()
        self.kctrl.enable()

        logger.info("TinyPedal core herladen")


# Singleton instance
core = TinyPedalCore()
