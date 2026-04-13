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

"""Runtime V2 boot entry point."""

from __future__ import annotations

import sys

# In frozen builds, import compiled QRC resources for embedded assets
if getattr(sys, "frozen", False):
    import resources_rc  # noqa: F401

from runtimeV2.runtime import RuntimeV2
from runtimeV2.schemas.startup import StartupResult
from runtimeV2.startup import startup_runtime_v2
from shared_runtime_host.startup_shutdown.startup import startup_shared_runtime_host
from ui_api.qt import create_application, create_engine
from ui_api.startup_logging import install_startup_diagnostics, log_startup_step, startup_log_path

if sys.platform == "win32":
    from ui_api.windowing import win_window  # eager import: registers QML singletons before engine


def main() -> int:
    """Start runtime V2 and hand it to ui_api."""

    log_path = install_startup_diagnostics()
    log_startup_step(f"bootv2 main start; log_path={log_path}")
    app = create_application()
    engine = create_engine()
    log_startup_step("starting runtime V2")

    def _start_host_bridge(runtime: RuntimeV2) -> StartupResult:
        _host_result, host_result = startup_shared_runtime_host(
            app=app,
            engine=engine,
            runtime=runtime,
        )
        return host_result

    startup_result = startup_runtime_v2(host_bridge_startup=_start_host_bridge)
    if not startup_result.ok:
        log_startup_step(
            f"runtime V2 startup failed: {startup_result.error_message}",
            level=40,
        )
        print(startup_result.error_message, file=sys.stderr)
        return 1

    log_startup_step(f"entering QApplication event loop; log_path={startup_log_path()}")
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
