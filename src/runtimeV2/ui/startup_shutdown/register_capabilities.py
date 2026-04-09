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

"""Capability registration for runtime V2 UI."""

from __future__ import annotations

from dataclasses import dataclass

from runtimeV2.ui.capabilities.chrome_model_read import UIChromeModelRead
from runtimeV2.ui.capabilities.panel_state_read import PanelStateRead
from runtimeV2.ui.capabilities.panel_state_write import PanelStateWrite
from runtimeV2.ui.capabilities.render_status_read import RenderStatusRead
from runtimeV2.ui.capabilities.window_actions_write import WindowActionsWrite
from runtimeV2.ui.capabilities.window_records_read import WindowRecordsRead
from runtimeV2.ui.contracts import UIChromeModel, UIRenderStatus, UIWindowRecord
from runtimeV2.ui.panel_state import UIPanelStateStore


@dataclass(frozen=True)
class UICapabilities:
    """Capabilities exposed by the UI domain."""

    window_records_read: WindowRecordsRead
    window_actions_write: WindowActionsWrite
    panel_state_read: PanelStateRead
    panel_state_write: PanelStateWrite
    render_status_read: RenderStatusRead
    chrome_model_read: UIChromeModelRead


def register_ui_capabilities(
    *,
    records: list[UIWindowRecord],
    main_window_id: str,
    panel_state: UIPanelStateStore,
    render_status: UIRenderStatus,
    chrome_model: UIChromeModel,
) -> UICapabilities:
    """Create UI domain capabilities."""

    window_records_read = WindowRecordsRead(records)
    return UICapabilities(
        window_records_read=window_records_read,
        window_actions_write=WindowActionsWrite(window_records_read, main_window_id),
        panel_state_read=PanelStateRead(panel_state),
        panel_state_write=PanelStateWrite(panel_state),
        render_status_read=RenderStatusRead(render_status),
        chrome_model_read=UIChromeModelRead(chrome_model),
    )
