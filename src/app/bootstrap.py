#  TinyUI
"""Application bootstrap helpers for the composition root."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tinycore.app import App, create_app
from tinycore.inspect import RuntimeInspector
from tinycore.log import get_logger
from tinycore.plugin.lifecycle import PluginLifecycleManager
from tinycore.plugin.manifest import PluginManifest, scan_plugins
from tinycore.plugin.subprocess_host import SubprocessPlugin
from tinyui import TinyUIPlugin
from tinyui.devtools import StateMonitorViewModel
from tinywidgets.fields import read_field
from tinywidgets.overlay import WidgetOverlay
from tinywidgets.spec import load_widgets_toml

_log = get_logger(__name__)


@dataclass(frozen=True)
class BootRuntime:
    """Bootstrapped runtime objects handed off to the UI launcher."""

    core: App
    lifecycle: PluginLifecycleManager
    overlay: WidgetOverlay
    state_monitor: StateMonitorViewModel
    extra_context: dict[str, object]


def discover_manifests(plugins_dir: Path) -> list[PluginManifest]:
    """Scan the plugin directory and return runtime manifests."""
    return scan_plugins(plugins_dir)


def bootstrap_runtime(config_dir: Path, manifests: list[PluginManifest]) -> BootRuntime:
    """Build and wire the runtime before the Qt event loop starts."""
    consumer_manifests = [m for m in manifests if m.is_consumer]
    provider_manifests = [m for m in manifests if m.is_provider]

    core = create_app(
        config_dir,
        *[
            (SubprocessPlugin(m.consumer_runtime_spec()), m.requires)
            for m in consumer_manifests
        ],
    )
    TinyUIPlugin().register(core)
    _load_host_state(core)
    core.start(plugins=False)

    lifecycle = _activate_plugins(core)
    _register_providers(core, provider_manifests)
    _bind_consumers(core, consumer_manifests)

    overlay, widget_sources = _build_overlay(core, config_dir, consumer_manifests)
    state_monitor = _build_state_monitor(core, overlay, widget_sources)

    return BootRuntime(
        core=core,
        lifecycle=lifecycle,
        overlay=overlay,
        state_monitor=state_monitor,
        extra_context={
            "widgetModel": overlay.model,
            "stateMonitorViewModel": state_monitor,
        },
    )


def _load_host_state(core: App) -> None:
    core.host.loaders.load_all(core.host.config)
    core.host.plugin_settings.load_persisted()
    core.host.host_settings.load_persisted()


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
        bindings = core.runtime.session.bind_consumer(manifest.name, manifest.requires)
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
    config_dir: Path,
    manifests: list[PluginManifest],
) -> tuple[WidgetOverlay, list[tuple[str, str, str]]]:
    overlay = WidgetOverlay(core.runtime.session, config_dir=config_dir)
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
) -> StateMonitorViewModel:
    runtime_inspector = RuntimeInspector()
    runtime_inspector.setup(core.runtime.session, widget_sources, read_field)
    state_monitor = StateMonitorViewModel(runtime_inspector)
    for context in overlay.model.contexts:
        state_monitor.register_object(f"Widget: {context.title}", context)
    return state_monitor
