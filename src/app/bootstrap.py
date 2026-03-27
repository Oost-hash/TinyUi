#  TinyUI
"""Application bootstrap helpers for the composition root."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Protocol

from tinycore.app import App, create_app
from tinycore.logging import get_logger
from tinycore.paths import AppPaths
from tinycore.plugin.lifecycle import PluginLifecycleManager
from tinycore.plugin.manifest import PluginManifest, scan_plugins
from tinycore.plugin.subprocess_host import SubprocessPlugin
from tinyui.plugin import TinyUIPlugin
from tinywidgets.overlay import WidgetOverlay
from tinywidgets.spec import load_widgets_toml

_log = get_logger(__name__)


class _StateMonitorLike(Protocol):
    def start(self) -> None: ...
    def shutdown(self) -> None: ...


def _ms(start: float) -> float:
    return round((perf_counter() - start) * 1000, 1)


def _log_startup_phase(phase: str, start: float) -> None:
    _log.startup_phase(phase, _ms(start))


@dataclass(frozen=True)
class BootRuntime:
    """Bootstrapped runtime objects handed off to the UI launcher."""

    core: App
    lifecycle: PluginLifecycleManager
    overlay: WidgetOverlay
    state_monitor: _StateMonitorLike | None
    extra_context: dict[str, object]


def discover_manifests(plugins_dir) -> list[PluginManifest]:
    """Scan the plugin directory and return runtime manifests."""
    return scan_plugins(plugins_dir)


def bootstrap_runtime(paths: AppPaths, manifests: list[PluginManifest]) -> BootRuntime:
    """Build and wire the runtime before the Qt event loop starts."""
    total_start = perf_counter()
    consumer_manifests = [m for m in manifests if m.is_consumer]
    provider_manifests = [m for m in manifests if m.is_provider]

    phase_start = perf_counter()
    core = create_app(
        paths,
        *[
            (SubprocessPlugin(m.consumer_runtime_spec()), m.requires)
            for m in consumer_manifests
        ],
    )
    _log_startup_phase("create_app", phase_start)

    phase_start = perf_counter()
    TinyUIPlugin().register(core)
    _load_host_state(core)
    core.start(plugins=False)
    _log_startup_phase("host_state", phase_start)

    phase_start = perf_counter()
    lifecycle = _activate_plugins(core)
    _log_startup_phase("activate_plugins", phase_start)

    phase_start = perf_counter()
    _register_providers(core, provider_manifests)
    _log_startup_phase("register_providers", phase_start)

    phase_start = perf_counter()
    _bind_consumers(core, consumer_manifests)
    _log_startup_phase("bind_consumers", phase_start)

    phase_start = perf_counter()
    overlay, widget_sources = _build_overlay(core, consumer_manifests)
    _log_startup_phase("build_overlay", phase_start)

    phase_start = perf_counter()
    state_monitor, devtools_context = _build_state_monitor(core, overlay, widget_sources)
    _log_startup_phase("build_state_monitor", phase_start)
    _log.startup_phase("bootstrap_runtime_total", _ms(total_start))

    extra_context = {
        "widgetModel": overlay.model,
        "widgetOverlayState": overlay.state,
    }
    extra_context.update(devtools_context)

    return BootRuntime(
        core=core,
        lifecycle=lifecycle,
        overlay=overlay,
        state_monitor=state_monitor,
        extra_context=extra_context,
    )


def _load_host_state(core: App) -> None:
    core.host.persistence.loaders.load_all(core.host.persistence.config)
    core.host.persistence.plugin_settings.load_persisted()
    core.host.persistence.host_settings.load_persisted()


def _activate_plugins(core: App) -> PluginLifecycleManager:
    lifecycle = PluginLifecycleManager(core.runtime.plugins, grace_seconds=30.0)
    plugin_names = [p.name for p in core.runtime.plugins.plugins]
    if plugin_names:
        lifecycle.activate(plugin_names[0])
    return lifecycle


def _register_providers(core: App, manifests: list[PluginManifest]) -> None:
    for manifest in manifests:
        if manifest.provider is None:
            continue
        provider = manifest.provider.create()
        provider.open()
        core.runtime.session.register_provider(manifest.name, provider, manifest.exports)
        _log.info(
            "provider registered  plugin=%s  type=%s  exports=%s",
            manifest.name,
            type(provider).__name__,
            ", ".join(manifest.exports) if manifest.exports else "-",
        )


def _bind_consumers(core: App, manifests: list[PluginManifest]) -> None:
    for manifest in manifests:
        bindings = core.runtime.session.bind_consumer(
            manifest.name,
            manifest.requires,
            manifest.provider_requests,
        )
        if bindings.missing:
            _log.warning(
                "consumer requires missing  plugin=%s  missing=%s",
                manifest.name,
                ", ".join(bindings.missing),
            )
            continue
        if bindings.resolved:
            _log.info(
                "consumer bound  plugin=%s  requires=%s",
                manifest.name,
                ", ".join(
                    f"{capability}->{binding.provider_name}"
                    for capability, binding in bindings.resolved.items()
                ),
            )


def _build_overlay(
    core: App,
    manifests: list[PluginManifest],
) -> tuple[WidgetOverlay, list[tuple[str, str, str]]]:
    overlay = WidgetOverlay(core.runtime.session, paths=core.paths)
    widget_sources: list[tuple[str, str, str]] = []
    for manifest in manifests:
        widgets_path = manifest.widgets_path()
        if widgets_path is None or not widgets_path.exists():
            continue
        specs = load_widgets_toml(widgets_path)
        overlay.load(specs, plugin_name=manifest.name)
        widget_sources.extend((manifest.name, spec.capability, spec.field) for spec in specs if spec.field)
    return overlay, widget_sources


def _build_state_monitor(
    core: App,
    overlay: WidgetOverlay,
    widget_sources: list[tuple[str, str, str]],
) -> tuple[_StateMonitorLike | None, dict[str, object]]:
    try:
        from tinydevtools.host import attach_runtime
    except ImportError:
        _log.info("devtools runtime attachment unavailable")
        return None, {}

    attachment = attach_runtime(core, overlay, widget_sources)
    return attachment.state_monitor, attachment.extra_context
