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
"""TinyUI-specific composition consumed by the shared tinyqt host layer."""

# pyright: reportAttributeAccessIssue=false, reportCallIssue=false, reportGeneralTypeIssues=false

from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter
from typing import Any, cast

from PySide6.QtCore import QObject

from tinycore.logging import LogInspector, get_logger
from tinycore.paths import AppPaths
from tinycore.runtime.boot import HostAssembly, HostOverlayBuild, HostStateMonitorBuild
from tinycore.runtime.core_runtime import CoreRuntime
from tinycore.runtime.plugins.participants import PluginParticipant
from tinycore.runtime.plugins.provider_activity import ProviderActivity
from tinycore.services import HostServices, RuntimeServices
from tinyui_schema import SettingsSpec

from tinyqt.optional_features import (
    build_devtools_runtime_attachment,
    get_devtools_monitor_info,
)
from tinyqt.launch import QtLaunchSpec
from tinyqt.manifests import (
    TinyQtAppManifest,
    TinyQtPanelManifest,
    TinyQtShellManifest,
    validate_manifest,
)
from tinyqt.registration import RegistrationMap, SingletonRegistration

from tinyqt.app_identity import APP_NAME, VERSION
from tinyqt.app_info import AppInfo
from tinyqt.theme import Theme
from tinyui.ui_bindings import (
    bind_statusbar_plugin_switching,
    bind_tab_plugin_switching,
    bind_theme_settings,
)
from tinyui.viewmodels.core_viewmodel import CoreViewModel
from tinyui.viewmodels.settings_panel_viewmodel import SettingsPanelViewModel
from tinyui.viewmodels.statusbar_viewmodel import StatusBarViewModel
from tinyui.viewmodels.tab_viewmodel import TabViewModel

_log = get_logger(__name__)

ThemeClass = cast(type[Theme], Theme)
CoreViewModelClass = cast(type[CoreViewModel], CoreViewModel)
StatusBarViewModelClass = cast(type[StatusBarViewModel], StatusBarViewModel)
SettingsPanelViewModelClass = cast(type[SettingsPanelViewModel], SettingsPanelViewModel)
TabViewModelClass = cast(type[TabViewModel], TabViewModel)
AppInfoClass = cast(type[AppInfo], AppInfo)


def _status_items(core) -> list[str]:
    items = ["Overlay"]
    provider_names = sorted(provider.name for provider in core.runtime.plugin_facts.providers())
    if provider_names:
        items.insert(0, provider_names[0].replace("_", " "))
    if build_tinyui_manifest(core.paths).optional_features:
        items.append("F12 DevTools")
    return items


def _active_plugin_label(core, index: int) -> str:
    participants = core.runtime.plugin_runtime.registered_participants
    if 0 <= index < len(participants):
        participant = participants[index]
        return participant.manifest.display_name or participant.name
    return ""


def _apply_status_shell_state(core, statusbar_vm: StatusBarViewModel, window: QObject) -> None:
    def _update_active_label() -> None:
        index = int(statusbar_vm.property("activePluginIndex"))
        window.setProperty("statusActiveLabel", _active_plugin_label(core, index))

    window.setProperty("statusItems", _status_items(core))
    _update_active_label()

    active_changed = cast(Any, getattr(statusbar_vm, "activePluginIndexChanged", None))
    if active_changed is not None:
        active_changed.connect(_update_active_label)


def build_tinyui_manifest(paths: AppPaths) -> TinyQtAppManifest:
    """Build the hosted TinyUI manifest from the rebuilt launch-first shell."""
    if paths.source_root is None:
        raise RuntimeError("TinyUI manifest requires a source_root in source runtime mode")
    return validate_manifest(
        TinyQtAppManifest(
            app_id="tinyui.main",
            title=APP_NAME,
            root_qml=paths.source_root / "qml_app" / "TinyUiMain.qml",
            shell=TinyQtShellManifest(
                use_window_menu_bar=True,
                use_tab_bar=True,
                use_status_bar=True,
                lazy_panel_loading=True,
            ),
            panels=(
                TinyQtPanelManifest(
                    panel_id="widgets",
                    label="Widgets",
                    qml_type="WidgetTab",
                    package="TinyUI",
                ),
            ),
            optional_features=("devtools_ui",),
        )
    )


@dataclass
class _EmptyOverlayModel:
    contexts: list[object] = field(default_factory=list)


@dataclass
class _NullOverlay:
    """Launch-first placeholder overlay while the widget runtime is rebuilt."""

    model: _EmptyOverlayModel = field(default_factory=_EmptyOverlayModel)
    state: object = None
    extra_context: RegistrationMap = field(default_factory=dict)
    update_interval_ms: int = 100

    def update_participants(self) -> tuple[tuple[str, str], ...]:
        return ()

    def start(self) -> None:
        return None

    def stop(self) -> None:
        return None


def _log_startup_phase(log, phase: str, start: float) -> None:
    log.startup_phase(phase, (perf_counter() - start) * 1000)


def register_tinyui_host_settings(host: HostServices) -> None:
    """Register TinyUI-owned host settings on the shared host persistence surface."""

    def _register(spec: SettingsSpec) -> None:
        host.persistence.register_host_setting("TinyUI", spec)

    _register(
        SettingsSpec(
            key="theme",
            label="Theme",
            type="enum",
            default="dark",
            options=["dark", "light"],
            description="Application color theme",
            section="Application",
        )
    )
    _register(
        SettingsSpec(
            key="startup_plugin",
            label="Startup plugin",
            type="string",
            default="demo",
            description="Plugin to activate on startup",
            section="Application",
        )
    )
    _register(
        SettingsSpec(
            key="remember_position",
            label="Remember position",
            type="bool",
            default=True,
            description="Restore window position on startup",
            section="Window",
        )
    )
    _register(
        SettingsSpec(
            key="remember_size",
            label="Remember size",
            type="bool",
            default=True,
            description="Restore window size on startup",
            section="Window",
        )
    )


def _build_registrations(
    *,
    theme: Theme,
    core_vm: CoreViewModel,
    statusbar_vm: StatusBarViewModel,
    settings_vm: SettingsPanelViewModel,
    tab_vm: TabViewModel,
    devtools_ui,
) -> list[SingletonRegistration]:
    devtools_path = "" if devtools_ui is None else devtools_ui.qml_url
    return [
        SingletonRegistration(ThemeClass, "TinyUI", "Theme", theme),
        SingletonRegistration(CoreViewModelClass, "TinyUI", "CoreViewModel", core_vm),
        SingletonRegistration(
            StatusBarViewModelClass, "TinyUI", "StatusBarViewModel", statusbar_vm
        ),
        SingletonRegistration(
            SettingsPanelViewModelClass,
            "TinyUI",
            "SettingsPanelViewModel",
            settings_vm,
        ),
        SingletonRegistration(TabViewModelClass, "TinyUI", "TabViewModel", tab_vm),
        SingletonRegistration(
            AppInfoClass,
            "TinyUI",
            "AppInfo",
            AppInfo(
                app_name=APP_NAME,
                devtools_available=devtools_ui is not None,
                devtools_path=devtools_path,
            ),
        ),
    ]


def build_tinyui_launch_spec(core) -> QtLaunchSpec:
    """Build the TinyUI-specific launch spec consumed by the shared tinyqt host."""
    log = get_logger(__name__)
    phase_start = perf_counter()
    app_manifest = build_tinyui_manifest(core.paths)

    log_inspector = LogInspector()
    theme = ThemeClass()
    statusbar_vm = StatusBarViewModelClass()
    settings_vm = SettingsPanelViewModelClass()
    core_vm = CoreViewModelClass(core)
    tab_vm = TabViewModelClass()

    for participant in core.runtime.plugin_runtime.registered_participants:
        label = participant.manifest.display_name or participant.name
        tab_vm.register(participant.name, label)

    bind_tab_plugin_switching(core, tab_vm)
    bind_statusbar_plugin_switching(core, statusbar_vm)
    bind_theme_settings(core, core_vm, settings_vm, theme)

    _log_startup_phase(log, "viewmodels", phase_start)
    return QtLaunchSpec(
        app_name=APP_NAME,
        version=VERSION,
        qml_path=app_manifest.root_qml or (core.paths.source_root / "qml_app" / "TinyUiMain.qml"),
        app_manifest=app_manifest,
        theme=theme,
        log_inspector=log_inspector,
        build_registrations=lambda _devtools_ui: [],
        restore_state_scope="TinyUI",
        module="TinyUI",
        on_host_ready=lambda host: _apply_status_shell_state(core, statusbar_vm, host.window),
        on_before_exec=lambda _host: core.units.set_state("ui.main", "running")
        if core.units.get("ui.main") is not None
        else None,
    )


@dataclass(frozen=True)
class TinyUiHostAssembly(HostAssembly):
    """Host-owned assembly for TinyUI surfaces through the shared tinyqt seam."""

    @property
    def devtools_monitor_interval_ms(self) -> int | None:
        return get_devtools_monitor_info().refresh_interval_ms

    def register_host(self, host: HostServices) -> None:
        register_tinyui_host_settings(host)

    def startup_participant(self, host: HostServices) -> str | None:
        return host.persistence.get_setting("TinyUI", "startup_plugin") or None

    def build_overlay(
        self,
        paths: AppPaths,
        host: HostServices,
        runtime: RuntimeServices,
        provider_activity: ProviderActivity,
        participants: list[PluginParticipant],
    ) -> HostOverlayBuild:
        return HostOverlayBuild(overlay=_NullOverlay(), widget_sources=[])

    def build_state_monitor(
        self,
        runtime: CoreRuntime,
        overlay: object,
        widget_sources: list[tuple[str, str, str]],
    ) -> HostStateMonitorBuild:
        return build_devtools_runtime_attachment(runtime, overlay)


TINYUI_HOST_ASSEMBLY = TinyUiHostAssembly()
