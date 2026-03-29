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
from typing import Any, Protocol, cast

from PySide6.QtCore import QObject

from tinycore.logging import LogInspector, get_logger
from tinycore.paths import AppPaths
from tinyruntime.boot import HostAssembly, HostOverlayBuild, HostStateMonitorBuild
from tinyruntime.core_runtime import CoreRuntime
from tinyruntime.plugins.participants import PluginParticipant
from tinyruntime.plugins.provider_activity import ProviderActivity
from tinycore.services import HostServices, RuntimeServices
from tinyqt_settings_schema import SettingsSpec

from tinyqt.optional_features import (
    build_widget_overlay,
    build_devtools_runtime_attachment,
    get_devtools_monitor_info,
)
from tinyqt.launch import QtLaunchSpec
from tinyqt.manifests import TinyQtAppManifest
from tinyqt.registration import RegistrationMap, SingletonRegistration

from tinyqt.app_identity import APP_NAME, VERSION
from tinyqt.app_info import AppInfo
from tinyqt.app_manifest_loader import load_tinyqt_app_manifests
from tinyqt.theme import Theme
from tinyqt_main.viewmodels.core_viewmodel import CoreViewModel
from tinyqt_settings.viewmodels.settings_panel_viewmodel import SettingsPanelViewModel
from tinyqt_main.viewmodels.statusbar_viewmodel import StatusBarViewModel
from tinyqt_main.viewmodels.tab_viewmodel import TabViewModel

_log = get_logger(__name__)

ThemeClass = cast(type[Theme], Theme)
CoreViewModelClass = cast(type[CoreViewModel], CoreViewModel)
StatusBarViewModelClass = cast(type[StatusBarViewModel], StatusBarViewModel)
SettingsPanelViewModelClass = cast(type[SettingsPanelViewModel], SettingsPanelViewModel)
TabViewModelClass = cast(type[TabViewModel], TabViewModel)
AppInfoClass = cast(type[AppInfo], AppInfo)


class _ThemeLike(Protocol):
    def load(self, name: str, /) -> None: ...


def _maybe_int(value: object) -> int | None:
    return int(value) if isinstance(value, int | float | str) else None


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


def _plugin_names(core) -> list[str]:
    return [
        participant.name
        for participant in core.runtime.plugin_runtime.registered_participants
    ]


def _apply_status_shell_state(core, statusbar_vm: StatusBarViewModel, window: QObject) -> None:
    def _update_active_label() -> None:
        index = int(statusbar_vm.property("activePluginIndex"))
        window.setProperty("statusActiveLabel", _active_plugin_label(core, index))

    window.setProperty("statusItems", _status_items(core))
    window.setProperty("pluginNames", _plugin_names(core))
    window.setProperty("statusBarController", statusbar_vm)
    _update_active_label()

    active_changed = cast(Any, getattr(statusbar_vm, "activePluginIndexChanged", None))
    if active_changed is not None:
        active_changed.connect(_update_active_label)


def _apply_widget_editor_state(core, window: QObject) -> None:
    model = getattr(core.overlay, "model", None)
    contexts = getattr(model, "contexts", None)
    contexts_changed = getattr(model, "contextsChanged", None)

    def _update_items() -> None:
        current_contexts = getattr(model, "contexts", None)
        if callable(current_contexts):
            window.setProperty("widgetEditorItems", current_contexts())
            return
        if current_contexts is not None:
            window.setProperty("widgetEditorItems", current_contexts)

    if callable(contexts):
        _update_items()
    elif contexts is not None:
        _update_items()

    if contexts_changed is not None:
        contexts_changed.connect(_update_items)


def _apply_tinyui_host_state(core, statusbar_vm: StatusBarViewModel, window: QObject) -> None:
    _apply_status_shell_state(core, statusbar_vm, window)
    _apply_widget_editor_state(core, window)


def _bind_statusbar_plugin_switching(core, statusbar_view_model: object) -> None:
    if not isinstance(statusbar_view_model, QObject):
        return

    plugin_names = [
        participant.name for participant in core.runtime.plugin_runtime.registered_participants
    ]
    if not plugin_names:
        return

    def _on_plugin_switch() -> None:
        index = _maybe_int(statusbar_view_model.property("activePluginIndex"))
        if index is None:
            return
        if 0 <= index < len(plugin_names):
            core.activation.activate(plugin_names[index])

    active_changed = cast(Any, getattr(statusbar_view_model, "activePluginIndexChanged", None))
    if active_changed is not None:
        active_changed.connect(_on_plugin_switch)


def _bind_tab_plugin_switching(core, tab_view_model: object) -> None:
    if not isinstance(tab_view_model, QObject):
        return

    plugin_names = [
        participant.name for participant in core.runtime.plugin_runtime.registered_participants
    ]
    if not plugin_names:
        return

    def _on_tab_switch() -> None:
        index = _maybe_int(tab_view_model.property("currentIndex"))
        if index is None:
            return
        if 0 <= index < len(plugin_names):
            core.activation.activate(plugin_names[index])

    current_index_changed = cast(Any, getattr(tab_view_model, "currentIndexChanged", None))
    if current_index_changed is not None:
        current_index_changed.connect(_on_tab_switch)


def _bind_theme_settings(
    core,
    core_view_model: object,
    settings_panel_view_model: object,
    theme: _ThemeLike,
) -> None:
    if not isinstance(core_view_model, QObject) or not isinstance(
        settings_panel_view_model, QObject
    ):
        return

    def _apply_tinyui_settings() -> None:
        theme_name = core.host.persistence.get_setting("TinyUI", "theme")
        if theme_name:
            theme.load(str(theme_name))

    def _save_setting(plugin_name: str) -> None:
        core.host.persistence.save_settings(plugin_name)

    settings_changed = cast(Any, getattr(core_view_model, "settingsChanged", None))
    setting_value_changed = cast(
        Any, getattr(core_view_model, "settingValueChanged", None)
    )
    setting_change_requested = cast(
        Any, getattr(settings_panel_view_model, "settingChangeRequested", None)
    )
    set_setting_value = cast(Any, getattr(core_view_model, "setSettingValue", None))

    if settings_changed is not None:
        settings_changed.connect(_apply_tinyui_settings)
    if setting_value_changed is not None:
        setting_value_changed.connect(_save_setting)
    if setting_change_requested is not None and callable(set_setting_value):
        setting_change_requested.connect(set_setting_value)

    _apply_tinyui_settings()


def build_tinyui_manifest(paths: AppPaths) -> TinyQtAppManifest:
    """Build the hosted TinyUI main-window manifest from tinyqt_main/manifest.toml."""
    manifest_path = paths.source_root / "tinyqt_main" / "manifest.toml" if paths.source_root else None
    if manifest_path is None:
        raise RuntimeError("TinyUI manifest requires a source_root in source runtime mode")
    manifests = load_tinyqt_app_manifests(manifest_path, paths=paths)
    for manifest in manifests:
        if manifest.app_id == "tinyui.main":
            return manifest
    raise RuntimeError(f"Missing TinyUI app manifest 'tinyui.main' in {manifest_path}")


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

    _bind_tab_plugin_switching(core, tab_vm)
    _bind_statusbar_plugin_switching(core, statusbar_vm)
    _bind_theme_settings(core, core_vm, settings_vm, theme)

    _log_startup_phase(log, "viewmodels", phase_start)

    def _on_host_ready(host) -> None:
        from tinyqt.host import create_settings_controller

        _apply_tinyui_host_state(core, statusbar_vm, host.window)
        settings_controller = create_settings_controller(
            app=None,
            core=core,
            theme=theme,
            build_registrations=lambda _devtools_ui: _build_registrations(
                theme=theme,
                core_vm=core_vm,
                statusbar_vm=statusbar_vm,
                settings_vm=settings_vm,
                tab_vm=tab_vm,
                devtools_ui=None,
            ),
        )
        host.window.setProperty("settingsController", settings_controller)
        host.window.setProperty("settingsAvailable", True)

    return QtLaunchSpec(
        app_name=APP_NAME,
        version=VERSION,
        qml_path=app_manifest.root_qml or (core.paths.source_root / "tinyqt_native_qml" / "TinyUiMain.qml"),
        app_manifest=app_manifest,
        theme=theme,
        log_inspector=log_inspector,
        build_registrations=lambda _devtools_ui: [],
        restore_state_scope="TinyUI",
        module="TinyUI",
        on_host_ready=_on_host_ready,
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
        return build_widget_overlay(
            paths=paths,
            host=host,
            runtime=runtime,
            provider_activity=provider_activity,
            participants=participants,
        )

    def build_state_monitor(
        self,
        runtime: CoreRuntime,
        overlay: object,
        widget_sources: list[tuple[str, str, str]],
    ) -> HostStateMonitorBuild:
        return build_devtools_runtime_attachment(runtime, overlay)


TINYUI_HOST_ASSEMBLY = TinyUiHostAssembly()

