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

"""QML source abstraction for filesystem vs QRC paths."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QUrl


@dataclass(frozen=True)
class QmlSource:
    """Reference to a QML file that works in both dev and build mode.
    
    In development: uses filesystem paths for hot-reload.
    In frozen builds: uses qrc:/ URLs for embedded resources.
    """

    _filesystem_path: Path | None = None
    _qrc_path: str | None = None

    @classmethod
    def filesystem(cls, path: Path) -> QmlSource:
        """Create a QML source that loads from the filesystem."""
        return cls(_filesystem_path=path)

    @classmethod
    def qrc(cls, path: str) -> QmlSource:
        """Create a QML source that loads from Qt resources (qrc:/)."""
        # Ensure path starts with /
        if not path.startswith("/"):
            path = "/" + path
        return cls(_qrc_path=path)

    @classmethod
    def dual(cls, filesystem_path: Path, qrc_path: str) -> QmlSource:
        """Create a QML source that works in both modes.
        
        In dev: loads from filesystem for hot-reload.
        In frozen: loads from QRC for embedded resources.
        """
        if not qrc_path.startswith("/"):
            qrc_path = "/" + qrc_path
        return cls(_filesystem_path=filesystem_path, _qrc_path=qrc_path)

    def to_url(self, frozen: bool | None = None) -> QUrl:
        """Return a QUrl suitable for loading by QQmlComponent.
        
        Args:
            frozen: If True, use QRC paths (build mode). 
                   If False, use filesystem paths (dev mode).
                   If None, auto-detect based on sys.frozen.
        """
        if frozen is None:
            frozen = getattr(sys, "frozen", False)
        
        if frozen:
            if self._qrc_path is None:
                raise RuntimeError(f"No QRC path registered for {self}")
            return QUrl(f"qrc:{self._qrc_path}")
        
        if self._filesystem_path is None:
            raise RuntimeError(f"No filesystem path registered for {self}")
        return QUrl.fromLocalFile(str(self._filesystem_path))

    def __str__(self) -> str:
        if self._qrc_path:
            return f"qrc:{self._qrc_path}"
        if self._filesystem_path:
            return str(self._filesystem_path)
        return "<empty QmlSource>"
