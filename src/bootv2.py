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

from runtimeV2.startup import get_runtime_v2_result, startup_runtime_v2
from ui_api.qt import create_application, create_engine
from ui_api.runtime_host import start_runtime_host


def main() -> int:
    """Start runtime V2 and hand it to ui_api."""

    app = create_application()
    engine = create_engine()
    startup_result = startup_runtime_v2()
    if not startup_result.ok:
        print(startup_result.error_message, file=sys.stderr)
        return 1

    runtime_result = get_runtime_v2_result()
    if runtime_result is None:
        print("Runtime V2 startup did not expose a runtime result", file=sys.stderr)
        return 1

    _host_result, ui_api_result = start_runtime_host(
        app=app,
        engine=engine,
        runtime=runtime_result.runtime,
    )
    if not ui_api_result.ok:
        print(ui_api_result.error_message, file=sys.stderr)
        return 1

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
