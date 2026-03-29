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
"""Manifest declaration for the hosted TinyDevTools surface."""

from __future__ import annotations

from tinycore.paths import AppPaths

from tinyqt.manifests import (
    TinyQtAppManifest,
    TinyQtPanelManifest,
    TinyQtShellManifest,
    validate_manifest,
)


def build_tinydevtools_manifest(paths: AppPaths) -> TinyQtAppManifest:
    """Build the hosted TinyDevTools manifest from the current source layout."""
    return validate_manifest(
        TinyQtAppManifest(
            app_id="tinydevtools.window",
            title="Dev Tools",
            root_qml=paths.qml_dir("tinydevtools") / "DevToolsRoot.qml",
            shell=TinyQtShellManifest(
                use_window_menu_bar=True,
                use_tab_bar=True,
                use_status_bar=False,
                lazy_panel_loading=True,
            ),
            panels=(
                TinyQtPanelManifest(
                    panel_id="state",
                    label="State",
                    qml_type="DevToolsStateTab",
                    package="TinyDevTools",
                ),
                TinyQtPanelManifest(
                    panel_id="runtime",
                    label="Runtime",
                    qml_type="DevToolsRuntimeTab",
                    package="TinyDevTools",
                ),
                TinyQtPanelManifest(
                    panel_id="console",
                    label="Console",
                    qml_type="ConsolePane",
                    package="TinyDevTools",
                ),
            ),
            required_singletons=(
                "Theme",
                "LogViewModel",
                "LogSettingsViewModel",
                "RuntimeViewModel",
                "StateMonitorViewModel",
            ),
        )
    )
