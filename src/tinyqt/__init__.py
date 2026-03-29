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
"""tinyqt — shared Qt runtime and render-host layer."""

from .manifests import TinyQtAppManifest, TinyQtPanelManifest, TinyQtShellManifest


def create_application(*args, **kwargs):
    from .app import create_application as _create_application

    return _create_application(*args, **kwargs)


def boot_and_launch_qml_app(*args, **kwargs):
    from .bootstrap import boot_and_launch_qml_app as _boot_and_launch_qml_app

    return _boot_and_launch_qml_app(*args, **kwargs)


def create_engine(*args, **kwargs):
    from .engine import create_engine as _create_engine

    return _create_engine(*args, **kwargs)


def launch_qml_app(*args, **kwargs):
    from .launch import launch_qml_app as _launch_qml_app

    return _launch_qml_app(*args, **kwargs)


__all__ = [
    "boot_and_launch_qml_app",
    "create_application",
    "create_engine",
    "launch_qml_app",
    "TinyQtAppManifest",
    "TinyQtPanelManifest",
    "TinyQtShellManifest",
]
